from sys import argv

from element_types import *
from error_type import *

_cur_seq = ""
_remained_char = None
_cur_state_order = 0
_asterisk_flag = False
_found_error = False


def flush():
    global _cur_seq, _remained_char, _cur_state_order
    _cur_seq = ""
    _remained_char = None
    _cur_state_order = 0


def scan_process(c: str, token_type: TokenType) -> (bool, bool):
    global _cur_seq, _remained_char, _cur_state_order
    cur_state = token_type.get_state(_cur_state_order)
    if c in cur_state.valid_set:
        if cur_state.ends:
            return False, True
        if cur_state.repeatable:
            return True, True
        _cur_state_order += 1
        return True, True
    elif c in cur_state.universal_set:
        if cur_state.otherwise_state is None:
            if cur_state.ends:
                return False, True
            else:
                raise Exception(f"Invalid State transition. {_cur_seq}-{token_type}-{_cur_state_order}")
        _cur_state_order = cur_state.otherwise_state
        return True, True
    else:
        if cur_state.repeatable:
            _remained_char = c
            return False, True
        else:
            return False, False


def handle_keyword(keyword: str):
    pass


def send_error(error: ErrorType, seq, file):
    global line_idx, _found_error
    error.write_to_file(file, seq, line_idx)
    _found_error = True


# todo make sure to handle _remained_char while facing errors
def get_next_token(file, error_file) -> (bool, Enum, str):
    global _cur_seq, _remained_char, _asterisk_flag, line_idx, _found_error

    def get_accepted_token(token):
        global _cur_seq
        if (token is TokenType.ID) and (_cur_seq in keywords_set):
            return False, TokenType.KEYWORD, _cur_seq
        return False, token, _cur_seq

    """initial character"""
    c = _remained_char if _remained_char else file.read(1)
    if not c:
        return True, TokenType.EOF, ""
    _asterisk_flag = False
    if c in asterisk_set:
        _asterisk_flag = True

    token_accepted = False
    for token_type in list(TokenType)[:-2]:
        flush()
        """ scan function is reading, token accepted """
        read, accepted = scan_process(c, token_type)
        if _asterisk_flag:
            read = True
        elif accepted:
            return get_accepted_token(token_type)
        while read:
            token_accepted = True
            _cur_seq += c
            c = file.read(1)
            if not c:
                if accepted:
                    return get_accepted_token(token_type)
                return True, TokenType.EOF, ""
            read, accepted = scan_process(c, token_type)
        if _asterisk_flag and c in comment_set:
            _remained_char = c
            send_error(ErrorType.UNMATCHED_COMMENT, _cur_seq[:7], error_file)
            # todo return sth
        elif _asterisk_flag:
            return False, TokenType.SYMBOL
        if not token_accepted:
            send_error(ErrorType.INVALID_INPUT, _cur_seq, error_file)
            # todo return sth
        if accepted:
            return get_accepted_token(token_type)
        else:
            if token_type is TokenType.COMMENT:
                send_error(ErrorType.UNCLOSED_COMMENT, _cur_seq[:7], error_file)
            if token_type is TokenType.NUM:
                send_error(ErrorType.INVALID_NUMBER, _cur_seq + str(_remained_char), error_file)
            # todo return sth


def dprint(*string):  # debug print
    global DEBUG
    if DEBUG:
        print(*string)


file_name = argv[1]
line_idx = 1
DEBUG = False


def __main__():
    global DEBUG, line_idx, _found_error
    if len(argv) >= 3:
        DEBUG = bool(argv[2])
    _found_error = False
    with open(file_name, 'r') as f, open('tokens.txt', 'w') as tokens_file, \
            open('lexical_errors.txt', 'w') as errors_file, open('symbol_table.txt', 'w') as symbol_table_file:
        while True:
            eof, token = get_next_token(f, errors_file)
            if not eof:
                if token is TokenType.WHITESPACE and _cur_seq == "\n":
                    line_idx += 1
                if token is TokenType.WHITESPACE or token is TokenType.COMMENT:
                    continue
                tokens_file.write(str((token, _cur_seq)) + ',')
                if token is TokenType.KEYWORD or token is TokenType.ID:
                    symbol_table_file.write(_cur_seq + ',\n')
            else:
                dprint("End of compilation.")
                if not _found_error:
                    errors_file.write("There is no lexical error.")
                break
