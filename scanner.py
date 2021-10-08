from enum import Enum
from sys import argv

num_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
alphanum_set = ['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g', 'H', 'h', 'I', 'i', 'J', 'j', 'K',
                'k', 'L', 'l', 'M', 'm', 'N', 'n', 'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't', 'U', 'u',
                'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z'] + num_set
keywords_set = ['if', 'else', 'return', 'break', 'until', 'repeat', 'int', 'void']
symbols_set = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<']
comment_set = ['/*', '//']
whitespaces_set = [' ', '\n', '\r', '\t', '\v', '\f']


class TokenType(Enum):
    NUM = (1, num_set),
    ID = (2, alphanum_set),
    KEYWORD = (3, keywords_set),
    SYMBOL = (4, symbols_set),
    COMMENT = (5, comment_set),
    WHITESPACE = (6, whitespaces_set)
    EOF = (7, [])


cur_seq = ""
remained_char = None


# TODO decide for handling errors (can it be done in get_next_token or it has to be done in scan methods?)
def get_next_token(file) -> (bool, Enum, str):
    global remained_char
    c = file.read(1)  # initial character
    if not c:
        return True, TokenType.EOF, ""

    #  TODO switch-case like logic
    # seq, accepted, remained_char = scan_comment(c, f)


# general pattern
def scan_for_num(initial_char: str, f) -> (str, bool, str):
    while True:
        c = f.read(1)
    pass


def scan_for_id_keyword(seq: str) -> (str, bool, str):
    return seq


def scan_for_symbol(seq: str) -> (str, bool, str):
    return seq


def scan_comment(seq: str) -> (str, bool, str):
    return seq


def scan_for_whitespace(seq: str) -> (str, bool, str):
    return seq


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
                tokens_file.write(str((token, seq)) + ',')
                if token is TokenType.KEYWORD or token is TokenType.ID:
                    symbol_table_file.write(seq + ',\n')
            else:
                dprint("End of compilation.")
