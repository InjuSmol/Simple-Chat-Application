import socket
import sys
import traceback
import argparse

MAX_NUM_CLIENTS = 10  # Maximum number of clients the server can handle concurrently

# Dictionary to store connected clients
connected_clients = {}

# Function to handle incoming messages from clients
def handle_messages(server_socket):
    try:
        while True:
            data, client_address = server_socket.recvfrom(1024)
            data_str = data.decode()
            if data_str.startswith("join"):
                handle_join_message(server_socket, data_str, client_address)
            elif data_str.startswith("msg"):
                handle_chat_message(server_socket, data_str, client_address)
            elif data_str.startswith("list"):
                parts = data_str.split()
                #print(data_str)
                #print(parts[0])
                username = parts[1]
                handle_list_command(server_socket, client_address, username)
            elif data_str.startswith("help"):
                handle_help_command(server_socket, client_address)
            elif data_str.startswith("quit"):
                handle_quit_command(server_socket, client_address)
            else:
                # Handle unknown message
                #parts = data_str.split()
                #username = parts[1]
                error_message = f"err_unknown_message"
                server_socket.sendto(error_message.encode(), client_address)
                #print(f"{username} sent unknown command")
                #del connected_clients[username]
                #server_socket.close()
    except Exception as e:
        print("Error:", e)
        traceback.print_exc(limit=1)
        sys.exit()

# Function to handle join message
def handle_join_message(server_socket, message, client_address):
    global connected_clients

    # Parse the username from the message
    parts = message.split()
    if len(parts) < 2:
        print("Error: Invalid 'join' message format.")
        return
    username = parts[1]

    # Case 1: Server full
    if len(connected_clients) >= MAX_NUM_CLIENTS:
        error_message = "err_server_full"
        server_socket.sendto(error_message.encode(), client_address)
        print("Disconnected: Server full")
        return

    # Case 2: Username already taken
    if username in connected_clients:
        error_message = f"err_username_unavailable {username}"
        server_socket.sendto(error_message.encode(), client_address)
        print(f"Disconnected: Username '{username}' not available")
        return

    # Case 3: Allow user to join
    connected_clients[username] = client_address
    print(f"join: {username}")

# Function to handle chat message
def handle_chat_message(server_socket, message, sender_address):
    global connected_clients
    parts = message.split()
    try:
        num_recipients = int(parts[1])
        recipients = parts[2:2+num_recipients]
        message_text = ' '.join(parts[2+num_recipients:])
    except ValueError:
        print("Error: Invalid message format.")
        traceback.print_exc(limit=1)
        return
    
    sender_username = None
    for username, address in connected_clients.items():
        if address == sender_address:
            sender_username = username
            break

    if sender_username:
        for recipient_username in recipients:
            if recipient_username in connected_clients:
                recipient_address = connected_clients[recipient_username]
                forward_message = f"msg {sender_username}: {message_text}"
                server_socket.sendto(forward_message.encode(), recipient_address)
            else:
                error_message = f"msg: {sender_username} to non-existent user {recipient_username}"
                server_socket.sendto(error_message.encode(), sender_address)
                
                
# Function to handle list command
def handle_list_command(server_socket, client_address, username):
    
    global connected_clients
    user_list = "list: " + " ".join(sorted(connected_clients.keys()))
    print(f"request_users_list: {username}")
    server_socket.sendto(user_list.encode(), client_address)

# Function to handle help command
def handle_help_command(server_socket, client_address):
    help_message = """
    1) Message:
    Input: msg <number_of_users> <username1> <username2> … <message>
    
    2) Available Users:
    Input: list
    
    3) Help:
    Input: help
    
    4) Quit:
    Input: quit
    """
    server_socket.sendto(help_message.encode(), client_address)

# Function to handle quit command
def handle_quit_command(server_socket, client_address):
    global connected_clients
    for username, address in connected_clients.items():
        if address == client_address:
            print(f"disconnected: {username}")
            del connected_clients[username]
            break
    server_socket.sendto("quitting".encode(), client_address)

def main():
    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(description="Chat server")

    # Add argument for port number
    parser.add_argument("-p", "--port", type=int, help="Port number for the server")
    args = parser.parse_args()

    # Check if port argument is provided
    if not args.port:
        print("Please specify the port number using the -p option.")
        exit()

    # Get the port number
    port_num = args.port
    server_address = ('localhost', port_num)  # Server's IP address and port
    try:
        # Create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(server_address)

        print("Server is running...")

        # Handle incoming messages from clients
        handle_messages(server_socket)
            
    except Exception as e:
        print("Error:", e)
        traceback.print_exc(limit=1)
        sys.exit()

if __name__ == "__main__":
    main()
