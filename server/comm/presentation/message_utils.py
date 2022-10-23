CLEAR = 0
LOG_TEXT = 1
JSON_DATA = 2
GET_FILES_REQUEST = 3
FLASH_REQUEST = 4

HEADER_LEN = {
    LOG_TEXT: 5,
    JSON_DATA: 5,
    GET_FILES_REQUEST: 5,
    CLEAR: 5,
    FLASH_REQUEST: 5,
}


def prep_message(message, type):
    byte_message = type.to_bytes(1, byteorder='big')
    byte_message += (HEADER_LEN[type] + len(message)).to_bytes(4, byteorder='big')
    # ...

    byte_message += message
    return byte_message
