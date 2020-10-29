import socket
import sys
import re
import constants

# Create a TCP/IP socket
import reverse_ping

response_message = '{}'.format(constants.OP_CODE_RESPONSE)

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
                op_code = message[0:2]
                body = message[3:len(message)]
                print(body)
                if op_code == constants.OP_CODE_REVERSE:
                    print("Server performing ping against client")
                    parsed_message = body.split(',')
                    count = int(parsed_message[0])
                    reverse_ping.ping(connection, count, client_address)
                if op_code == constants.OP_CODE_DIRECT and not body:
                    connection.sendall(response_message.encode('utf-8'))
                if op_code == constants.OP_CODE_DIRECT and body:
                    connection.sendall(response_message.encode('utf-8'))
            else:
                print('No data received from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
