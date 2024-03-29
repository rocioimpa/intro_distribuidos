import sys
import time
import socket
import client
import common
import constants


def direct_ping(count, verbose, server_address):
    my_socket = client.make_socket(server_address)
    start_time = send_signal(my_socket)  # establish the connection by sending a direct ping to the server
    response = common.receive_command(my_socket)  # await for the server's response

    i = 0
    sequence_number = 1
    rtt_time = 2
    all_rtts = []

    if response is not None and response.decode() == constants.OP_CODE_RESPONSE:
        try:
            while True:
                send_time = send(my_socket)
                receive_time, packet = receive(my_socket)

                if packet is None:
                    print("Request timed out.")

                else:
                    rtt_time = common.calc_delay(send_time, receive_time)
                    packet_size = sys.getsizeof(packet)

                    msg = "{} bytes from {}: seq={} time={:.3f} ms".format(
                        packet_size,
                        server_address,
                        sequence_number,
                        rtt_time
                    )

                    all_rtts.append(rtt_time)

                if verbose:
                    print(msg)

                i += 1
                if count != 0 and i == count:
                    break

                sequence_number += 1
                common.wait_until_next(rtt_time)

        except KeyboardInterrupt:
            pass

    common.close_socket(my_socket, server_address, all_rtts, sequence_number, start_time)


def send(my_socket):
    packet = build_packet()
    send_time = time.time()

    my_socket.sendall(packet)
    return send_time


def receive(my_socket):
    my_socket.settimeout(constants.TIMEOUT_SECONDS)

    while True:
        try:
            packet, address = my_socket.recvfrom(constants.SIZE_MESSAGE)
            receive_time = time.time()
        except socket.timeout:
            return 0, None

        return receive_time, packet


def send_signal(my_socket):
    message = '{}'.format(constants.OP_CODE_DIRECT)
    send_time = time.time()
    my_socket.sendall(message.encode('utf-8'))
    return send_time


def build_packet():
    message = '{},{}'.format(constants.OP_CODE_DIRECT, constants.PING_MESSAGE)
    return message.encode('utf-8')
