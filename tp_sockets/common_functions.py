import types
from constants import (ENCODE_TYPE, OP_CODE_UPLOAD, OP_CODE_DOWNLOAD,
                       OP_CODE_DOWNLOAD_RESP, OP_CODE_UPLOAD_RESP)


def default_file_transfer_data():
    return types.SimpleNamespace(
        connection_id=0,
        address='',
        op_code=0,
        header_sent=False,
        header_read=False,
        file_name=''.encode(ENCODE_TYPE),
        file_path=''.encode(ENCODE_TYPE),
        file_size=0,
        file_content="".encode(ENCODE_TYPE),
        total_processed=0,
        dest_dir='',
        variable=0,
        error_code='',
        in_bytes="".encode(ENCODE_TYPE),
        out_bytes="".encode(ENCODE_TYPE)
    )

# Reliable UDP header will have this look:
# op_code|file_name_size|file_name|file_size|connection_id|error


def create_header(name, size, connection_id, op_code, chunk_size, error=None):
    err = 0 if not error else error
    return "{}|{}|{}|{}|{}|{}".format(op_code, len(name), name, size,
                                      connection_id, err).encode(ENCODE_TYPE)


def parse_header(data, sock):
    received_data = sock.recv(5)
    if not received_data:
        print("Error parsing header from {}".format(data.address))
        return False
    fields = received_data.decode(ENCODE_TYPE).split("|")
    print(fields)
    op_code = int(fields[0])
    print("op code is {}".format(op_code))
    if not op_code_is_valid(op_code):
        print("Incorrect operation code received")
        return False
    data.op_code = op_code
    file_name_length = int(fields[1])
    if file_name_length == 0:
        print("Invalid file name length from {}".format(data.address))
        return False
    received_data = sock.recv(file_name_length)
    if not received_data:
        print("Erro reading file from {}".format(data.address))
        return False
    data.file_name = received_data.decode('utf8')  # TODO: Check this line
    received_data = sock.recv(4)
    if not received_data:
        print("Error reading file size from {}".format(data.address))
        return False
    data.file_size = fields[3]
    received_data = sock.recv(4)
    if not received_data:
        print("Error reading connection ID from {}".format(data.address))
        return False
    data.connection_id = fields[4]
    received_data = sock.recv(4)
    if not received_data:
        print("Error reading error variable from {}".format(data.addr))
        return False
    data.error = fields[5]
    if data.error == 0:
        print("Received 0 length on error from {} ".format(data.addr))
    else:
        received_data = sock.recv(data.error)
        if not received_data:
            print("Error reading error field (should be {})"
                  .format(data.error))
            return False
        data.error = received_data.decode('utf8')
    data.header_read = True
    print("Successfully parsed header!")
    return True


def op_code_is_valid(op_code):
    return op_code in (OP_CODE_DOWNLOAD, OP_CODE_UPLOAD,
                       OP_CODE_UPLOAD_RESP, OP_CODE_DOWNLOAD_RESP)
