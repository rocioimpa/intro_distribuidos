import socket
import os
from common_functions import receive_file
from constants import OP_CODE_DOWNLOAD, SOCK_TIMEOUT, MAX_TIMEOUT, CHUNK_SIZE


def download_file(server_address, name, dst):
    index = dst.rfind('/')
    folder = dst[:index]

    if not os.path.exists(folder):
        print("Creating destination folder")
        os.makedirs(folder, exist_ok=True)

    print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(SOCK_TIMEOUT)

    request = '{}|{}'.format(OP_CODE_DOWNLOAD, name)
    ack_from_server, response = send_message(request, sock, server_address)

    response = response.split('|')
    if not ack_from_server:
        print('Could not send request to server. Program exiting')
        return exit(1)

    if response == 'File not found':
        print('The requested file was not found in the server')
        return exit(1)

    total_chunks = int(response[1])
    send_message('ok', sock, server_address)
    receive_file(sock, server_address, dst, name, total_chunks)
    sock.close()


def send_message(request, cli_socket, server_address):
    for i in range(MAX_TIMEOUT):
        cli_socket.sendto(request.encode(), server_address)
        try:
            response, addr = cli_socket.recvfrom(CHUNK_SIZE)
            return True, response.decode('latin_1')
        except socket.timeout:
            print('Timeout number {} - Request: {}'.format(str(i), request))
    return False, ''
