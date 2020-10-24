import select
import socket
import sys

# Create a UDP socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
message = b'This is the message.  It will be repeated.'

# TODO: read from input
count = 2

"""to configure"""
timeout = 1

try:
    for i in range(0, count):
        # Send data
        print('sending {!r}'.format(message))
        send_time = time.time()
        sent = sock.sendto(message, server_address)

        inputready, outputready, exceptready = select.select([sock], [], [], timeout)
        if inputready == []:
            """compute as packet loss"""
            print("packet loss")

        # Receive response
        data, server = sock.recvfrom(4096)
        receive_time = time.time()
        print('received {!r} in {:.3f} ms'.format(data, receive_time - send_time))

finally:
    print('closing socket')
    sock.close()
