import client
import socket
import sys
import time
import calculations as calc

server_address = ('localhost', 10000)
client_address = "127.0.0.1"
timeout_seconds = 1
max_wait = 1000  # ms


def reverse_ping(count, verbose):
    my_socket = client.make_socket()
    send_reverse_command(my_socket, count)  # send a message to server indicating the reverse operation

    # TODO: identify when the server stop sending ping message
    while True:
        data = my_socket.recv(1000)

        print('received {!r}'.format(data))
        if data:
            print('sending data back to the server')
            my_socket.sendall(data)
        else:
            print('no data from')
            break
        count += 1


def ping(server_socket, count):
    sequence_number = 1
    i = 0

    try: 
        while True: 
            send_time = send(server_socket)
            
            try:
                receive_time, packet = receive(server_socket)
            except socket.timeout:
                print("packet loss")
                return 0, None

            rtt_time = calc_delay(send_time, receive_time)
            packet_size = sys.getsizeof(packet)

            msg = "{} bytes from {}: seq={} time={:.3f} ms".format(
                packet_size,
                client_address,
                sequence_number,
                rtt_time
            )

            sequence_number += 1
            wait_until_next(rtt_time)

            print(msg)

            i += 1
            if count != 0 and i == count:
                break
    except:
        pass


def send_reverse_command(my_socket, count):
    message = 'reverse' + str(count)
    send_time = time.time()
    my_socket.sendall(message.encode('utf-8'))
    return send_time


def send(my_socket):
    packet = build_packet()
    send_time = time.time()

    my_socket.sendall(packet)
    return send_time


def receive(my_socket):
    while True:
        try:
            packet = my_socket.recv(1000)
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
