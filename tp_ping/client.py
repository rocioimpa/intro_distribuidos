import socket

#TODO: take value from user input
server_address = ('localhost', 10000)

def make_socket():
    # Create a TCP/IP socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    print('connecting to {} port {}'.format(*server_address))
    my_socket.connect(server_address)
    return my_socket