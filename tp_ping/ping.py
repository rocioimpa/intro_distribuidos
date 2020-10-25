import select
import socket
import sys
import time


class Ping:

    def __init__(self, server_address=('localhost', 10000), ping_type='ping'):
        self.server_address = server_address
        self.type = ping_type
        self.timeout = 1000
        self.sequence_number = 0
        self.max_wait = 1000  # ms

    def ping(self, count=1):
        my_socket = self.make_socket()

        for i in range(0, count):
            send_time = self.send(my_socket)
            receive_time, packet = self.receive(my_socket)

            rtt_time = self._calc_delay(send_time, receive_time)
            packet_size = sys.getsizeof(packet)

            msg = "{} bytes from {}: seq={} time={:.3f} ms".format(
                packet_size,
                self.server_address,
                self.sequence_number,
                rtt_time
            )

            self.sequence_number += 1

            self._wait_until_next(rtt_time)

            print(msg)

        print('closing socket')
        my_socket.close()

    def make_socket(self):
        # Create a TCP/IP socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', 10000)
        print('connecting to {} port {}'.format(*server_address))
        my_socket.connect(server_address)
        return my_socket

    def send(self, my_socket):
        packet = self.build_packet()
        send_time = time.time()

        my_socket.sendall(packet)
        return send_time

    def receive(self, my_socket):
        timeout = self.timeout / 1000
        while True:
            select_start = time.time()
            readable, writable, exceptional = select.select([my_socket], [], [], timeout)
            select_duration = (time.time() - select_start)
            if not readable:
                print("packet loss")
                return 0, None

            packet, address = my_socket.recvfrom(1000)  # TODO: review this size
            receive_time = time.time()

            # TODO: do some checks ex: check sum (?
            return receive_time, packet

            timeout = timeout - select_duration
            if timeout <= 0:
                print("packet loss")
                return 0, None

    # TODO: define message structure
    def build_packet(self):
        message = b'This is the message.  It will be repeated.'
        return message

    def _calc_delay(self, send_time, receive_time):
        if not send_time or not receive_time:
            return -1
        return (receive_time - send_time) * 1000

    def _wait_until_next(self, delay):
        if self.max_wait > delay:
            time.sleep((self.max_wait - delay) / 1000)
