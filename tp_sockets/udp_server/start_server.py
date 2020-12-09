import sys
import os
import socket
from random import seed

from common_functions import parse_file_to_chunks, send_file, receive_file
from constants import (OP_CODE_DOWNLOAD, OP_CODE_UPLOAD,
                       OP_CODE_DOWNLOAD_RESP, OP_CODE_UPLOAD_RESP,
                       CHUNK_SIZE, ENCODE_TYPE, SOCK_TIMEOUT, MAX_TIMEOUT)
from logger_config import configLogger, LOGGING_LEVEL_INFO

seed(1)

logger = configLogger('udp-server')


def start_server(server_address, storage_dir, verbose):
    if not bool(verbose):
        logger.setLevel(LOGGING_LEVEL_INFO)

    try:
        if not os.path.exists(storage_dir) or not os.path.isdir(storage_dir):
            logger.info('Invalid path to file: {} does not exist or \
                  is not a valid directory'.format(storage_dir))
            sys.exit(-1)

        logger.info('UDP: start_server({}, {})'.format(server_address,
                                                       storage_dir))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server_address)

        logger.debug("Socket bound to address {} and port {}"
                     .format(server_address[0], server_address[1]))

        while True:
            sock.settimeout(None)
            request, client_address = sock.recvfrom(CHUNK_SIZE)
            request = request.decode(ENCODE_TYPE).split('|')

            try:
                op_code = int(request[0])
                filename = str(request[1])
                if op_code not in (OP_CODE_DOWNLOAD, OP_CODE_UPLOAD):
                    logger.error('Operation received is not supported')
                    exit(-1)
                if op_code == OP_CODE_UPLOAD:
                    chunks_to_receive = int(request[2])
                    logger.debug('Received upload request for file {} with \
                           total {} packets'.format(filename,
                                                    chunks_to_receive))
                    upload(filename, chunks_to_receive, sock, client_address,
                           storage_dir)
                if op_code == OP_CODE_DOWNLOAD:
                    logger.debug('Received download request for file {} from \
                           address {} packets'.format(filename,
                                                      client_address))
                    download(filename, sock, client_address, storage_dir)

            except ValueError:
                continue

    except KeyboardInterrupt:
        logger.debug("Closing server after interrupt signal...")
        sock.close()
        sys.exit()


def upload(filename, chunks_to_receive, sock, address, storage_dir):
    sock.sendto('{}'.format(OP_CODE_UPLOAD_RESP).encode(ENCODE_TYPE), address)
    receive_file(sock, address, os.path.join(storage_dir, filename), chunks_to_receive)


def download(filename, sock, client_address, storage_dir):
    sock.settimeout(SOCK_TIMEOUT)
    filepath = storage_dir+'/'+filename

    if os.path.exists(filepath):
        send_file_info(filepath, sock, client_address)
    else:
        sock.sendto(b'File not found', client_address)


def send_file_info(filename, sock, address):
    chunks = parse_file_to_chunks(filename)

    for i in range(MAX_TIMEOUT):
        response_msg = '{}|{}'.format(OP_CODE_DOWNLOAD_RESP, str(len(chunks)))
        sock.sendto(response_msg.encode(ENCODE_TYPE), address)
        try:
            ack, addr = sock.recvfrom(CHUNK_SIZE)
            send_file(chunks, address, sock)
            break
        except socket.timeout:
            logger.debug('Timeout sending file info.')
    return 1
