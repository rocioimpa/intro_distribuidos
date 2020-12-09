import socket
import os
from constants import (MESSAGE_SIZE, OP_CODE_UPLOAD, OP_CODE_DOWNLOAD,
                       ACK_SIZE_RECEIVED)
from logger_config import configLogger, LOGGING_LEVEL_INFO


logger = configLogger('server')


def create_socket(server_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    return sock


def close_socket(sock):
    sock.close()


def start_server(server_address, storage_dir, verbose):
    if not bool(verbose):
        logger.setLevel(LOGGING_LEVEL_INFO)

    print('TCP: start_server({}, {})'.format(server_address, storage_dir))

    sock = create_socket(server_address)
    sock.listen()

    while True:
        connection, address = sock.accept()
        if not connection:
            return close_socket(sock)

        print("Connection from {}".format(address))

        parsed_response = connection.recv(MESSAGE_SIZE).decode().split(',')
        op_code = int(parsed_response[0])
        file_name = parsed_response[1]

        full_file_name = "{}/{}".format(storage_dir, file_name)
        if op_code == OP_CODE_DOWNLOAD:
            start_download(full_file_name, connection)
        elif op_code == OP_CODE_UPLOAD:
            file_size = int(parsed_response[2])
            start_upload(full_file_name, file_size, connection)


def start_download(file_name, connection):
    connection.send(str(ACK_SIZE_RECEIVED).encode())
    fp = open(file_name, "rb")
    size = os.path.getsize(file_name)

    print("Sent file size: {}".format(size))

    connection.send(str(size).encode())

    while True:
        chunk = fp.read(MESSAGE_SIZE)
        if not chunk:
            break
        connection.send(chunk)

    end_transfer(fp, connection)


def start_upload(file_name, file_size, connection):
    connection.send(str(ACK_SIZE_RECEIVED).encode())
    fp = open(file_name, "wb")
    received = 0
    while received < file_size:
        chunk = connection.recv(MESSAGE_SIZE)
        received += len(chunk)
        fp.write(chunk)

    end_transfer(fp, connection)


def end_transfer(fp, connection):
    fp.close()
    connection.close()
