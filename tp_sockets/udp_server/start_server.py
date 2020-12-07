import sys
import os
import socket

from constants import (OP_CODE_DOWNLOAD, OP_CODE_UPLOAD,
                       OP_CODE_DOWNLOAD_RESP, OP_CODE_UPLOAD_RESP,
                       CHUNK_SIZE, ENCODE_TYPE, SOCK_TIMEOUT, MAX_TIMEOUT)


def start_server(server_address, storage_dir):
    try:
        if not os.path.exists(storage_dir) or not os.path.isdir(storage_dir):
            print('Invalid path to file: {} does not exist or \
                  is not a valid directory'.format(storage_dir))
            sys.exit(-1)

        print('UDP: start_server({}, {})'.format(server_address, storage_dir))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server_address)

        print("Socket bound to address {} and port {}"
              .format(server_address[0], server_address[1]))

        while True:
            sock.settimeout(None)
            request, client_address = sock.recvfrom(CHUNK_SIZE)
            request = request.decode(ENCODE_TYPE).split('|')

            try:
                op_code = int(request[0])
                filename = str(request[1])
                chunks_to_receive = int(request[2])
                if op_code not in (OP_CODE_DOWNLOAD, OP_CODE_UPLOAD):
                    print('Operation received is not supported')
                    exit(-1)
                if op_code == OP_CODE_UPLOAD:
                    print('Received upload request for file {} with \
                           total {} packets'.format(filename,
                                                    chunks_to_receive))
                    upload(filename, chunks_to_receive, sock, client_address,
                           storage_dir)
                if op_code == OP_CODE_DOWNLOAD:
                    download(request)
            except ValueError:
                continue

    except KeyboardInterrupt:
        print("Closing server after interrupt signal...")
        sock.close()
        sys.exit()


def upload(filename, chunks_to_receive, sock, address, storage_dir):
    sock.sendto('{}'.format(OP_CODE_UPLOAD_RESP).encode(ENCODE_TYPE), address)
    receive_file(sock, address, storage_dir, filename, chunks_to_receive)


def download(request):
    pass


def receive_file(sock, address, storage_dir, filename, total_chunks):
    chunks = {}
    received_chunks = 0
    timeouts = 0
    sock.settimeout(SOCK_TIMEOUT)

    while (received_chunks < total_chunks) and (timeouts < MAX_TIMEOUT):
        try:
            chunk, addr = sock.recvfrom(CHUNK_SIZE)
            seq_numb, chunk = chunk.decode(ENCODE_TYPE).split('|')

            timeouts = 0
            sock.sendto('{}|{}'.format('0', seq_numb).encode(), addr)
            if seq_numb not in chunks:
                chunks[seq_numb] = chunk
                received_chunks += 1

        except socket.timeout:
            print('Socket timeout')
            timeouts += 1
            continue

    if timeouts >= MAX_TIMEOUT:
        print('Timeout limit has been reached. Could not receive file')
        return 1

    sock.sendto(b'done', addr)
    write_file(chunks, storage_dir, filename)


def write_file(chunks, storage, filename):
    file = open(os.path.join(storage, filename), "wb")
    for i in range(0, len(chunks)):
        file.write(chunks[str(i)].encode(ENCODE_TYPE))
    file.close()
    print('File uploaded successfully')
