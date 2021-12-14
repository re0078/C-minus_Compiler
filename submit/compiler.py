import math

from enum import Enum
from typing import Optional

num_set = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
alphabet_set = {'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g', 'H', 'h', 'I', 'i', 'J', 'j', 'K',
                'k', 'L', 'l', 'M', 'm', 'N', 'n', 'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't', 'U', 'u',
                'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z'}
alphanumeric_set = alphabet_set.union(num_set)
keywords_list = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return', 'endif']
asterisk_dict = {'*': 'asterisk'}
asterisk_set = {sym for sym in asterisk_dict.keys()}
symbols_dict = {';': 'semicolon', ':': 'colon', ',': 'comma', '[': 'bracket_open', ']': 'bracket_close',
                '(': 'parenthesis_open', ')': 'parenthesis_close', '{': 'brace_open', '}': 'brace_close', '+': 'plus',
                '-': 'minus', '<': 'less', "*": "asterisk"}
symbols_set = {sym for sym in symbols_dict.keys()}
equal_char_set = {'='}
comment_set = {'/'}
next_line_set = {'\n'}
whitespaces_set = {' ', '\r', '\t', '\v', '\f'}.union(next_line_set)
empty_set = set()
valid_chars_set = alphanumeric_set.union(symbols_set).union(equal_char_set) \
    .union(comment_set).union(whitespaces_set).union(asterisk_set)
other_chars = set("!@#$%^&_}{?>|':;,.").union(set('"'))


class ScanerErrorType(Enum):
    INVALID_INPUT = "Invalid input"
    UNCLOSED_COMMENT = "Unclosed comment"
    UNMATCHED_COMMENT = "Unmatched comment"
    INVALID_NUMBER = "Invalid number"

    def write_to_file(self, file, seq, lineno, new_line):
        if new_line:
            file.write(f"{lineno}.\t({seq}, {self.value})")
        else:
            file.write(f" ({seq}, {self.value})")


class ParserErrorType(Enum):
    MISSING = "missing"
    ILLEGAL = "illegal"
    UNEXPECTED = "Unexpected"


class ScanState:
    def __init__(self, valid_set: set, ends: bool, repeatable: bool = False, otherwise_state: int = None,
                 universal_set=None):
        if universal_set is None:
            universal_set = {}
        self.valid_set = valid_set
        self.ends = ends
        self.repeatable = repeatable
        self.otherwise_state = otherwise_state
        self.universal_set = universal_set

    def __repr__(self):
        base_str = "State\n\t* valid_set: " + str(self.valid_set) + "\n\t* repeatable: " + str(self.repeatable) + \
                   "\n\t* ends: " + str(self.ends) + "\n"
        if self.otherwise_state is not None:
            return base_str + "otherwise_state: " + str(self.otherwise_state) + "otherwise_set: " + str(
                self.universal_set)
        return base_str


class ScanTokenType(Enum):
    """ tuple of valid states """
    NUM = ScanState(num_set, ends=False, repeatable=False, otherwise_state=1, universal_set=num_set), \
          ScanState(num_set, ends=False, repeatable=True, universal_set=valid_chars_set - alphabet_set),
    ID = ScanState(alphabet_set, ends=False), ScanState(alphanumeric_set, ends=False, repeatable=True),
    SYMBOL = ScanState(symbols_set, ends=True, otherwise_state=1, universal_set=equal_char_set), \
             ScanState(equal_char_set, ends=True, universal_set=valid_chars_set),
    COMMENT = ScanState(comment_set, ends=False), \
              ScanState(asterisk_set, ends=False, otherwise_state=4, universal_set=comment_set), \
              ScanState(asterisk_set, ends=False, otherwise_state=2, universal_set=valid_chars_set.union(other_chars)), \
              ScanState(comment_set, ends=True, otherwise_state=2, universal_set=valid_chars_set.union(other_chars)), \
              ScanState(empty_set, ends=True, otherwise_state=4,
                        universal_set=(valid_chars_set - next_line_set).union(other_chars))
    WHITESPACE = ScanState(whitespaces_set, ends=True),
    KEYWORD = ScanState(keywords_list, ends=True, repeatable=False),
    EOF = (),
    ERROR = ()

    def get_state(self, state_order: int) -> ScanState:
        return self.value[state_order]

    def __str__(self):
        # todo rename asterisk
        name = self.name
        return '(' + name + ', {seq:s})'


class ParseTokenType(Enum):
    TERMINAL = 0,
    VARIABLE_TERMINAL = 1,
    NON_TERMINAL = 2,

    def __repr__(self):
        if self == ParseTokenType.TERMINAL:
            return "T"
        elif self == ParseTokenType.VARIABLE_TERMINAL:
            return "V"
        else:
            return "N"

    def __str__(self):
        return self.name


