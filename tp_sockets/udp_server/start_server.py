import sys
import errno
import os
import socket

from constants import (OP_CODE_DOWNLOAD, OP_CODE_UPLOAD,
                       RESP_CODE_FILE_DOWNLOAD, RESP_CODE_FILE_UPLOAD)
from common_functions import (default_file_transfer_data, create_header,
                              parse_header)


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
        # sock.listen(10)
        sock.setblocking(True)

        while True:
            data = default_file_transfer_data()
            data.storage_dir = storage_dir

            if not parse_header(data, sock):
                print("Error while reading header: {}".format(data))
                sock.close()
                return False
            else:
                # print("Header read {}".format(data))
                if data.operation == OP_CODE_DOWNLOAD:
                    try:
                        file = open(os.path.join(data.storage_dir,
                                    data.file_name), 'rb')
                        file_content = file.read()
                        file.close()
                        data.file_content = file_content
                        header = create_header(data.file_name,
                                               len(file_content),
                                               data.connection_id,
                                               RESP_CODE_FILE_UPLOAD)
                        data.outb += header + file_content
                    except Exception as e:
                        data.outb += create_header(data.file_name, -1,
                                                   data.connection_id,
                                                   RESP_CODE_FILE_DOWNLOAD, -1,
                                                   str(e))
                        print("Error while trying to read \
                               requested file {}: {}"
                              .format(data.file_name, str(e)))

            while True:
                if data.operation == OP_CODE_UPLOAD:
                    if data.processed_total < data.file_size:
                        chunk_size = data.variable
                        try:
                            recv_data = sock.recv(chunk_size)
                            if recv_data:
                                print('Received {} [{}/{}] from {}'
                                      .format(len(recv_data),
                                              data.processed_total,
                                              data.file_size, data.addr))
                                data.file_content += recv_data
                                data.processed_total += len(recv_data)
                            else:
                                print("Closing connection to {}"
                                      .format(data.addr))
                                sock.close()
                                return
                        except IOError as e:  # and here it is handled
                            if e.errno == errno.EWOULDBLOCK:
                                pass
                    if data.processed_total >= data.file_size:
                        # File received successfully. Save to disk
                        print("Received all the file {} on connection {}"
                              .format(data.file_name, data.connid))
                        file = open(os.path.join(data.storage_dir,
                                    data.file_name), 'wb')
                        file_content = file.write(data.file_content)
                        file.close()
                        sock.close()
                        return

                if data.outb:
                    # Send whatever is on the output buffer.
                    chunk_size = data.variable
                    try:
                        sent = sock.send(data.outb[:chunk_size])
                    except BrokenPipeError as e:
                        print("Client closed connection unexpectedly ({})"
                              .format(e))
                        break
                    if sent:
                        print("Sent data to client {} bytes"
                              .format(sent if sent else 0))
                    data.outb = data.outb[sent:]
                elif data.operation == OP_CODE_DOWNLOAD:
                    # Sent all the data in buffer already.
                    break
            try:
                sock.close()
            except Exception as e1:
                print("Error while trying to close the client connection ({})"
                      .format(e1))

    except KeyboardInterrupt:
        print("Closing server after interrupt signal...")
        sock.close()
        sys.exit()
