import socket

def make_socket(server_address):
    # Create a TCP/IP socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    my_socket.connect(server_address)
    return my_socket