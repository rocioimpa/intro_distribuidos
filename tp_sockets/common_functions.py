import socket
import os
from random import randint
import argparse

from constants import (ENCODE_TYPE, CHUNK_SIZE, MAX_TIMEOUT, SOCK_TIMEOUT)
from logger_config import configLogger, LOGGING_LEVEL_INFO

logger = logger = configLogger('common')


def str2bool(v):
    value = True
    if isinstance(v, bool):
        value = v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        value = True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        value = False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    if not value:
        logger.setLevel(LOGGING_LEVEL_INFO)
    return value


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


def write_file(chunks, storage, filename):
    file = open(os.path.join(storage, filename), "wb")
    for i in range(0, len(chunks)):
        file.write(chunks[str(i)].encode(ENCODE_TYPE))
    file.close()


def send_file(chunks, address, sock):
    sent_chunks = 0
    total_chunks = len(chunks)
    pending_chunks = total_chunks
    timeouts = 0

    retry = 0
    while (timeouts < MAX_TIMEOUT and len(chunks) > 0):
        logger.debug("Sending with retry " + str(retry))
        seq_numbs = list(chunks.keys())

        for seq_numb in chunks.keys():
            msg = chunks[seq_numb].encode(ENCODE_TYPE)
            logger.debug('Sending chunk {}'.format(seq_numb))
            sock.sendto(msg, address)

        for j in range(pending_chunks):
            try:
                server_response, addr = sock.recvfrom(CHUNK_SIZE)

                acked_seq_numb = server_response.decode()

                logger.debug('Receiving ack chunk {}'.format(acked_seq_numb))

                timeouts = 0
                if acked_seq_numb in seq_numbs:
                    sent_chunks += 1
                    pending_chunks -= 1
                    chunks.pop(acked_seq_numb)

            except socket.timeout:
                timeouts += 1
                logger.debug('File sending has timed out')
                continue
        retry += 1

    if timeouts >= MAX_TIMEOUT:
        logger.error('Could not send request to server. Program exiting')
        sock.close()
        exit(1)

    logger.info("File was sent successfully")


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

            # simulate timeout
            x = randint(0, 10)
            if x > 2:
                sock.sendto('{}'.format(seq_numb).encode(), addr)
                if seq_numb not in chunks:
                    chunks[seq_numb] = chunk
                    received_chunks += 1

        except socket.timeout:
            logger.debug('Socket timeout')
            timeouts += 1
            continue

    if timeouts >= MAX_TIMEOUT:
        logger.debug('Timeout limit has been reached. Could not receive file')
        return 1

    sock.sendto(b'done', addr)
    try:
        write_file(chunks, storage_dir, filename)
        logger.info('File saved successfully')
    except IOError:
        logger.error('There was an error when saving the file')
