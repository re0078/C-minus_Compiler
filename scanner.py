from enum import Enum
import re as regex


class TokenType(Enum):
    NUM = (1, regex.compile("^[0-9]+$")),
    ID = (2, regex.compile("^[A-Za-z][A-Za-z0-9]*$")),
    KEYWORD = (3, regex.compile("^(if|else|void|int|repeat|break|until|return)$")),
    SYMBOL = (4, regex.compile("^([;:,\[\]{}()*+\-<]+|=|==)$")),
    COMMENT = (5, regex.compile("^(/\*(\n|.)*\*/|//.*\n?)$")),
    WHITESPACE = (6, regex.compile("(\s\n\r\t\v\f)"))


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
