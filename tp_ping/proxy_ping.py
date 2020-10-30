import client
import socket
import sys
import time
import common
import constants

timeout_seconds = 1
max_wait = 1000  # ms


def proxy_ping(count, verbose, server_address, destination):
    my_socket = client.make_socket(server_address)
    send_proxy_command(my_socket, count, destination)  # send a message to server indicating the proxy operation
    all_rtts = []
    sequence_number = 0
    i = 0

    start_time = time.time()
    try:
        while True:
            data = my_socket.recv(1000)

            if data:
                if constants.OP_CODE_RESPONSE in data.decode():
                    response = data.decode()
                    parsed_response = response.split(',')

                    packet_size = int(parsed_response[1])
                    sequence_number = int(parsed_response[2])
                    rtt_time = float(parsed_response[3])

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

                else:
                    my_socket.sendall(data)

            else:
                break
    except KeyboardInterrupt:
        pass

    common.close_socket(my_socket, destination, all_rtts, sequence_number, start_time)


def ping(server_socket, count, destination_ip, destination_port):
    sequence_number = 1
    i = 0
    destination = (destination_ip, destination_port)
    server_b_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_b_socket.connect(destination)
    try:
        while True:
            send_time = send(server_b_socket, destination)

            try:
                receive_time, packet = receive(server_b_socket)
            except socket.timeout:
                print("Packet loss")
                return 0, None

            rtt_time = calc_delay(send_time, receive_time)
            packet_size = sys.getsizeof(packet)

            print('Sending results to client')
            results = "{},{},{},{:.3f}".format(constants.OP_CODE_RESPONSE, packet_size, sequence_number, rtt_time)

            send_results(server_socket, results)

            sequence_number += 1
            wait_until_next(rtt_time)

            i += 1
            if count != 0 and i == count:
                break
    except:
        pass


def send_proxy_command(my_socket, count, destination):
    message = '{},{},{}'.format(constants.OP_CODE_PROXY, str(count), destination)
    send_time = time.time()
    my_socket.sendall(message.encode('utf-8'))
    return send_time


def send_results(my_socket, msg):
    my_socket.sendall(msg.encode('utf-8'))


def send(my_socket, destination):
    packet = build_packet()
    send_time = time.time()

    my_socket.sendto(packet, destination)
    return send_time


def receive(my_socket):
    while True:
        try:
            packet = my_socket.recv(1000)
            receive_time = time.time()
        except socket.timeout:
            print("Packet loss")
            return 0, None

        return receive_time, packet


def build_packet():
    message = '{},{}'.format(constants.OP_CODE_DIRECT, constants.PING_MESSAGE)
    return message.encode('utf-8')


def calc_delay(send_time, receive_time):
    if not send_time or not receive_time:
        return -1
    return (receive_time - send_time) * 1000


def wait_until_next(delay):
    if max_wait > delay:
        time.sleep((max_wait - delay) / 1000)
