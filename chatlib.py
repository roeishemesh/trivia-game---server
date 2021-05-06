# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names

command_list = ['ERROR', 'HIGHSCORE', 'LOGOUT', 'GET_QUESTION', 'NEW_USER', 'WRONG_ANSWER', 'ALL_SCORE', 'YOUR_SCORE',
                'USERS_LIST', 'LOGIN', 'YOUR_QUESTION', 'SEND_ANSWER', 'MY_SCORE', 'LOGIN_OK', 'NO_QUESTIONS', 'LOGGED',
                'CORRECT_ANSWER', "END_QUESTION","END_GAME","BEST_SCORE","YOUR_BEST_SCORE"]

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
    """
    Gets command name (str) and data field (str) and creates a valid protocol message
    Returns: str, or None if error occured
    """
    if cmd in command_list and 0 <= len(data) <= 9999:
        full_cmd = cmd + "                "
        full_msg_list = [full_cmd[:16], str(len(data)).zfill(4), data]
        full_msg = DELIMITER.join(full_msg_list)
        return full_msg


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    data_list = data.split(DELIMITER)
    if len(data_list) == 3:
        cmd = data_list[0].strip(" ")
        msg = data_list[-1]
        if data_list[1].strip().isalpha() is True:
            return None, None
        if cmd in command_list and 0 <= len(msg) <= 9999 and int(data_list[1].strip()) == len(msg):
            return cmd, msg
        else:
            return None, None
    else:
        return None, None


def split_data(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's data field delimiter (|#) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    msg_delimiter_num = msg.count(DATA_DELIMITER)
    if msg_delimiter_num == expected_fields:
        return msg_delimiter_num + 1
    else:
        return None


def join_data(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter.
    Returns: string that looks like cell1#cell2#cell3
    """
    string_message = ""
    for i in msg_fields:
        string_message += str(i) + DATA_DELIMITER
    return string_message[:-1]
