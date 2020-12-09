import socket
from constants import OP_CODE_DOWNLOAD, MESSAGE_SIZE
from logger_config import configLogger, LOGGING_LEVEL_INFO


logger = configLogger('server')


def download_file(server_address, name, dst, verbose):
    if not bool(verbose):
        logger.setLevel(LOGGING_LEVEL_INFO)

    logger.info('TCP: download_file({}, {}, {})'.format(server_address, name,
                                                        dst))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    message = '{},{}'.format(OP_CODE_DOWNLOAD, name)
    sock.send(message.encode('utf-8'))
    sock.recv(MESSAGE_SIZE)

    size = int(sock.recv(MESSAGE_SIZE).decode())
    logger.debug("Received file size: {}".format(size))

    fp = open(dst, "wb")

    received = 0
    while received < size:
        chunk = sock.recv(MESSAGE_SIZE)
        received += len(chunk)
        fp.write(chunk)

    end_transfer(fp, sock)


def end_transfer(fp, sock):
    fp.close()
    sock.close()
