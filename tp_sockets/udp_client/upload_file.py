import socket
import os
import sys

from constants import (OP_CODE_UPLOAD, OP_CODE_UPLOAD_RESP, CHUNK_SIZE,
                       ENCODE_TYPE, MAX_TIMEOUT, WINDOW_SIZE)


def upload_file(server_address, src, name):
    try:
        if not os.path.exists(src):
            print('Invalid path to file: {} does not exist or \
                is not a valid directory'.format(src))
            sys.exit(-1)

        print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))
        chunks = parse_file_to_chunks(src)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)

        ack_from_server = send_upload_request_to_server(name, len(chunks),
                                                        server_address, sock)

        if ack_from_server:
            send_file_to_upload_to_server(chunks, server_address, sock)
        else:
            print('Unable to send request to server. Terminating process...')
            sock.close()
            sys.exit(1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt signal received. Terminating process...')
        sock.close()
        sys.exit(0)


def parse_file_to_chunks(file):
    file_to_read = open(file, 'rb')
    chunks = {}
    seq_numb = 0

    while True:
        header = '{}|'.format(seq_numb)
        chunk = file_to_read.read(CHUNK_SIZE - len(header))
        if not chunk:
            break

        chunks[str(seq_numb)] = header + chunk.decode(ENCODE_TYPE)
        seq_numb += 1

    file_to_read.close()
    return chunks


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


def send_file_to_upload_to_server(chunks, address, sock):
    sent_chunks = 0
    total_chunks = len(chunks)
    timeouts = 0

    while (timeouts < MAX_TIMEOUT and sent_chunks < total_chunks):
        seq_numbs = list(chunks.keys())
        pending_chunks = total_chunks - sent_chunks

        remaining_chunks = pending_chunks
        if pending_chunks > WINDOW_SIZE:
            remaining_chunks = WINDOW_SIZE

        for i in range(remaining_chunks):
            msg = chunks[seq_numbs[i]].encode(ENCODE_TYPE)
            sock.sendto(msg, address)

        for j in range(remaining_chunks):
            try:
                server_response, addr = sock.recvfrom(CHUNK_SIZE)
                parsed_response = server_response.decode().split('|')
                acked = bool(parsed_response[0])
                acked_seq_numb = int(parsed_response[1])
                if acked:
                    print('File sent successfully!')
                    sock.close()
                    sys.exit(0)
                timeouts = 0
                if acked_seq_numb in seq_numbs:
                    sent_chunks += 1
                    chunks.pop(acked_seq_numb)

            except socket.timeout:
                timeouts += 1
                print('File sending has timed out')
                continue

    if timeouts >= MAX_TIMEOUT:
        print('Could not send request to server. Program exiting')
        sock.close()
        exit(1)
