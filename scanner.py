from enum import Enum
from sys import argv

num_set = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
alphabet_set = {'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g', 'H', 'h', 'I', 'i', 'J', 'j', 'K',
                'k', 'L', 'l', 'M', 'm', 'N', 'n', 'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't', 'U', 'u',
                'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z'}
keywords_set = {'if', 'else', 'return', 'break', 'until', 'repeat', 'int', 'void'}
symbols_set = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<'}
comment_set = {'/*', '//'}
whitespaces_set = {' ', '\n', '\r', '\t', '\v', '\f'}


# general pattern
def scan_for_num(c: str) -> (str, bool, str):
    pass


def scan_for_id_keyword(c: str, f) -> (str, bool, str):
    return c


def scan_for_symbol(c: str) -> (str, bool, str):
    return c


def scan_comment(c: str) -> (str, bool, str):
    return c


def scan_for_whitespace(c: str) -> (str, bool, str):
    return c


class TokenType(Enum):
    # id, initial_set, vocabulary, scan_func
    NUM = (1, num_set, num_set, scan_for_num),
    ID = (2, alphabet_set, alphabet_set.union(num_set), scan_for_id_keyword),
    KEYWORD = (3, alphabet_set, keywords_set, scan_for_id_keyword),
    SYMBOL = (4, symbols_set, symbols_set, scan_for_symbol),
    COMMENT = (5, {'/'}, comment_set, scan_comment),
    WHITESPACE = (6, whitespaces_set, whitespaces_set, scan_for_whitespace)
    EOF = (7, {}, {})


_cur_seq = ""
_remained_char = None


# TODO decide for handling errors (can it be done in get_next_token or it has to be done in scan methods?)
def get_next_token(file) -> (bool, Enum, str):
    global _cur_seq, _remained_char
    # todo handle remained char here
    c = file.read(1)  # initial character
    if not c:
        return True, TokenType.EOF, ""

    for token_type in TokenType:
        initial_set = token_type.value[1]
        if c in initial_set:
            scan_func = token_type.value[3]
            # scan function is reading, token accepted, result token(if accepted), extra char
            read, accepted, seq, _remained_char = scan_func(c)
            while read:
                _cur_seq += c
                if accepted:
                    return False, token_type, seq
                c = file.read(1)
                if not c:
                    return True, TokenType.EOF, ""
                read, accepted, seq, _remained_char = scan_func(c)


def dprint(*string):  # debug print
    global DEBUG
    if DEBUG:
        print(*string)


file_name = argv[1]
line_idx = 1
DEBUG = False


def __main__():
    global DEBUG
    if len(argv) >= 3:
        DEBUG = bool(argv[2])
    with open(file_name, 'r') as f, open('tokens.txt', 'w') as tokens_file, \
            open('lexical_errors.txt', 'w') as errors_file, open('symbol_table.txt', 'w') as symbol_table_file:
        while True:
            eof, token, seq = get_next_token(f)
            if not eof:
                # todo handle remained char
                #
                tokens_file.write(str((token, seq)) + ',')
                if token is TokenType.KEYWORD or token is TokenType.ID:
                    symbol_table_file.write(seq + ',\n')
            else:
                dprint("End of compilation.")
                break
