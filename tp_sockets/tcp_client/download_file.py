import socket
from constants import *


def download_file(server_address, name, dst):
    print('TCP: download_file({}, {}, {})'.format(server_address, name, dst))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    message = '{},{}'.format(OP_CODE_DOWNLOAD, name)
    sock.sendall(message.encode('utf-8'))

    size = int(sock.recv(MESSAGE_SIZE).decode())
    print("Received file size: {}".format(size))

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