class ParseToken(Enum):
    EPSILON = (0, ParseTokenType.TERMINAL),
    PROGRAM = (1, ParseTokenType.NON_TERMINAL),
    DECLARATION_LIST = (2, ParseTokenType.NON_TERMINAL),
    DECLARATION = (3, ParseTokenType.NON_TERMINAL),
    DECLARATION_INITIAL = (4, ParseTokenType.NON_TERMINAL),
    DECLARATION_PRIME = (5, ParseTokenType.NON_TERMINAL),
    TYPE_SPECIFIER = (6, ParseTokenType.NON_TERMINAL),
    ID = (7, ParseTokenType.VARIABLE_TERMINAL),
    FUN_DECLARATION_PRIME = (8, ParseTokenType.NON_TERMINAL),
    VAR_DECLARATION_PRIME = (9, ParseTokenType.NON_TERMINAL),
    SEMICOLON = (10, ParseTokenType.TERMINAL),
    NUM = (11, ParseTokenType.VARIABLE_TERMINAL),
    PARENTHESIS_OPEN = (12, ParseTokenType.TERMINAL),
    PARENTHESIS_CLOSE = (13, ParseTokenType.TERMINAL),
    PARAMS = (14, ParseTokenType.NON_TERMINAL),
    COMPOUND_STMT = (15, ParseTokenType.NON_TERMINAL),
    INT = (16, ParseTokenType.TERMINAL),
    VOID = (17, ParseTokenType.TERMINAL),
    PARAM_PRIME = (18, ParseTokenType.NON_TERMINAL),
    PARAM_LIST = (19, ParseTokenType.NON_TERMINAL),
    COMMA = (20, ParseTokenType.TERMINAL),
    BRACKET_OPEN = (21, ParseTokenType.TERMINAL),
    BRACKET_CLOSE = (22, ParseTokenType.TERMINAL),
    BRACE_OPEN = (23, ParseTokenType.TERMINAL),
    BRACE_CLOSE = (24, ParseTokenType.TERMINAL),
    STATEMENT_LIST = (25, ParseTokenType.NON_TERMINAL),
    STATEMENT = (26, ParseTokenType.NON_TERMINAL),
    EXPRESSION_STMT = (27, ParseTokenType.NON_TERMINAL),
    SELECTION_STMT = (28, ParseTokenType.NON_TERMINAL),
    ITERATION_STMT = (29, ParseTokenType.NON_TERMINAL),
    RETURN_STMT = (30, ParseTokenType.NON_TERMINAL),
    EXPRESSION = (31, ParseTokenType.NON_TERMINAL),
    BREAK = (32, ParseTokenType.TERMINAL),
    IF = (33, ParseTokenType.TERMINAL),
    ELSE_STMT = (34, ParseTokenType.NON_TERMINAL),
    ENDIF = (35, ParseTokenType.TERMINAL),
    ELSE = (36, ParseTokenType.TERMINAL),
    REPEAT = (37, ParseTokenType.TERMINAL),
    UNTIL = (38, ParseTokenType.TERMINAL),
    RETURN = (39, ParseTokenType.TERMINAL),
    RETURN_STMT_PRIME = (40, ParseTokenType.NON_TERMINAL),
    SIMPLE_EXPRESSION_ZEGOND = (41, ParseTokenType.NON_TERMINAL),
    B = (42, ParseTokenType.NON_TERMINAL),
    H = (43, ParseTokenType.NON_TERMINAL),
    G = (44, ParseTokenType.NON_TERMINAL),
    D = (45, ParseTokenType.NON_TERMINAL),
    C = (46, ParseTokenType.NON_TERMINAL),
    ADDITIVE_EXPRESSION_ZEGOND = (47, ParseTokenType.NON_TERMINAL),
    ADDITIVE_EXPRESSION_PRIME = (48, ParseTokenType.NON_TERMINAL),
    RELOP = (49, ParseTokenType.NON_TERMINAL),
    ADDITIVE_EXPRESSION = (50, ParseTokenType.NON_TERMINAL),
    LESS = (51, ParseTokenType.TERMINAL),
    EQUALS = (52, ParseTokenType.TERMINAL),
    TERM = (53, ParseTokenType.NON_TERMINAL),
    TERM_PRIME = (54, ParseTokenType.NON_TERMINAL),
    TERM_ZEGOND = (55, ParseTokenType.NON_TERMINAL),
    ADDOP = (56, ParseTokenType.NON_TERMINAL),
    PLUS = (57, ParseTokenType.TERMINAL),
    MINUS = (58, ParseTokenType.TERMINAL),
    FACTOR = (59, ParseTokenType.NON_TERMINAL),
    FACTOR_PRIME = (60, ParseTokenType.NON_TERMINAL),
    FACTOR_ZEGOND = (61, ParseTokenType.NON_TERMINAL),
    ASTERISK = (62, ParseTokenType.TERMINAL),
    VAR_CALL_PRIME = (63, ParseTokenType.NON_TERMINAL),
    ARGS = (64, ParseTokenType.NON_TERMINAL),
    VAR_PRIME = (65, ParseTokenType.NON_TERMINAL),
    ARG_LIST = (66, ParseTokenType.NON_TERMINAL),
    ARG_LIST_PRIME = (67, ParseTokenType.NON_TERMINAL),
    DOLLAR = (68, ParseTokenType.TERMINAL),
    PARAM = (69, ParseTokenType.NON_TERMINAL),
    SIMPLE_EXPRESSION_PRIME = (70, ParseTokenType.NON_TERMINAL),
    IS = (71, ParseTokenType.TERMINAL),

    def get_type(self) -> ParseTokenType:
        return self.value[0][1]

    def __str__(self):
        if self == ParseToken.EPSILON:
            return 'epsilon'
        if self == ParseToken.DOLLAR:
            return '$'
        if self == ParseToken.ID:
            return 'ID'
        if self == ParseToken.NUM:
            return 'NUM'
        str_name = (self.name[0] + self.name[1:].lower()).replace('_', '-')
        return str_name

    def __repr__(self):
        return str(self)


class ParseRule(Enum):
    R1 = (ParseToken.PROGRAM, ((ParseToken.DECLARATION_LIST, ParseToken.DOLLAR),)),
    R2 = (ParseToken.DECLARATION_LIST, ((ParseToken.DECLARATION, ParseToken.DECLARATION_LIST), (ParseToken.EPSILON,))),
    R3 = (ParseToken.DECLARATION, ((ParseToken.DECLARATION_INITIAL, ParseToken.DECLARATION_PRIME),)),
    R4 = (ParseToken.DECLARATION_INITIAL, ((ParseToken.TYPE_SPECIFIER, ParseToken.ID),)),
    R5 = (ParseToken.DECLARATION_PRIME, ((ParseToken.FUN_DECLARATION_PRIME,), (ParseToken.VAR_DECLARATION_PRIME,))),
    R6 = (ParseToken.VAR_DECLARATION_PRIME, ((ParseToken.SEMICOLON,), (ParseToken.BRACKET_OPEN, ParseToken.NUM,
                                                                       ParseToken.BRACKET_CLOSE,
                                                                       ParseToken.SEMICOLON))),
    R7 = (ParseToken.FUN_DECLARATION_PRIME, ((ParseToken.PARENTHESIS_OPEN, ParseToken.PARAMS,
                                              ParseToken.PARENTHESIS_CLOSE, ParseToken.COMPOUND_STMT),)),
    R8 = (ParseToken.TYPE_SPECIFIER, ((ParseToken.INT,), (ParseToken.VOID,))),
    R9 = (ParseToken.PARAMS, ((ParseToken.INT, ParseToken.ID, ParseToken.PARAM_PRIME, ParseToken.PARAM_LIST),
                              (ParseToken.VOID,))),
    R10 = (ParseToken.PARAM_LIST, ((ParseToken.COMMA, ParseToken.PARAM, ParseToken.PARAM_LIST), (ParseToken.EPSILON,))),
    R11 = (ParseToken.PARAM, ((ParseToken.DECLARATION_INITIAL, ParseToken.PARAM_PRIME),)),
    R12 = (ParseToken.PARAM_PRIME, ((ParseToken.BRACKET_OPEN, ParseToken.BRACKET_CLOSE), (ParseToken.EPSILON,))),
    R13 = (ParseToken.COMPOUND_STMT, ((ParseToken.BRACE_OPEN, ParseToken.DECLARATION_LIST, ParseToken.STATEMENT_LIST,
                                       ParseToken.BRACE_CLOSE),)),
    R14 = (ParseToken.STATEMENT_LIST, ((ParseToken.STATEMENT, ParseToken.STATEMENT_LIST),
                                       (ParseToken.EPSILON,))),
    R15 = (ParseToken.STATEMENT, ((ParseToken.EXPRESSION_STMT,), (ParseToken.COMPOUND_STMT,),
                                  (ParseToken.SELECTION_STMT,), (ParseToken.ITERATION_STMT,),
                                  (ParseToken.RETURN_STMT,))),
    R16 = (ParseToken.EXPRESSION_STMT, ((ParseToken.EXPRESSION, ParseToken.SEMICOLON), (ParseToken.BREAK,
                                                                                        ParseToken.SEMICOLON),
                                        (ParseToken.SEMICOLON,))),
    R17 = (ParseToken.SELECTION_STMT, ((ParseToken.IF, ParseToken.PARENTHESIS_OPEN, ParseToken.EXPRESSION,
                                        ParseToken.PARENTHESIS_CLOSE, ParseToken.STATEMENT, ParseToken.ELSE_STMT),)),
    R18 = (ParseToken.ELSE_STMT, ((ParseToken.ENDIF,), (ParseToken.ELSE, ParseToken.STATEMENT, ParseToken.ENDIF),)),
    R19 = (ParseToken.ITERATION_STMT, ((ParseToken.REPEAT, ParseToken.STATEMENT, ParseToken.UNTIL,
                                        ParseToken.PARENTHESIS_OPEN, ParseToken.EXPRESSION,
                                        ParseToken.PARENTHESIS_CLOSE),)),
    R20 = (ParseToken.RETURN_STMT, ((ParseToken.RETURN, ParseToken.RETURN_STMT_PRIME),)),
    R21 = (ParseToken.RETURN_STMT_PRIME, ((ParseToken.SEMICOLON,), (ParseToken.EXPRESSION, ParseToken.SEMICOLON))),
    R22 = (ParseToken.EXPRESSION, ((ParseToken.SIMPLE_EXPRESSION_ZEGOND,), (ParseToken.ID, ParseToken.B),)),
    R23 = (ParseToken.B, ((ParseToken.IS, ParseToken.EXPRESSION), (ParseToken.BRACKET_OPEN, ParseToken.EXPRESSION,
                                                                   ParseToken.BRACKET_CLOSE, ParseToken.H),
                          (ParseToken.SIMPLE_EXPRESSION_PRIME,))),
    R24 = (ParseToken.H, ((ParseToken.IS, ParseToken.EXPRESSION), (ParseToken.G, ParseToken.D, ParseToken.C))),
    R25 = (ParseToken.SIMPLE_EXPRESSION_ZEGOND, ((ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ParseToken.C),)),
    R26 = (ParseToken.SIMPLE_EXPRESSION_PRIME, ((ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.C),)),
    R27 = (ParseToken.C, ((ParseToken.RELOP, ParseToken.ADDITIVE_EXPRESSION), (ParseToken.EPSILON,))),
    R28 = (ParseToken.RELOP, ((ParseToken.LESS,), (ParseToken.EQUALS,))),
    R29 = (ParseToken.ADDITIVE_EXPRESSION, ((ParseToken.TERM, ParseToken.D),)),
    R30 = (ParseToken.ADDITIVE_EXPRESSION_PRIME, ((ParseToken.TERM_PRIME, ParseToken.D),)),
    R31 = (ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ((ParseToken.TERM_ZEGOND, ParseToken.D),)),
    R32 = (ParseToken.D, ((ParseToken.ADDOP, ParseToken.TERM, ParseToken.D), (ParseToken.EPSILON,))),
    R33 = (ParseToken.ADDOP, ((ParseToken.PLUS,), (ParseToken.MINUS,))),
    R34 = (ParseToken.TERM, ((ParseToken.FACTOR, ParseToken.G),)),
    R35 = (ParseToken.TERM_PRIME, ((ParseToken.FACTOR_PRIME, ParseToken.G),)),
    R36 = (ParseToken.TERM_ZEGOND, ((ParseToken.FACTOR_ZEGOND, ParseToken.G),)),
    R37 = (ParseToken.G, ((ParseToken.ASTERISK, ParseToken.FACTOR, ParseToken.G), (ParseToken.EPSILON,))),
    R38 = (ParseToken.FACTOR, ((ParseToken.PARENTHESIS_OPEN, ParseToken.EXPRESSION, ParseToken.PARENTHESIS_CLOSE),
                               (ParseToken.ID, ParseToken.VAR_CALL_PRIME), (ParseToken.NUM,))),
    R39 = (ParseToken.VAR_CALL_PRIME, ((ParseToken.PARENTHESIS_OPEN, ParseToken.ARGS, ParseToken.PARENTHESIS_CLOSE),
                                       (ParseToken.VAR_PRIME,))),
    R40 = (ParseToken.VAR_PRIME, ((ParseToken.BRACE_OPEN, ParseToken.EXPRESSION, ParseToken.BRACKET_CLOSE),
                                  (ParseToken.EPSILON,))),
    R41 = (ParseToken.FACTOR_PRIME, ((ParseToken.PARENTHESIS_OPEN, ParseToken.ARGS, ParseToken.PARENTHESIS_CLOSE),
                                     (ParseToken.EPSILON,))),
    R42 = (
              ParseToken.FACTOR_ZEGOND,
              ((ParseToken.PARENTHESIS_OPEN, ParseToken.EXPRESSION, ParseToken.PARENTHESIS_CLOSE),
               (ParseToken.NUM,))),
    R43 = (ParseToken.ARGS, ((ParseToken.ARG_LIST,), (ParseToken.EPSILON,),)),
    R44 = (ParseToken.ARG_LIST, ((ParseToken.EXPRESSION, ParseToken.ARG_LIST_PRIME),)),
    R45 = (ParseToken.ARG_LIST_PRIME, ((ParseToken.COMMA, ParseToken.EXPRESSION, ParseToken.ARG_LIST_PRIME),
                                       (ParseToken.EPSILON,))),

    def get_prods(self) -> tuple:
        return self.value[0][1]

    def get_token(self) -> ParseToken:
        return self.value[0][0]

    def __str__(self):
        ret_str = f"{self.get_token().name} -> "
        for prod in self.get_prods():
            token: ParseToken
            for token in prod:
                if token.get_type() == ParseTokenType.NON_TERMINAL:
                    ret_str += f"{token.name}"
                else:
                    ret_str += f"{token.name.lower()}"
                ret_str += " "
            ret_str += "| "
        return ret_str[:-2]

    def __repr__(self):
        return self.__str__()


