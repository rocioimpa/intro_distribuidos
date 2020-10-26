import math
from numpy import mean, absolute


def calculate_min_rtt(all_rtts):
    return min(all_rtts) if len(all_rtts) > 0 else 0


def calculate_max_rtt(all_rtts):
    return max(all_rtts) if len(all_rtts) > 0 else 0


def calculate_avg_rtt(all_rtts, sequence_number):
    return sum(all_rtts) / sequence_number if len(all_rtts) > 0 else 0


def calculate_mdev_rtt(all_rtts, sequence_number):
    return mean(absolute(all_rtts - mean(all_rtts))) if len(all_rtts) > 0 else 0


def close_socket(my_socket, server_address, all_rtts, sequence_number):
    print('closing socket')
    my_socket.close()
    display_summary(server_address, all_rtts, sequence_number)


def display_summary(server_address, all_rtts, sequence_number):
    min_rtt = calculate_min_rtt(all_rtts)
    max_rtt = calculate_max_rtt(all_rtts)
    avg_rtt = calculate_avg_rtt(all_rtts, sequence_number)
    mdev_rtt = calculate_mdev_rtt(all_rtts, sequence_number)
    packet_loss = (sequence_number - float(len(all_rtts))) / sequence_number * 100

    print('--- {} ping statistics ---'.format(server_address))
    print('{} packets transmitted, {} received, {} %packet loss, time {:.3f}ms'
          .format(sequence_number, len(all_rtts), packet_loss, 0))
    print('rtt min/avg/max/mdev = {:.3f}/{:.3f}/{:.3f}/{:.3f} ms'.format(min_rtt, max_rtt, avg_rtt, mdev_rtt))
