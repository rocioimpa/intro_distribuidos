import socket
import sys
import re

# Create a TCP/IP socket
import reverse_ping

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

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
            data = connection.recv(10000)

            print('Received {!r}'.format(data))
            if data:
                message = data.decode('utf-8')
                if 'reverse' in message:
                    print("Server performing ping against client")
                    parsed_message = message.split()
                    count = int(parsed_message[1])
                    reverse_ping.ping(connection, count, client_address)
                else:
                    connection.sendall(data)

            else:
                print('No data received from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