def find_rule_by_token(token: ParseToken) -> Optional[ParseRule]:
    rule: ParseRule
    for rule in ParseRule:
        if rule.value[0][0] == token:
            return rule
    return None


def get_parse_token_for_seq(seq: str, scan_token: ScanTokenType) -> Optional[ParseToken]:
    token: ParseToken
    if scan_token == ScanTokenType.KEYWORD:
        for token in ParseToken:
            if token.name.lower() == seq:
                return token
    elif scan_token == ScanTokenType.ID:
        return ParseToken.ID
    elif scan_token == ScanTokenType.NUM:
        return ParseToken.NUM
    elif scan_token == ScanTokenType.SYMBOL:
        if seq[0] in equal_char_set:
            if len(seq) == 1:
                return ParseToken.IS
            else:
                return ParseToken.EQUALS
        for token in ParseToken:
            if token.name.lower() == symbols_dict[seq]:
                return token
    elif scan_token == ScanTokenType.EOF:
        return ParseToken.DOLLAR


_cur_seq = ""
_remained_char = ""
_cur_state_order = 0
_token_type_determined = False


def flush():
    global _cur_seq, _remained_char, _cur_state_order, _token_type_determined
    _cur_seq = ""
    _remained_char = ""
    _cur_state_order = 0
    _token_type_determined = False


def scan_process(c: str, token_type: ScanTokenType) -> (bool, bool):
    global _cur_seq, _remained_char, _cur_state_order, _token_type_determined
    if _token_type_determined and (token_type is ScanTokenType.COMMENT):
        if c not in valid_chars_set.union(other_chars):
            _remained_char = c
            return False, False
    elif c not in valid_chars_set:
        _remained_char = c
        return False, False
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
            _remained_char = c
            if cur_state.ends:
                return False, True
            else:
                return False, True
        _cur_state_order = cur_state.otherwise_state
        if cur_state.ends:
            return True, True
        else:
            return True, False
    else:
        if _token_type_determined:
            _remained_char = c
            if cur_state.repeatable:
                if len(cur_state.universal_set) != 0:
                    return False, False
                return False, True
            if cur_state.valid_set == empty_set:
                return False, True
            return False, False
        else:
            _remained_char = c
            return False, False


