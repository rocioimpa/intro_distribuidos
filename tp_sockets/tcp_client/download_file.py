import socket
import sys
import os
from constants import OP_CODE_DOWNLOAD, MESSAGE_SIZE, ENCODE_TYPE, ACK_SIZE_RECEIVED
from logger_config import configLogger, LOGGING_LEVEL_INFO


logger = configLogger('download-client-tcp')


def download_file(server_address, name, dst, verbose):
    if not bool(verbose):
        logger.setLevel(LOGGING_LEVEL_INFO)

    try:
        index = dst.rfind('/')
        folder = dst[:index]

        if not os.path.exists(folder):
            logger.debug("Creating destination folder")
            os.makedirs(folder, exist_ok=True)

        logger.info('TCP: download_file({}, {}, {})'.format(server_address,
                                                            name, dst))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)

        message = '{},{}'.format(OP_CODE_DOWNLOAD, name)
        sock.send(message.encode('utf-8'))
        sock.recv(MESSAGE_SIZE)

        logger.debug('Sending download request to server {}'
                     .format(server_address))

        size = int(sock.recv(MESSAGE_SIZE).decode(ENCODE_TYPE))
        sock.send(str(ACK_SIZE_RECEIVED).encode())

        if size == -1:
            logger.error("The requested file ({}) was not found in the server"
                         .format(name))
            sock.close()
            sys.exit(0)

        else:
            logger.debug("Received file size: {}".format(size))

            fp = open(dst, "wb")

            received = 0
            logger.debug("Downloading file from {}".format(server_address))
            while received < size:
                chunk = sock.recv(MESSAGE_SIZE)
                received += len(chunk)
                logger.debug("Received packet from {}".format(server_address))
                fp.write(chunk)

            end_transfer(fp, sock)

    except KeyboardInterrupt:
        logger.debug(
            'KeyboardInterrupt signal received. Terminating process...')
        sock.close()
        sys.exit(0)


def end_transfer(fp, sock):
    fp.close()
    sock.close()
