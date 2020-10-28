import socket
import sys
import re

# Create a TCP/IP socket
import reverse_ping
import proxy_ping
from server_config import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

used_port = server_port_a


def start_server(server_port):
    server_address = ('localhost', server_port)
    sock.bind(server_address)
    print('server started up on {} port {}'.format(*server_address))


# Bind the socket to the port
try:
    start_server(server_port_a)
except socket.error:
    used_port = server_port_b
    start_server(server_port_b)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(used_port)

            print('received {!r}'.format(data))
            if data:
                message = data.decode('utf-8')

                if 'reverse' in message:
                    print("server performing ping against client")
                    count = int(re.findall(r'[0-9]+', message)[0])
                    reverse_ping.ping(connection, count, client_address)

                if 'proxy' in message:
                    parsed_message = message.split(',')

                    count = int(parsed_message[1])
                    destination = parsed_message[2]

                    print("server performing ping against {}".format(destination))

                    proxy_ping.ping(connection, count, destination)

                else:
                    connection.sendall(data)

            else:
                print('no data received from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
