import socket
import sys

import constants

# Create a TCP/IP socket
import reverse_ping
import proxy_ping

response_message = '{}'.format(constants.OP_CODE_RESPONSE)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

used_port = constants.DEFAULT_PORT_A


def start_server(server_port):
    server_address = ('localhost', server_port)
    sock.bind(server_address)
    print('Starting up on {} port {}'.format(*server_address))


# Bind the socket to the port
try:
    used_port = int(sys.argv[1])
except IndexError:
    used_port = constants.DEFAULT_PORT_A

try:
    start_server(used_port)
except socket.error:
    if used_port is not None:
        print("Port {} is in use!".format(used_port))
    used_port = constants.DEFAULT_PORT_B
    start_server(constants.DEFAULT_PORT_B)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('Waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('Connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(used_port)

            print('Received {!r}'.format(data))
            if data:
                message = data.decode('utf-8')
                op_code = message[0:2]
                body = message[3:len(message)]

                if op_code == constants.OP_CODE_REVERSE and body:
                    print("Server performing ping against client")
                    parsed_message = body.split(',')
                    count = int(parsed_message[0])
                    reverse_ping.ping(connection, count, client_address)
                if op_code == constants.OP_CODE_DIRECT and not body:
                    connection.sendall(response_message.encode('utf-8'))
                if op_code == constants.OP_CODE_DIRECT and body:
                    connection.sendall(response_message.encode('utf-8'))
                if op_code == constants.OP_CODE_PROXY and body:
                    parsed_message = message.split(',')
                    count = int(parsed_message[1])
                    destination = parsed_message[2].split(':')
                    print("Server performing ping against {} on {}".format(destination[0], destination[1]))
                    proxy_ping.ping(connection, count, destination[0], int(destination[1]))
            else:
                print('No data received from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
