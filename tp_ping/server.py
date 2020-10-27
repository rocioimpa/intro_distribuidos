import socket
import sys
import re

# Create a TCP/IP socket
import reverse_ping
import proxy_ping

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 9800)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

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
            data = connection.recv(10000)

            print('received {!r}'.format(data))
            if data:
                message = data.decode('utf-8')

                if 'reverse' in message:
                    print("server performing ping against client")
                    count = int(re.findall(r'[0-9]+', message)[0] )
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
