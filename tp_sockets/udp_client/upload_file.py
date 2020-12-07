import socket
import os
import random

from constants import OP_CODE_UPLOAD, CHUNK_SIZE, ENCODE_TYPE
from common_functions import default_file_transfer_data, create_header


def upload_file(server_address, src, name):
    print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))

    connection_id = random.randint(1, 100000000)
    fp = open(src, "rb")
    fp_content = fp.read()
    fp.close()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setblocking(False)
    sock.connect_ex(server_address)
    data = default_file_transfer_data()
    data.connection_id = connection_id
    data.op_code = OP_CODE_UPLOAD
    data.file_name = name.encode(ENCODE_TYPE)
    data.file_path = src
    data.file_size = len(fp_content)
    data.file_content = fp_content
    data.out_bytes = create_header(data.file_name, data.file_size,
                                   data.connection_id, OP_CODE_UPLOAD,
                                   CHUNK_SIZE)
    data.out_bytes += data.file_content

    while True:
        if data.out_bytes:
            try:
                print("sending {} bytes ({} remaining) to connection {}"
                      .format(CHUNK_SIZE, len(data.out_bytes),
                              data.connection_id))
                sent = sock.send(data.out_bytes[0:CHUNK_SIZE])
                data.out_bytes = data.out_bytes[sent:]
            except BlockingIOError:
                pass
        else:
            print("Successfully sent file {} to server. Closing connection"
                  .format(data.file_name))
            sock.close()
            os._exit(0)
            return
