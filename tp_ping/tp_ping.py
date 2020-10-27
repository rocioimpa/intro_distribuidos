import getopt

from direct_ping import *
from reverse_ping import *
#from proxy_ping import *


def main(argv):
    count = 0
    verbose = True
    server_address = ('localhost', 10000)
    client_address = "127.0.0.1"
    destination = ""
    operation_type = 'direct'

    try:
        opts, args = getopt.getopt(argv, "hvqs:c:prxd:",
                                   ["help", "verbose", "quiet", "server=", "count=", "ping", "reverse", "proxy",
                                    "dest="])
    except getopt.GetoptError:
        print ('Option selected does not exist or requires input, for help type tp_ping.py -h')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print ('usage : tp_ping . py [ - h ] [ - v | -q ] [ - s ADDR ] [ - c COUNT ] [ -p | -r | -x ] [ - d ADDR ]')
            print ('\n')
            print ('optional arguments :')
            print ('-h , -- help show this help message and exit')
            print ('-v , -- verbose increase output verbosity')
            print ('-q , -- quiet decrease output verbosity')
            print ('-s , -- server server IP address')
            print ('-c , -- count stop after < count > replies')
            print ('-p , -- ping direct ping')
            print ('-r , -- reverse reverse ping')
            print ('-x , -- proxy proxy pin')
            print ('-d , -- dest destination IP address)')
            sys.exit()
        if opt in ('-v', "--verbose"):
            verbose = True
        if opt in ('-q', "--quiet"):
            verbose = False
        if opt in ('-s', "--server"):
            server_address = arg
        if opt in ('-c', "--count"):
            count = arg
        if opt in ('-p', "--ping"):
            operation_type = 'direct'
        if opt in ('-r', "--reverse"):
            operation_type = 'reverse'
        if opt in ('-x', "--proxy"):
            operation_type = 'proxy'
        if opt in ('-d', "--dest"):
            destination = arg

    print('TP-PING v0.1')
    print('Operation: {} Ping'.format(operation_type.title()))
    print('Server Address: {}'.format(server_address))
    print('Client Address: {}'.format(client_address))

    if operation_type == 'direct':
        direct_ping(int(count), verbose, server_address, client_address)
    if operation_type == 'reverse':
        reverse_ping(int(count), verbose, server_address, client_address)
    if operation_type == 'proxy': 
        print('proxy ping')
        #proxy_ping(int(count), verbose, server_address, destination)


if __name__ == "__main__":
    main(sys.argv[1:])


# use timeit.timeit() for time measuring