def get_next_token(file) -> (bool, ScanTokenType, ScanerErrorType, str, str):
    global _cur_seq, _remained_char, _token_type_determined

    def look_ahead(file, is_asterisk: bool) -> (bool, ScanerErrorType):
        global _cur_seq, _remained_char
        look_ahead_c = file.read(1)
        if not look_ahead_c:
            return True, None
        if look_ahead_c not in valid_chars_set:
            _cur_seq += look_ahead_c
            return False, ScanerErrorType.INVALID_INPUT
        if is_asterisk:
            if look_ahead_c in comment_set:
                _cur_seq += look_ahead_c
                return False, ScanerErrorType.UNMATCHED_COMMENT
            _remained_char = look_ahead_c
            return False, None
        else:
            file.seek(file.tell() - 1, 0)
            if look_ahead_c in asterisk_set.union(comment_set):
                return False, None
            if look_ahead_c in valid_chars_set:
                return False, ScanerErrorType.INVALID_INPUT

    def get_accepted_token(token_type):
        global _cur_seq
        if (token_type is ScanTokenType.ID) and (_cur_seq in keywords_list):
            return False, ScanTokenType.KEYWORD, None, _cur_seq, _remained_char
        return False, token_type, None, _cur_seq, _remained_char

    """initial character"""
    c = _remained_char if len(_remained_char) != 0 else file.read(1)
    if not c:
        return True, ScanTokenType.EOF, None, _cur_seq, _remained_char
    if c in asterisk_set:
        flush()
        _cur_seq += c
        look_ahead_eof, look_ahead_err = look_ahead(file, True)
        if look_ahead_err is None:
            return look_ahead_eof, ScanTokenType.SYMBOL, None, _cur_seq, _remained_char
        return look_ahead_eof, ScanTokenType.ERROR, look_ahead_err, _cur_seq, _remained_char

    if c in comment_set:
        flush()
        _cur_seq += c
        look_ahead_eof, look_ahead_err = look_ahead(file, False)
        if look_ahead_err is not None:
            return look_ahead_eof, ScanTokenType.ERROR, look_ahead_err, _cur_seq, _remained_char

    for token_type in list(ScanTokenType)[:-3]:
        flush()
        read, accepted = scan_process(c, token_type)
        if accepted:
            _token_type_determined = True
            _cur_seq += c
        else:
            continue
        while read:
            """ scan function is reading, token accepted """
            c = file.read(1)
            if not c:
                if accepted:
                    return get_accepted_token(token_type)
                return True, ScanTokenType.ERROR, ScanerErrorType.UNCLOSED_COMMENT, _cur_seq, _remained_char
            read, accepted = scan_process(c, token_type)
            _cur_seq += c
        if _token_type_determined:
            _cur_seq = _cur_seq[0:len(_cur_seq) - len(_remained_char)]
            if accepted:
                return get_accepted_token(token_type)
            else:
                if token_type is ScanTokenType.NUM:
                    return False, ScanTokenType.ERROR, ScanerErrorType.INVALID_NUMBER, _cur_seq, _remained_char
                return False, ScanTokenType.ERROR, ScanerErrorType.INVALID_INPUT, _cur_seq, _remained_char
    return False, ScanTokenType.ERROR, ScanerErrorType.INVALID_INPUT, _cur_seq, _remained_char


