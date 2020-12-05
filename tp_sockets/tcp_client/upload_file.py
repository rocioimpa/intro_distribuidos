import socket
import os
from constants import *


def upload_file(server_address, src, name):
    print('TCP: upload_file({}, {}, {})'.format(server_address, src, name))

    fp = open(src, "rb")
    size = os.path.getsize(src)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    message = '{},{},{}'.format(OP_CODE_UPLOAD, name, size)
    sock.send(message.encode('utf-8'))
    sock.recv(MESSAGE_SIZE)

    while True:
        chunk = fp.read(MESSAGE_SIZE)
        if not chunk:
            break
        sock.send(chunk)

    end_transfer(fp, sock)


def end_transfer(fp, sock):
    fp.close()
    sock.close()