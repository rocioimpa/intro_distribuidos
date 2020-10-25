import math
from numpy import mean, absolute

def calculate_min_rtt(all_rtts):
    return min(all_rtts)


def calculate_max_rtt(all_rtts):
    return max(all_rtts)


def calculate_avg_rtt(all_rtts, sequence_number):
    return sum(all_rtts) / sequence_number
    

def calculate_mdev_rtt(all_rtts, sequence_number):
    return mean(absolute(all_rtts - mean(all_rtts))) 