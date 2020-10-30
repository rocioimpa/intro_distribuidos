import client
import socket
import sys
import time
import common
import constants

timeout_seconds = 1
max_wait = 1000  # ms


def reverse_ping(count, verbose, server_address, client_address):
    my_socket = client.make_socket(server_address)
    send_reverse_command(my_socket, count)  # send a message to server indicating the reverse operation
    all_rtts = []
    sequence_number = 0
    i = 0

    try:
        start_time = time.time()
        while True:
            data = my_socket.recv(constants.SIZE_MESSAGE)

            if data:
                if constants.OP_CODE_RESPONSE in data.decode():
                    response = data.decode()
                    parsed_response = response.split(',')

                    packet_size = int(parsed_response[1])
                    sequence_number = int(parsed_response[2])
                    rtt_time = float(parsed_response[3])

                    msg = "{} bytes from {}: seq={} time={:.3f} ms".format(
                        packet_size,
                        client_address,
                        sequence_number,
                        rtt_time
                    )

                    all_rtts.append(rtt_time)

                    if verbose:
                        print(msg)

                    i += 1
                    if count != 0 and i == count:
                        break

                else:
                    my_socket.sendall(data)

            else:
                print('No data received from')
                break
    except KeyboardInterrupt:
        pass

    common.close_socket(my_socket, server_address, all_rtts, sequence_number, start_time)


def ping(server_socket, count, client_address):
    sequence_number = 1
    i = 0

    try:
        while True:
            send_time = send(server_socket)

            try:
                receive_time, packet = receive(server_socket)
            except socket.timeout:
                print("Packet loss")
                return 0, None

            rtt_time = common.calc_delay(send_time, receive_time)
            packet_size = sys.getsizeof(packet)

            results = "{},{},{},{:.3f}".format(constants.OP_CODE_RESPONSE, packet_size, sequence_number, rtt_time)

            send_results(server_socket, results)

            sequence_number += 1
            common.wait_until_next(rtt_time)

            i += 1
            if count != 0 and i == count:
                break
    except:
        pass


def send_reverse_command(my_socket, count):
    message = '{},{}'.format(constants.OP_CODE_REVERSE, str(count))
    send_time = time.time()
    my_socket.sendall(message.encode('utf-8'))
    return send_time


def send_results(my_socket, msg):
    my_socket.sendall(msg.encode('utf-8'))


def send(my_socket):
    packet = build_packet()
    send_time = time.time()

    my_socket.sendall(packet)
    return send_time


def receive(my_socket):
    while True:
        try:
            packet = my_socket.recv(constants.SIZE_MESSAGE)
            receive_time = time.time()
        except socket.timeout:
            print("Packet loss")
            return 0, None

        return receive_time, packet


def build_packet():
    message = '{},{}'.format(constants.OP_CODE_REVERSE, constants.PING_MESSAGE)
    return message.encode('utf-8')
