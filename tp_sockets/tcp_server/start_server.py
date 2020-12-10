import socket
import os
import sys
from constants import (MESSAGE_SIZE, OP_CODE_UPLOAD, OP_CODE_DOWNLOAD,
                       ACK_SIZE_RECEIVED)
from logger_config import configLogger, LOGGING_LEVEL_INFO


logger = configLogger('tcp-server')


def create_socket(server_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    return sock


def close_socket(sock):
    sock.close()


def start_server(server_address, storage_dir, verbose):
    if not bool(verbose):
        logger.setLevel(LOGGING_LEVEL_INFO)

    try:
        if not os.path.exists(storage_dir) or not os.path.isdir(storage_dir):
            logger.info('Invalid path to file: {} does not exist or \
                         is not a valid directory'.format(storage_dir))
            sys.exit(-1)

        logger.info('TCP: start_server({}, {})'.format(server_address,
                                                       storage_dir))

        sock = create_socket(server_address)
        sock.listen()

        while True:
            connection, address = sock.accept()
            if not connection:
                return close_socket(sock)

            logger.debug("Connection from {}".format(address))

            parsed_response = connection.recv(MESSAGE_SIZE).decode().split(',')
            op_code = int(parsed_response[0])
            file_name = parsed_response[1]

            full_file_name = "{}/{}".format(storage_dir, file_name)
            if op_code not in (OP_CODE_DOWNLOAD, OP_CODE_UPLOAD):
                logger.error('Operation received is not supported')
                exit(-1)
            if op_code == OP_CODE_DOWNLOAD:
                logger.debug("Received message requesting download from {}"
                             .format(address))
                start_download(full_file_name, connection, address)
            elif op_code == OP_CODE_UPLOAD:
                file_size = int(parsed_response[2])
                logger.debug(
                    "Received message requesting download from {}, size: {}"
                    .format(address, file_size))
                start_upload(full_file_name, file_size, connection)

    except KeyboardInterrupt:
        logger.debug("Closing server after interrupt signal...")
        sock.close()
        sys.exit()


def start_download(file_name, connection, address):
    connection.send(str(ACK_SIZE_RECEIVED).encode())

    if not os.path.exists(file_name):
        logger.info('The requested file: {} does not exist'.format(file_name))
        connection.send(str(-1).encode())
        connection.close()
    else:
        fp = open(file_name, "rb")
        size = os.path.getsize(file_name)

        # Calculate the missing number of bytes
        pad_size = MESSAGE_SIZE - len(str(size)) % MESSAGE_SIZE

        # Add missing bytes with 'white spaces'
        fixed_size = ("0" * pad_size) + str(size)

        logger.debug("Sent file size: {}".format(size))

        print(fixed_size)
        # print(len(fixed_size.encode('utf-8')))
        # print(int(fixed_size))

        connection.send(str(fixed_size).encode())

        logger.debug("Starting tranmission")
        while True:
            chunk = fp.read(MESSAGE_SIZE)
            if not chunk:
                break
            logger.debug("Sending packet to address {}".format(address))
            connection.send(chunk)

        end_transfer(fp, connection)


def start_upload(file_name, file_size, connection):
    connection.send(str(ACK_SIZE_RECEIVED).encode())
    fp = open(file_name, "wb")
    received = 0

    logger.debug("Receiving data")

    while received < file_size:
        chunk = connection.recv(MESSAGE_SIZE)
        received += len(chunk)
        fp.write(chunk)

    end_transfer(fp, connection)


def end_transfer(fp, connection):
    logger.debug("Transfer completed, closing connection")
    fp.close()
    connection.close()