parse_table = {
    (ParseToken.PROGRAM, ParseToken.INT): ParseRule.R1.get_prods()[0],
    (ParseToken.PROGRAM, ParseToken.VOID): ParseRule.R1.get_prods()[0],

    (ParseToken.DECLARATION_LIST, ParseToken.INT): ParseRule.R2.get_prods()[0],
    (ParseToken.DECLARATION_LIST, ParseToken.VOID): ParseRule.R2.get_prods()[0],

    (ParseToken.DECLARATION, ParseToken.INT): ParseRule.R3.get_prods()[0],
    (ParseToken.DECLARATION, ParseToken.VOID): ParseRule.R3.get_prods()[0],

    (ParseToken.DECLARATION_INITIAL, ParseToken.INT): ParseRule.R4.get_prods()[0],
    (ParseToken.DECLARATION_INITIAL, ParseToken.VOID): ParseRule.R4.get_prods()[0],

    (ParseToken.DECLARATION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R5.get_prods()[0],
    (ParseToken.DECLARATION_PRIME, ParseToken.SEMICOLON): ParseRule.R5.get_prods()[1],
    (ParseToken.DECLARATION_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R5.get_prods()[1],

    (ParseToken.VAR_DECLARATION_PRIME, ParseToken.SEMICOLON): ParseRule.R6.get_prods()[0],
    (ParseToken.VAR_DECLARATION_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R6.get_prods()[1],

    (ParseToken.FUN_DECLARATION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R7.get_prods()[0],

    (ParseToken.TYPE_SPECIFIER, ParseToken.INT): ParseRule.R8.get_prods()[0],
    (ParseToken.TYPE_SPECIFIER, ParseToken.VOID): ParseRule.R8.get_prods()[1],

    (ParseToken.PARAMS, ParseToken.INT): ParseRule.R9.get_prods()[0],
    (ParseToken.PARAMS, ParseToken.VOID): ParseRule.R9.get_prods()[1],

    (ParseToken.PARAM_LIST, ParseToken.COMMA): ParseRule.R10.get_prods()[0],

    (ParseToken.PARAM, ParseToken.INT): ParseRule.R11.get_prods()[0],
    (ParseToken.PARAM, ParseToken.VOID): ParseRule.R11.get_prods()[0],

    (ParseToken.PARAM_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R12.get_prods()[0],

    (ParseToken.COMPOUND_STMT, ParseToken.BRACE_OPEN): ParseRule.R13.get_prods()[0],

    (ParseToken.STATEMENT_LIST, ParseToken.BREAK): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.SEMICOLON): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.ID): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.PARENTHESIS_OPEN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.NUM): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.IF): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.RETURN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.BRACE_OPEN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.REPEAT): ParseRule.R14.get_prods()[0],

    (ParseToken.STATEMENT, ParseToken.BREAK): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.SEMICOLON): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.ID): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.PARENTHESIS_OPEN): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.NUM): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.BRACE_OPEN): ParseRule.R15.get_prods()[1],
    (ParseToken.STATEMENT, ParseToken.IF): ParseRule.R15.get_prods()[2],
    (ParseToken.STATEMENT, ParseToken.REPEAT): ParseRule.R15.get_prods()[3],
    (ParseToken.STATEMENT, ParseToken.RETURN): ParseRule.R15.get_prods()[4],

    (ParseToken.EXPRESSION_STMT, ParseToken.ID): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.PARENTHESIS_OPEN): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.NUM): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.BREAK): ParseRule.R16.get_prods()[1],
    (ParseToken.EXPRESSION_STMT, ParseToken.SEMICOLON): ParseRule.R16.get_prods()[2],

    (ParseToken.SELECTION_STMT, ParseToken.IF): ParseRule.R17.get_prods()[0],

    (ParseToken.ELSE_STMT, ParseToken.ENDIF): ParseRule.R18.get_prods()[0],
    (ParseToken.ELSE_STMT, ParseToken.ELSE): ParseRule.R18.get_prods()[1],

    (ParseToken.ITERATION_STMT, ParseToken.REPEAT): ParseRule.R19.get_prods()[0],

    (ParseToken.RETURN_STMT, ParseToken.RETURN): ParseRule.R20.get_prods()[0],

    (ParseToken.RETURN_STMT_PRIME, ParseToken.SEMICOLON): ParseRule.R21.get_prods()[0],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.ID): ParseRule.R21.get_prods()[1],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R21.get_prods()[1],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.NUM): ParseRule.R21.get_prods()[1],

    (ParseToken.EXPRESSION, ParseToken.PARENTHESIS_OPEN): ParseRule.R22.get_prods()[0],
    (ParseToken.EXPRESSION, ParseToken.NUM): ParseRule.R22.get_prods()[0],
    (ParseToken.EXPRESSION, ParseToken.ID): ParseRule.R22.get_prods()[1],

    (ParseToken.B, ParseToken.IS): ParseRule.R23.get_prods()[0],
    (ParseToken.B, ParseToken.BRACKET_OPEN): ParseRule.R23.get_prods()[1],
    (ParseToken.B, ParseToken.PARENTHESIS_OPEN): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.ASTERISK): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.MINUS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.PLUS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.LESS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.EQUALS): ParseRule.R23.get_prods()[2],

    (ParseToken.H, ParseToken.IS): ParseRule.R24.get_prods()[0],
    (ParseToken.H, ParseToken.ASTERISK): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.PLUS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.MINUS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.LESS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.EQUALS): ParseRule.R24.get_prods()[1],

    (ParseToken.SIMPLE_EXPRESSION_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R25.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_ZEGOND, ParseToken.NUM): ParseRule.R25.get_prods()[0],

    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.ASTERISK): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.PLUS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.MINUS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.LESS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.EQUALS): ParseRule.R26.get_prods()[0],

    (ParseToken.C, ParseToken.LESS): ParseRule.R27.get_prods()[0],
    (ParseToken.C, ParseToken.EQUALS): ParseRule.R27.get_prods()[0],

    (ParseToken.RELOP, ParseToken.LESS): ParseRule.R28.get_prods()[0],
    (ParseToken.RELOP, ParseToken.EQUALS): ParseRule.R28.get_prods()[1],

    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.PARENTHESIS_OPEN): ParseRule.R29.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.ID): ParseRule.R29.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.NUM): ParseRule.R29.get_prods()[0],

    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.ASTERISK): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.PLUS): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.MINUS): ParseRule.R30.get_prods()[0],

    (ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R31.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ParseToken.NUM): ParseRule.R31.get_prods()[0],

    (ParseToken.D, ParseToken.PLUS): ParseRule.R32.get_prods()[0],
    (ParseToken.D, ParseToken.MINUS): ParseRule.R32.get_prods()[0],

    (ParseToken.ADDOP, ParseToken.PLUS): ParseRule.R33.get_prods()[0],
    (ParseToken.ADDOP, ParseToken.MINUS): ParseRule.R33.get_prods()[1],

    (ParseToken.TERM, ParseToken.PARENTHESIS_OPEN): ParseRule.R34.get_prods()[0],
    (ParseToken.TERM, ParseToken.ID): ParseRule.R34.get_prods()[0],
    (ParseToken.TERM, ParseToken.NUM): ParseRule.R34.get_prods()[0],

    (ParseToken.TERM_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R35.get_prods()[0],
    (ParseToken.TERM_PRIME, ParseToken.ASTERISK): ParseRule.R35.get_prods()[0],

    (ParseToken.TERM_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R36.get_prods()[0],
    (ParseToken.TERM_ZEGOND, ParseToken.NUM): ParseRule.R36.get_prods()[0],

    (ParseToken.G, ParseToken.ASTERISK): ParseRule.R37.get_prods()[0],

    (ParseToken.FACTOR, ParseToken.PARENTHESIS_OPEN): ParseRule.R38.get_prods()[0],
    (ParseToken.FACTOR, ParseToken.ID): ParseRule.R38.get_prods()[1],
    (ParseToken.FACTOR, ParseToken.NUM): ParseRule.R38.get_prods()[2],

    (ParseToken.VAR_CALL_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R39.get_prods()[0],
    (ParseToken.VAR_CALL_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R39.get_prods()[1],

    (ParseToken.VAR_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R40.get_prods()[0],

    (ParseToken.FACTOR_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R41.get_prods()[0],

    (ParseToken.FACTOR_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R42.get_prods()[0],
    (ParseToken.FACTOR_ZEGOND, ParseToken.NUM): ParseRule.R42.get_prods()[1],

    (ParseToken.ARGS, ParseToken.ID): ParseRule.R43.get_prods()[0],
    (ParseToken.ARGS, ParseToken.PARENTHESIS_OPEN): ParseRule.R43.get_prods()[0],
    (ParseToken.ARGS, ParseToken.NUM): ParseRule.R43.get_prods()[0],

    (ParseToken.ARG_LIST, ParseToken.ID): ParseRule.R44.get_prods()[0],
    (ParseToken.ARG_LIST, ParseToken.PARENTHESIS_OPEN): ParseRule.R44.get_prods()[0],
    (ParseToken.ARG_LIST, ParseToken.NUM): ParseRule.R44.get_prods()[0],

    (ParseToken.ARG_LIST_PRIME, ParseToken.COMMA): ParseRule.R45.get_prods()[0],

}

epsilon_set = {
    ParseToken.ARGS: tuple(),
    ParseToken.ARG_LIST_PRIME: tuple(),
    ParseToken.DECLARATION_LIST: tuple(),
    ParseToken.FACTOR_PRIME: tuple(),
    ParseToken.VAR_PRIME: tuple(),
    ParseToken.VAR_CALL_PRIME: ParseRule.R39.get_prods()[1],
    ParseToken.B: ParseRule.R23.get_prods()[2],
    ParseToken.C: tuple(),
    ParseToken.D: tuple(),
    ParseToken.G: tuple(),
    ParseToken.H: ParseRule.R24.get_prods()[1],
    ParseToken.TERM_PRIME: ParseRule.R35.get_prods()[0],
    ParseToken.ADDITIVE_EXPRESSION_PRIME: ParseRule.R30.get_prods()[0],
    ParseToken.SIMPLE_EXPRESSION_PRIME: ParseRule.R26.get_prods()[0],
    ParseToken.STATEMENT_LIST: tuple(),
    ParseToken.PARAM_PRIME: tuple(),
    ParseToken.PARAM_LIST: tuple()
}

symbol_str_map = {
    ParseToken.ASTERISK: "*",
    ParseToken.PLUS: "+",
    ParseToken.MINUS: "-",
    ParseToken.LESS: "<",
    ParseToken.EQUALS: "==",
    ParseToken.IS: "=",
    ParseToken.COMMA: ",",
    ParseToken.SEMICOLON: ";",
    ParseToken.PARENTHESIS_OPEN: "(",
    ParseToken.PARENTHESIS_CLOSE: ")",
    ParseToken.BRACE_OPEN: "{",
    ParseToken.BRACE_CLOSE: "}",
    ParseToken.BRACKET_OPEN: "[",
    ParseToken.BRACKET_CLOSE: "]"}

synchronizing_table = {
    ParseToken.ADDITIVE_EXPRESSION: {ParseToken.BRACKET_CLOSE,
                                     ParseToken.COMMA,
                                     ParseToken.SEMICOLON,
                                     ParseToken.PARENTHESIS_CLOSE},
    ParseToken.ADDITIVE_EXPRESSION_PRIME: {ParseToken.PARENTHESIS_CLOSE,
                                           ParseToken.COMMA,
                                           ParseToken.SEMICOLON,
                                           ParseToken.LESS,
                                           ParseToken.EQUALS,
                                           ParseToken.BRACKET_CLOSE},
    ParseToken.ADDITIVE_EXPRESSION_ZEGOND: {ParseToken.PARENTHESIS_CLOSE,
                                            ParseToken.COMMA,
                                            ParseToken.SEMICOLON,
                                            ParseToken.LESS,
                                            ParseToken.EQUALS,
                                            ParseToken.BRACKET_CLOSE},
    ParseToken.ADDOP: {ParseToken.PARENTHESIS_OPEN,
                       ParseToken.ID,
                       ParseToken.NUM},
    ParseToken.ARG_LIST: {ParseToken.PARENTHESIS_CLOSE},
    ParseToken.ARG_LIST_PRIME: {ParseToken.PARENTHESIS_CLOSE},
    ParseToken.ARGS: {ParseToken.PARENTHESIS_CLOSE},
    ParseToken.B: {ParseToken.PARENTHESIS_CLOSE,
                   ParseToken.COMMA,
                   ParseToken.SEMICOLON,
                   ParseToken.BRACKET_CLOSE},
    ParseToken.C: {ParseToken.PARENTHESIS_CLOSE,
                   ParseToken.COMMA,
                   ParseToken.SEMICOLON,
                   ParseToken.BRACKET_CLOSE},
    ParseToken.COMPOUND_STMT: {ParseToken.DOLLAR,
                               ParseToken.PARENTHESIS_OPEN,
                               ParseToken.SEMICOLON,
                               ParseToken.ID,
                               ParseToken.NUM,
                               ParseToken.BREAK,
                               ParseToken.ELSE,
                               ParseToken.ENDIF,
                               ParseToken.IF,
                               ParseToken.INT,
                               ParseToken.REPEAT,
                               ParseToken.RETURN,
                               ParseToken.UNTIL,
                               ParseToken.VOID,
                               ParseToken.BRACE_OPEN,
                               ParseToken.BRACE_CLOSE},
    ParseToken.D: {ParseToken.PARENTHESIS_CLOSE,
                   ParseToken.COMMA,
                   ParseToken.SEMICOLON,
                   ParseToken.LESS,
                   ParseToken.EQUALS,
                   ParseToken.BRACKET_CLOSE},
    ParseToken.DECLARATION: {ParseToken.DOLLAR,
                             ParseToken.PARENTHESIS_OPEN,
                             ParseToken.SEMICOLON,
                             ParseToken.ID,
                             ParseToken.NUM,
                             ParseToken.BREAK,
                             ParseToken.IF,
                             ParseToken.INT,
                             ParseToken.REPEAT,
                             ParseToken.RETURN,
                             ParseToken.VOID,
                             ParseToken.BRACE_OPEN,
                             ParseToken.BRACE_CLOSE},
    ParseToken.DECLARATION_INITIAL: {ParseToken.PARENTHESIS_OPEN,
                                     ParseToken.PARENTHESIS_CLOSE,
                                     ParseToken.COMMA,
                                     ParseToken.SEMICOLON,
                                     ParseToken.BRACKET_OPEN},
    ParseToken.DECLARATION_LIST: {ParseToken.DOLLAR,
                                  ParseToken.PARENTHESIS_OPEN,
                                  ParseToken.SEMICOLON,
                                  ParseToken.ID,
                                  ParseToken.NUM,
                                  ParseToken.BREAK,
                                  ParseToken.IF,
                                  ParseToken.REPEAT,
                                  ParseToken.RETURN,
                                  ParseToken.BRACE_OPEN,
                                  ParseToken.BRACE_CLOSE},
    ParseToken.DECLARATION_PRIME: {ParseToken.DOLLAR,
                                   ParseToken.PARENTHESIS_OPEN,
                                   ParseToken.SEMICOLON,
                                   ParseToken.ID,
                                   ParseToken.NUM,
                                   ParseToken.BREAK,
                                   ParseToken.IF,
                                   ParseToken.INT,
                                   ParseToken.REPEAT,
                                   ParseToken.RETURN,
                                   ParseToken.VOID,
                                   ParseToken.BRACE_OPEN,
                                   ParseToken.BRACE_CLOSE},
    ParseToken.ELSE_STMT: {ParseToken.PARENTHESIS_OPEN,
                           ParseToken.SEMICOLON,
                           ParseToken.ID,
                           ParseToken.NUM,
                           ParseToken.BREAK,
                           ParseToken.ELSE,
                           ParseToken.ENDIF,
                           ParseToken.IF,
                           ParseToken.REPEAT,
                           ParseToken.RETURN,
                           ParseToken.UNTIL,
                           ParseToken.BRACE_OPEN,
                           ParseToken.BRACE_CLOSE},
    ParseToken.EXPRESSION: {ParseToken.PARENTHESIS_CLOSE,
                            ParseToken.COMMA,
                            ParseToken.SEMICOLON,
                            ParseToken.BRACKET_CLOSE},
    ParseToken.EXPRESSION_STMT: {ParseToken.PARENTHESIS_OPEN,
                                 ParseToken.SEMICOLON,
                                 ParseToken.ID,
                                 ParseToken.NUM,
                                 ParseToken.BREAK,
                                 ParseToken.ELSE,
                                 ParseToken.ENDIF,
                                 ParseToken.IF,
                                 ParseToken.REPEAT,
                                 ParseToken.RETURN,
                                 ParseToken.UNTIL,
                                 ParseToken.BRACE_OPEN,
                                 ParseToken.BRACE_CLOSE},
    ParseToken.FACTOR: {ParseToken.PARENTHESIS_CLOSE,
                        ParseToken.ASTERISK,
                        ParseToken.PLUS,
                        ParseToken.COMMA,
                        ParseToken.MINUS,
                        ParseToken.SEMICOLON,
                        ParseToken.LESS,
                        ParseToken.EQUALS,
                        ParseToken.BRACKET_CLOSE},
    ParseToken.FACTOR_PRIME: {ParseToken.PARENTHESIS_CLOSE,
                              ParseToken.ASTERISK,
                              ParseToken.PLUS,
                              ParseToken.COMMA,
                              ParseToken.MINUS,
                              ParseToken.SEMICOLON,
                              ParseToken.LESS,
                              ParseToken.EQUALS,
                              ParseToken.BRACKET_CLOSE},
    ParseToken.FACTOR_ZEGOND: {ParseToken.PARENTHESIS_CLOSE,
                               ParseToken.ASTERISK,
                               ParseToken.PLUS,
                               ParseToken.COMMA,
                               ParseToken.MINUS,
                               ParseToken.SEMICOLON,
                               ParseToken.LESS,
                               ParseToken.EQUALS,
                               ParseToken.BRACKET_CLOSE},
    ParseToken.FUN_DECLARATION_PRIME: {ParseToken.DOLLAR,
                                       ParseToken.PARENTHESIS_OPEN,
                                       ParseToken.SEMICOLON,
                                       ParseToken.ID,
                                       ParseToken.NUM,
                                       ParseToken.BREAK,
                                       ParseToken.IF,
                                       ParseToken.INT,
                                       ParseToken.REPEAT,
                                       ParseToken.RETURN,
                                       ParseToken.VOID,
                                       ParseToken.BRACE_OPEN,
                                       ParseToken.BRACE_CLOSE},
    ParseToken.G: {ParseToken.PARENTHESIS_CLOSE,
                   ParseToken.PLUS,
                   ParseToken.COMMA,
                   ParseToken.MINUS,
                   ParseToken.SEMICOLON,
                   ParseToken.LESS,
                   ParseToken.EQUALS,
                   ParseToken.BRACKET_CLOSE},
    ParseToken.H: {ParseToken.PARENTHESIS_CLOSE,
                   ParseToken.COMMA,
                   ParseToken.SEMICOLON,
                   ParseToken.BRACKET_CLOSE},
    ParseToken.ITERATION_STMT: {ParseToken.PARENTHESIS_OPEN,
                                ParseToken.SEMICOLON,
                                ParseToken.ID,
                                ParseToken.NUM,
                                ParseToken.BREAK,
                                ParseToken.ELSE,
                                ParseToken.ENDIF,
                                ParseToken.IF,
                                ParseToken.REPEAT,
                                ParseToken.RETURN,
                                ParseToken.UNTIL,
                                ParseToken.BRACE_OPEN,
                                ParseToken.BRACE_CLOSE},
    ParseToken.PARAM: {ParseToken.PARENTHESIS_CLOSE,
                       ParseToken.COMMA},
    ParseToken.PARAM_LIST: {ParseToken.PARENTHESIS_CLOSE},
    ParseToken.PARAM_PRIME: {ParseToken.PARENTHESIS_CLOSE,
                             ParseToken.COMMA},
    ParseToken.PARAMS: {ParseToken.PARENTHESIS_CLOSE},
    ParseToken.PROGRAM: {ParseToken.ASTERISK},
    ParseToken.RELOP: {ParseToken.PARENTHESIS_OPEN,
                       ParseToken.ID,
                       ParseToken.NUM},
    ParseToken.RETURN_STMT: {ParseToken.PARENTHESIS_OPEN,
                             ParseToken.SEMICOLON,
                             ParseToken.ID,
                             ParseToken.NUM,
                             ParseToken.BREAK,
                             ParseToken.ELSE,
                             ParseToken.ENDIF,
                             ParseToken.IF,
                             ParseToken.REPEAT,
                             ParseToken.RETURN,
                             ParseToken.UNTIL,
                             ParseToken.BRACE_OPEN,
                             ParseToken.BRACE_CLOSE},
    ParseToken.RETURN_STMT_PRIME: {ParseToken.PARENTHESIS_OPEN,
                                   ParseToken.SEMICOLON,
                                   ParseToken.ID,
                                   ParseToken.NUM,
                                   ParseToken.BREAK,
                                   ParseToken.ELSE,
                                   ParseToken.ENDIF,
                                   ParseToken.IF,
                                   ParseToken.REPEAT,
                                   ParseToken.RETURN,
                                   ParseToken.UNTIL,
                                   ParseToken.BRACE_OPEN,
                                   ParseToken.BRACE_CLOSE},
    ParseToken.SELECTION_STMT: {ParseToken.PARENTHESIS_OPEN,
                                ParseToken.SEMICOLON,
                                ParseToken.ID,
                                ParseToken.NUM,
                                ParseToken.BREAK,
                                ParseToken.ELSE,
                                ParseToken.ENDIF,
                                ParseToken.IF,
                                ParseToken.REPEAT,
                                ParseToken.RETURN,
                                ParseToken.UNTIL,
                                ParseToken.BRACE_OPEN,
                                ParseToken.BRACE_CLOSE},
    ParseToken.SIMPLE_EXPRESSION_PRIME: {ParseToken.PARENTHESIS_CLOSE,
                                         ParseToken.COMMA,
                                         ParseToken.SEMICOLON,
                                         ParseToken.BRACKET_CLOSE},
    ParseToken.SIMPLE_EXPRESSION_ZEGOND: {ParseToken.PARENTHESIS_CLOSE,
                                          ParseToken.COMMA,
                                          ParseToken.SEMICOLON,
                                          ParseToken.BRACKET_CLOSE},
    ParseToken.STATEMENT: {ParseToken.PARENTHESIS_OPEN,
                           ParseToken.SEMICOLON,
                           ParseToken.ID,
                           ParseToken.NUM,
                           ParseToken.BREAK,
                           ParseToken.ELSE,
                           ParseToken.ENDIF,
                           ParseToken.IF,
                           ParseToken.REPEAT,
                           ParseToken.RETURN,
                           ParseToken.UNTIL,
                           ParseToken.BRACE_OPEN,
                           ParseToken.BRACE_CLOSE},
    ParseToken.STATEMENT_LIST: {ParseToken.BRACE_CLOSE},
    ParseToken.TERM: {ParseToken.PARENTHESIS_CLOSE,
                      ParseToken.PLUS,
                      ParseToken.COMMA,
                      ParseToken.MINUS,
                      ParseToken.SEMICOLON,
                      ParseToken.LESS,
                      ParseToken.EQUALS,
                      ParseToken.BRACKET_CLOSE},
    ParseToken.TERM_PRIME: {ParseToken.PARENTHESIS_CLOSE,
                            ParseToken.PLUS,
                            ParseToken.COMMA,
                            ParseToken.MINUS,
                            ParseToken.SEMICOLON,
                            ParseToken.LESS,
                            ParseToken.EQUALS,
                            ParseToken.BRACKET_CLOSE},
    ParseToken.TERM_ZEGOND: {ParseToken.PARENTHESIS_CLOSE,
                             ParseToken.PLUS,
                             ParseToken.COMMA,
                             ParseToken.MINUS,
                             ParseToken.SEMICOLON,
                             ParseToken.LESS,
                             ParseToken.EQUALS,
                             ParseToken.BRACKET_CLOSE},
    ParseToken.TYPE_SPECIFIER: {ParseToken.ID},
    ParseToken.VAR_CALL_PRIME: {ParseToken.PARENTHESIS_CLOSE,
                                ParseToken.ASTERISK,
                                ParseToken.PLUS,
                                ParseToken.COMMA,
                                ParseToken.MINUS,
                                ParseToken.SEMICOLON,
                                ParseToken.LESS,
                                ParseToken.EQUALS,
                                ParseToken.BRACKET_CLOSE},
    ParseToken.VAR_DECLARATION_PRIME: {ParseToken.DOLLAR,
                                       ParseToken.PARENTHESIS_OPEN,
                                       ParseToken.SEMICOLON,
                                       ParseToken.ID,
                                       ParseToken.NUM,
                                       ParseToken.BREAK,
                                       ParseToken.IF,
                                       ParseToken.INT,
                                       ParseToken.REPEAT,
                                       ParseToken.RETURN,
                                       ParseToken.VOID,
                                       ParseToken.BRACE_OPEN,
                                       ParseToken.BRACE_CLOSE},
    ParseToken.VAR_PRIME: {ParseToken.PARENTHESIS_CLOSE,
                           ParseToken.ASTERISK,
                           ParseToken.PLUS,
                           ParseToken.COMMA,
                           ParseToken.MINUS,
                           ParseToken.SEMICOLON,
                           ParseToken.LESS,
                           ParseToken.EQUALS,
                           ParseToken.BRACKET_CLOSE},
}


def send_error(error: ScanerErrorType, error_file, new_line: bool, cur_seq: str, remained_char: str):
    global _line_idx, _found_lexical_error
    seq = cur_seq + remained_char
    if error != ScanerErrorType.UNCLOSED_COMMENT:
        error.write_to_file(error_file, seq, _line_idx, new_line)
    else:
        error.write_to_file(error_file, seq[0:min(len(seq), 7)] + "...", _line_idx, new_line)
    _found_lexical_error = True
    flush()


def print_tree_row(info: str, depth: list, index: int, parse_tree_f, is_last: bool, is_dollar: bool):
    row = ''
    cur_depth = depth[index]
    if cur_depth > 0:
        for i in range(1, cur_depth):
            last_occur_prev = index - depth[:index][::-1].index(i) - 1
            if not check_is_last(depth[last_occur_prev:]):
                row += '│   '
            else:
                row += '    '
        if is_last:
            row += '└── '
        else:
            row += '├── '

    row += info + ('\n' if not is_dollar else '')
    parse_tree_f.write(row)


def check_is_last(depth_list: list):
    for i in range(1, len(depth_list)):
        if depth_list[i] == depth_list[0]:
            return False
        elif depth_list[i] < depth_list[0]:
            return True
    return True


def print_tree(tree_entries: list, parse_tree_f):
    depth_list = [d for _, d in tree_entries]
    last_idx = len(tree_entries) - 1
    for i in range(0, last_idx):
        print_tree_row(tree_entries[i][0], depth_list, i, parse_tree_f, check_is_last(depth_list[i:]), False)
    print_tree_row(tree_entries[last_idx][0], depth_list, last_idx, parse_tree_f, True, True)


error_found = False


def send_parser_error(file, error_type: ParserErrorType, _line_idx: int, info: str):
    global error_found
    error = "\n" if error_found else ""
    error_found = True
    error += f"#{_line_idx} : syntax error, {error_type.value} {info}"
    file.write(error)


def apply_rule(seq: str, scan_token_type: ScanTokenType, parse_tokens: tuple, depth: list, parse_tree_f,
               syntax_error_f, _line_idx, tree_entries: list) -> (tuple, list, bool, bool):
    parse_token_equivalent = get_parse_token_for_seq(seq, scan_token_type)
    init_token: ParseToken
    init_token = parse_tokens[0]
    if init_token.get_type() != ParseTokenType.NON_TERMINAL and init_token == parse_token_equivalent:
        if parse_token_equivalent == ParseToken.DOLLAR:
            tree_entries.append((str(parse_token_equivalent).format(seq=seq), depth[0]))
        else:
            tree_entries.append((str(scan_token_type).format(seq=seq), depth[0]))
        return parse_tokens[1:], depth[1:], tree_entries, False, False
    else:
        pair = (init_token, parse_token_equivalent)
        if pair in parse_table.keys():
            tree_entries.append((str(init_token), depth[0]))
            prods: tuple
            prods = parse_table[pair]
            new_depth = [depth[0] + 1 for _ in prods]
            return apply_rule(seq, scan_token_type, prods.__add__(parse_tokens[1:]), new_depth.__add__(depth[1:]),
                              parse_tree_f, syntax_error_f, _line_idx, tree_entries)
        elif pair[0] in epsilon_set and pair[1] in synchronizing_table[pair[0]]:
            tree_entries.append((str(init_token), depth[0]))
            prods = epsilon_set[init_token]
            if len(prods) == 0:
                tree_entries.append((str(ParseToken.EPSILON).format(seq=seq), depth[0] + 1))
            new_depth = [depth[0] + 1 for _ in prods]
            return prods + parse_tokens[1:], new_depth.__add__(depth[1:]), tree_entries, True, False
        else:
            if (pair[0].get_type() != ParseTokenType.NON_TERMINAL) or (pair[1] in synchronizing_table[pair[0]]):
                if pair[0].get_type() == ParseTokenType.NON_TERMINAL:
                    info = str(init_token)
                else:
                    if scan_token_type in {ScanTokenType.ID, ScanTokenType.NUM}:
                        info = scan_token_type.name
                    elif init_token in {ParseToken.IF, ParseToken.ENDIF, ParseToken.ELSE, ParseToken.BREAK,
                                        ParseToken.REPEAT, ParseToken.RETURN, ParseToken.UNTIL}:
                        info = init_token.name.lower()
                    elif init_token in symbol_str_map:
                        info = symbol_str_map[init_token]
                    else:
                        info = str(init_token)
                send_parser_error(syntax_error_f, ParserErrorType.MISSING, _line_idx, info)
                depth[0] += 1
                return parse_tokens[1:], depth[1:], tree_entries, True, True
            else:
                line_idx = _line_idx
                error_type = ParserErrorType.ILLEGAL
                if scan_token_type is ScanTokenType.SYMBOL:
                    info = seq
                elif parse_token_equivalent is ParseToken.INT:
                    info = "int"
                elif scan_token_type is ScanTokenType.EOF:
                    info = "EOF"
                    line_idx += 1
                    error_type = ParserErrorType.UNEXPECTED
                else:
                    info = str(parse_token_equivalent)
                send_parser_error(syntax_error_f, error_type, line_idx,
                                  info)
                return parse_tokens, depth, tree_entries, False, True


input_file_name = "input.txt"
tokens_file_name = 'tokens.txt'
lexical_errors_file_name = "lexical_errors.txt"
symbols_file_name = 'symbol_table.txt'
parse_tree_file_name = "parse_tree.txt"
syntax_errors_file_name = "syntax_errors.txt"
DEBUG = True
_line_idx = 1
_symbol_idx = 1
_found_lexical_error = False
_found_syntax_error = False


def dprint(*string):  # debug print
    global DEBUG
    if DEBUG:
        print(*string)


def run(input_fn: str, tokens_fn: str, lexical_errors_fn: str, symbols_fn: str, parse_tree_fn: str,
        syntax_errors_fn: str):
    global DEBUG, _line_idx, _found_lexical_error, _symbol_idx, _found_syntax_error
    _found_lexical_error = False
    next_line_flag = True
    printing_started = False
    prev_err_line_idx = math.inf
    with open(input_fn, 'r') as input_f, open(tokens_fn, 'w') as tokens_f, open(lexical_errors_fn, 'w') as \
            lexical_errors_f, open(symbols_fn, 'w') as symbols_f, open(parse_tree_fn, 'w') as parse_tree_f, \
            open(syntax_errors_fn, 'w') as syntax_errors_f:
        ids_table = list()
        parse_tokens, depth, tree_entries = (ParseRule.R1.get_token(),), [0], []
        while True:
            eof, scan_token, error, cur_seq, remained_char = get_next_token(input_f)
            if scan_token is ScanTokenType.ERROR:
                if remained_char in next_line_set:
                    _line_idx += 1
                if prev_err_line_idx < _line_idx:
                    lexical_errors_f.write("\n")
                    send_error(error, lexical_errors_f, True, cur_seq, remained_char)
                elif prev_err_line_idx == math.inf:
                    send_error(error, lexical_errors_f, True, cur_seq, remained_char)
                else:
                    send_error(error, lexical_errors_f, False, cur_seq, remained_char)
                prev_err_line_idx = _line_idx
                continue
            if not eof:
                # Scanner
                if scan_token is ScanTokenType.WHITESPACE and cur_seq in next_line_set:
                    next_line_flag = True
                    _line_idx += 1
                if scan_token is ScanTokenType.COMMENT and list(next_line_set)[0] in cur_seq:
                    _line_idx += cur_seq.count(list(next_line_set)[0])
                if scan_token is ScanTokenType.WHITESPACE or scan_token is ScanTokenType.COMMENT:
                    continue
                if next_line_flag:
                    if printing_started:
                        tokens_f.write('\n{lineno:d}.\t'.format(lineno=_line_idx))
                    else:
                        tokens_f.write('{lineno:d}.\t'.format(lineno=_line_idx))
                        printing_started = True
                    next_line_flag = False
                tokens_f.write(str(scan_token).format(seq=cur_seq) + ' ')
                if scan_token is ScanTokenType.ID:
                    if cur_seq not in ids_table:
                        ids_table.append(cur_seq)
                # Parser
                epsilon = True
                if scan_token not in (ScanTokenType.WHITESPACE, ScanTokenType.COMMENT):
                    while epsilon:
                        parse_tokens, depth, tree_entries, epsilon, error = apply_rule(
                            cur_seq, scan_token, parse_tokens, depth, parse_tree_f, syntax_errors_f, _line_idx,
                            tree_entries)
                        if len(parse_tokens) == 0:
                            break
                        if error:
                            _found_syntax_error = True
                        if parse_tokens is None:
                            continue
                    if len(parse_tokens) == 0:
                        break
            else:
                # Scanner
                tokens_f.write(str(ScanTokenType.EOF).format(seq="$") + ' ')
                dprint("End of compilation.")
                if not _found_lexical_error:
                    lexical_errors_f.write("There is no lexical error.")
                if not _found_syntax_error:
                    syntax_errors_f.write("There is no syntax error.")
                # Parser
                epsilon = True
                while epsilon:
                    parse_tokens, depth, tree_entries, epsilon, error = apply_rule(
                        cur_seq, scan_token, parse_tokens, depth, parse_tree_f, syntax_errors_f, _line_idx,
                        tree_entries)
                    if error:
                        _found_syntax_error = True
                tree_entries.append(('', 0))
                break
        print_tree(tree_entries, parse_tree_f)
        item_no = 1
        for sym in keywords_list:
            symbols_f.write(f"{item_no}.\t{sym}\n")
            item_no += 1
        for sym in ids_table:
            symbols_f.write(f"{item_no}.\t{sym}\n")
            item_no += 1
        input_f.close()
        tokens_f.close()
        lexical_errors_f.close()
        symbols_f.close()


run(input_file_name, tokens_file_name, lexical_errors_file_name, symbols_file_name, parse_tree_file_name,
    syntax_errors_file_name)
