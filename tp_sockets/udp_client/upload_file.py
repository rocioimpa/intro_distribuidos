import socket
import os
import sys

from common_functions import parse_file_to_chunks, send_file
from constants import (OP_CODE_UPLOAD, OP_CODE_UPLOAD_RESP, CHUNK_SIZE,
                       ENCODE_TYPE, MAX_TIMEOUT)


def upload_file(server_address, src, name):
    try:
        if not os.path.exists(src):
            print('Invalid path to file: {} does not exist or \
                is not a valid directory'.format(src))
            sys.exit(-1)

        print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))
        chunks = parse_file_to_chunks(src)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.1)

        ack_from_server = send_upload_request_to_server(name, len(chunks),
                                                        server_address, sock)

        if ack_from_server:
            send_file(chunks, server_address, sock)
        else:
            print('Unable to send request to server. Terminating process...')
            sock.close()
            sys.exit(1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt signal received. Terminating process...')
        sock.close()
        sys.exit(0)


def send_upload_request_to_server(name, chunks_amount, address, sock):
    request = '{}|{}|{}'.format(OP_CODE_UPLOAD, name, str(chunks_amount))

    for i in range(MAX_TIMEOUT):
        print('Attempting to send upload request to server, {} of {}'
              .format(i+1, MAX_TIMEOUT))
        sock.sendto(request.encode(ENCODE_TYPE), address)
        try:
            acked, address = sock.recvfrom(CHUNK_SIZE)
            if int(acked.decode(ENCODE_TYPE)) == OP_CODE_UPLOAD_RESP:
                return True
        except socket.timeout:
            print('Request has timed out')

    return False
