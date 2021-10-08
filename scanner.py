from enum import Enum

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


def get_next_token(seq: str) -> (Enum, str):
    return


def parse_num(seq: str):
    return seq


def parse_id(seq: str):
    return seq


def parse_keyword(seq: str):
    return seq


def parse_symbol(seq: str):
    return seq


def parse_comment(seq: str):
    return seq


def parse_whitespace(seq: str):
    return seq
