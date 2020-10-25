import sys
import time
import socket
import client

server_address = ('localhost', 10000)
client_address = "127.0.0.1"
timeout_seconds = 1
max_wait = 1000  # ms


def direct_ping(count):
    my_socket = client.make_socket()
    sequence_number = 0

    for i in range(0, count):
        send_time = send(my_socket)
        receive_time, packet = receive(my_socket)

        rtt_time = calc_delay(send_time, receive_time)
        packet_size = sys.getsizeof(packet)

        msg = "{} bytes from {}: seq={} time={:.3f} ms".format(
            packet_size,
            server_address,
            client_address,
            rtt_time
        )

        sequence_number += 1
        wait_until_next(rtt_time)

        print(msg)

    print('closing socket')
    my_socket.close()


def make_socket():
    # Create a TCP/IP socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    print('connecting to {} port {}'.format(*server_address))
    my_socket.connect(server_address)
    return my_socket


def send(my_socket):
    packet = build_packet()
    send_time = time.time()

    my_socket.sendall(packet)
    return send_time


def receive(my_socket):
    my_socket.settimeout(timeout_seconds)

    while True:
        try:
            packet, address = my_socket.recvfrom(1000)  # TODO: review this size
            receive_time = time.time()
        except socket.timeout:
            print("packet loss")
            return 0, None

        # TODO: do some checks ex: check sum (?
        return receive_time, packet


# TODO: define message structure
def build_packet():
    message = b'ping message'
    return message


def calc_delay(send_time, receive_time):
    if not send_time or not receive_time:
        return -1
    return (receive_time - send_time) * 1000


def wait_until_next(delay):
    if max_wait > delay:
        time.sleep((max_wait - delay) / 1000)
