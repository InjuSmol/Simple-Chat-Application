
import socket
import sys
import threading
import argparse

exit_event = threading.Event()

def send_join_message(sock, username):
    join_message = f"join {username}"
    sock.sendall(join_message.encode())


# Function to send messages to the server
def send_message(sock, username):
    try:
        while True:
            message = input().strip()
            if message == "quit":
                sock.sendall(b'quit')
                break
            if message.startswith("list"):
                message = message + ' ' +  f"{username}"
            sock.sendall(message.encode())
    except Exception as e:
        print("Error:", e)
        sock.close()


# Function to receive messages from the server
def receive_message(sock):
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            if message.startswith("err_unknown_message"):
                print(f"disconnected: server received an unknown command")
                sock.close()
                sys.exit()
            else:
                print(message)
    except Exception as e:
        print("Error:", e)
        sock.close()

def main():
    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(description="Chat client")

    # Add argument for server port number
    parser.add_argument("-p", "--port", type=int, help="Port number of the server")

    # Add argument for username
    parser.add_argument("-u", "--username", help="Username for the client")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Check if port argument is provided
    if not args.port:
        print("Please specify the server port number using the -p option.")
        exit()

    # Check if username argument is provided
    if not args.username:
        print("Please specify the username using the -u option.")
        exit()

    # Get the server port number and username
    server_port_num = args.port
    username = args.username
    server_address = ('localhost', server_port_num)  # Server's IP address and port
    try:
        # Create a UDP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.connect(server_address)

        # Get username from user
        #username = input("Enter your username: ").strip()
        send_join_message(client_socket, username)

        # Thread to send messages to the server
        send_thread = threading.Thread(target=send_message, args=(client_socket, username))
        send_thread.start()

        # Thread to receive messages from the server
        receive_thread = threading.Thread(target=receive_message, args=(client_socket,))
        receive_thread.start()
        
        # Wait for the threads to finish
        send_thread.join()
        receive_thread.join()


    except Exception as e:
        print("Error:", e)
        sys.exit()

if __name__ == "__main__":
    main()
