import socket
import os
import sys
from constants import OP_CODE_UPLOAD, MESSAGE_SIZE, ENCODE_TYPE
from logger_config import configLogger, LOGGING_LEVEL_INFO


logger = configLogger('upload-client-tcp')


def upload_file(server_address, src, name, verbose):
    if not bool(verbose):
        logger.setLevel(LOGGING_LEVEL_INFO)

    try:
        if not os.path.exists(src):
            logger.error('Invalid path to file: {} does not exist or \
                is not a valid directory'.format(src))
            sys.exit(-1)

        logger.info('TCP: upload_file({}, {}, {})'.format(server_address, src,
                                                          name))

        fp = open(src, "rb")
        size = os.path.getsize(src)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)

        message = '{},{},{}'.format(OP_CODE_UPLOAD, name, size)

        logger.debug('Sending upload request to server {}'
                     .format(server_address))

        sock.send(message.encode(ENCODE_TYPE))
        sock.recv(MESSAGE_SIZE)

        while True:
            chunk = fp.read(MESSAGE_SIZE)
            if not chunk:
                break
            logger.debug("Sending packet to address {}"
                         .format(server_address))
            sock.send(chunk)

        end_transfer(fp, sock)

    except KeyboardInterrupt:
        logger.debug(
            'KeyboardInterrupt signal received. Terminating process...')
        sock.close()
        sys.exit(0)


def end_transfer(fp, sock):
    fp.close()
    sock.close()
