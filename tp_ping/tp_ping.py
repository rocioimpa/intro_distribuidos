import getopt
import sys
import time
import socket


def display_summary(host):
    print('--- {} ping statistics ---'.format(host))
    print('{} packets transmitted, {} received, {}%packet loss, time {}ms'.format(0, 0, 0, 0))
    print('rtt min/avg/max/mdev = {}/{}/{}/{} ms'.format(0, 0, 0, 0))


def direct_ping(count, verbose, server, client):
    try:
        i = 0
        while True:
            if verbose:
                print('{} bytes from {}: seq={} time={}ms'.format(0, server, 0, 0))
            i += 1
            time.sleep(1)
            if count != 0 and i == count:
                break
    except KeyboardInterrupt:
        display_summary(server)


def reverse_ping(count, verbose, server, client):
    try:
        i = 0
        while True:
            if verbose:
                print('{} bytes from {}: seq={} time={}ms'.format(0, server, 0, 0))
            i += 1
            time.sleep(1)
            if count != 0 and i == count:
                break
    except KeyboardInterrupt:
        display_summary(client)


def print_operation_info(operation, server, client):
    print('TP-PING v0.1')
    print('Operation: {}'.format(operation))
    print('Server Address: {}'.format(server))
    print('Client Address: {}'.format(client))


def display_help_and_exit():
    print('Usage : tp_ping . py [ - h ] [ - v | -q ] [ - s ADDR ] [ - c COUNT ] [ -p | -r | -x ] [ - d ADDR ]')
    print('Optional arguments :')
    print('-h , -- help show this help message and exit')
    print('-v , -- verbose increase output verbosity')
    print('-q , -- quiet decrease output verbosity')
    print('-s , -- server server IP address')
    print('-c , -- count stop after < count > replies')
    print('-p , -- ping direct ping')
    print('-r , -- reverse reverse ping')
    print('-x , -- proxy proxy pin')
    print('-d , -- dest destination IP address)')
    sys.exit()


def main(argv):
    count = 0
    verbose = True
    server = "127.0.0.1"
    client = socket.gethostbyname(socket.gethostname())
    destination = ""

    try:
        opts, args = getopt.getopt(argv, "hvqs:c:prxd:",
                                   ["help", "verbose", "quiet", "server=", "count=", "ping", "reverse", "proxy",
                                    "dest="])
    except getopt.GetoptError:
        print('Option selected does not exist or requires input, for help type tp_ping.py -h')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            display_help_and_exit()
        if opt in ('-v', "--verbose"):
            verbose = True
        if opt in ('-q', "--quiet"):
            verbose = False
        if opt in ('-s', "--server"):
            print('server')
        if opt in ('-c', "--count"):
            count = arg
        if opt in ('-p', "--ping"):
            print_operation_info('Direct Ping', server, client)
            direct_ping(int(count), verbose, server, client)
        if opt in ('-r', "--reverse"):
            print_operation_info('Reverse Ping', server, client)
            reverse_ping(int(count), verbose, server, client)
        if opt in ('-x', "--proxy"):
            print_operation_info('Proxy Ping', server, client)
        if opt in ('-d', "--dest"):
            print('destination')


if __name__ == "__main__":
    main(sys.argv[1:])

# use timeit.timeit() for time measuring
