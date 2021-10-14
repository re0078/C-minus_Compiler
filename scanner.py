from sys import argv
from element_types import *

_cur_seq = ""
_remained_char = None
_cur_state_order = 0
_keyword_flag = False
_asterisk_flag = False


def flush():
    global _cur_seq, _remained_char, _cur_state_order, _keyword_flag
    _cur_seq = ""
    _remained_char = None
    _cur_state_order = 0
    _keyword_flag = False


def scan_process(c: str, token_type: TokenType) -> (bool, bool):
    global _cur_state_order
    cur_state = token_type.get_state(_cur_state_order)
    if token_type == TokenType.ID and _cur_seq in TokenType.KEYWORD.get_state(_cur_state_order).valid_set:
        _keyword_flag = True
    else:
        _keyword_flag = False
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


def send_error():
    pass


# TODO decide for handling errors (can it be done in get_next_token or it has to be done in scan methods?)
def get_next_token(file) -> (bool, Enum, str):
    global _cur_seq, _remained_char, _asterisk_flag
    # todo handle remained char here
    c = file.read(1)  # initial character
    if not c:
        return True, TokenType.EOF, ""

    for token_type in TokenType:
        # scan function is reading, token accepted, result token(if accepted), extra char
        flush()
        read, accepted = scan_process(c, token_type)
        while read:
            _cur_seq += c
            if accepted:
                return False, token_type, _cur_seq
            c = file.read(1)
            if not c:
                return True, TokenType.EOF, ""
            read, accepted = scan_process(c, token_type)
        if c == asterisk_set:
            _asterisk_flag = True
        if _asterisk_flag and c == comment_set:
            send_error()
        if _keyword_flag:
            handle_keyword(_cur_seq)


def dprint(*string):  # debug print
    global DEBUG
    if DEBUG:
        print(*string)


# file_name = argv[1]
line_idx = 1
DEBUG = False


def __main__():
    global DEBUG
    if len(argv) >= 3:
        DEBUG = bool(argv[2])
    # with open(file_name, 'r') as f, open('tokens.txt', 'w') as tokens_file, \
    #         open('lexical_errors.txt', 'w') as errors_file, open('symbol_table.txt', 'w') as symbol_table_file:
    #     while True:
    #         eof, token, seq = get_next_token(f)
    #         if not eof:
    #             # todo handle remained char
    #             #
    #             tokens_file.write(str((token, seq)) + ',')
    #             if token is TokenType.KEYWORD or token is TokenType.ID:
    #                 symbol_table_file.write(seq + ',\n')
    #         else:
    #             dprint("End of compilation.")
    #             break
