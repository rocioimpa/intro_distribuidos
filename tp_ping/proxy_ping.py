import client
import socket
import sys
import time
import common

timeout_seconds = 1
max_wait = 1000  # ms


def proxy_ping(count, verbose, server_address, destination):
    my_socket = client.make_socket()
    send_proxy_command(my_socket, count, destination)  # send a message to server indicating the proxy operation
    all_rtts = []
    sequence_number = 0
    i = 0

    try: 
        while True:
            data = my_socket.recv(1000)

            print('received {!r}'.format(data))
            if data:
                if 'response' in data.decode():
                    response = data.decode()
                    parsed_response = response.split(',')

                    packet_size = int(parsed_response[1])
                    sequence_number = int(parsed_response[2])
                    rtt_time = float(parsed_response[3])

                    msg = "{} bytes from {}: seq={} time={:.3f} ms".format(
                        packet_size,
                        destination,
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
                    print('sending data back to the server')
                    my_socket.sendall(data)

            else:
                print('no data from')
                break
    except KeyboardInterrupt: 
        pass

    common.close_socket(my_socket, destination, all_rtts, sequence_number)

def ping(server_socket, count, destination):
    sequence_number = 1
    i = 0
    destination = ("127.0.0.1",9800)
    try: 
        while True: 
            send_time = send(server_socket,destination)
            
            try:
                receive_time, packet = receive(server_socket)
            except socket.timeout:
                print("packet loss")
                return 0, None

            rtt_time = calc_delay(send_time, receive_time)
            packet_size = sys.getsizeof(packet)

            msg = "{} bytes from {}: seq={} time={:.3f} ms".format(
                packet_size,
                destination,
                sequence_number,
                rtt_time
            )

            print('sending results to client')
            results = "response,{},{},{:.3f}".format(packet_size,sequence_number,rtt_time)
            
            send_results(server_socket,results)

            sequence_number += 1
            wait_until_next(rtt_time)

            print(msg)

            i += 1
            if count != 0 and i == count:
                break
    except:
        pass


def send_proxy_command(my_socket, count, destination):
    message = 'proxy,{},{}'.format(str(count),destination)
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
            print(packet)
        except socket.timeout:
            print("packet loss")
            return 0, None

        # TODO: do some checks ex: check sum (?
        return receive_time, packet


# TODO: define message structure
def build_packet():
    message = 'ping'
    return message.encode('utf-8')


def calc_delay(send_time, receive_time):
    if not send_time or not receive_time:
        return -1
    return (receive_time - send_time) * 1000


def wait_until_next(delay):
    if max_wait > delay:
        time.sleep((max_wait - delay) / 1000)
