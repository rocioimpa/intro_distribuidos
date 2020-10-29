import math
import time
from numpy import mean, absolute
import socket

timeout_seconds = 1


def calculate_min_rtt(all_rtts):
    return min(all_rtts) if len(all_rtts) > 0 else 0


def calculate_max_rtt(all_rtts):
    return max(all_rtts) if len(all_rtts) > 0 else 0


def calculate_avg_rtt(all_rtts, sequence_number):
    return sum(all_rtts) / sequence_number if len(all_rtts) > 0 else 0


def calculate_mdev_rtt(all_rtts, sequence_number):
    return mean(absolute(all_rtts - mean(all_rtts))) if len(all_rtts) > 0 else 0


def calculate_elapsed_time(start_time,end_time):
    return (end_time - start_time) * 1000


def close_socket(my_socket, server_address, all_rtts, sequence_number, start_time):
    my_socket.close()
    display_summary(server_address, all_rtts, sequence_number, start_time)


def display_summary(server_address, all_rtts, sequence_number, start_time):
    end_time = time.time()
    elapsed_time = calculate_elapsed_time(start_time, end_time)

    min_rtt = calculate_min_rtt(all_rtts)
    max_rtt = calculate_max_rtt(all_rtts)
    avg_rtt = calculate_avg_rtt(all_rtts, sequence_number)
    mdev_rtt = calculate_mdev_rtt(all_rtts, sequence_number)
    packet_loss = (sequence_number - float(len(all_rtts))) / sequence_number * 100

    print('\n')
    print('--- {} ping statistics ---'.format(server_address))
    print('{} packets transmitted, {} received, {:.3f}% packet loss, time {:.3f}ms'
          .format(sequence_number, len(all_rtts), packet_loss, elapsed_time))
    print('rtt min/avg/max/mdev = {:.3f}/{:.3f}/{:.3f}/{:.3f} ms'.format(min_rtt, max_rtt, avg_rtt, mdev_rtt))


def receive_command(my_socket):
    my_socket.settimeout(timeout_seconds)

    while True:
        try:
            packet, address = my_socket.recvfrom(1000)
        except socket.timeout:
            return 0, None

        return packet
