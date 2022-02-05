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
_VARS_OFFSET = 100
_TEMP_OFFSET = 500
_OFFSET_COE = 4


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
    ERROR = (),

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


class SymbolStackElementType(Enum):
    REPEAT = 0,
    FUNCTION = 1,
    VARIABLE_SINGLE = 2,
    VARIABLE_ARRAY = 3,
    PARAM_SINGLE = 4,
    PARAM_ARRAY = 5,
    UNKNOWN = 6,


class BraceElementType(Enum):
    FUNCTION = 0,
    REPEAT = 1,
    IF = 2,
    ELSE = 3,
    MAIN = 4,


class ActionSymbol(Enum):
    PID = 0,
    ADD = 1,
    MULT = 2,
    SUB = 3,
    EQ = 4,
    LT = 5,
    ASSIGN = 6,
    JPF = 7,
    JP = 8,
    PRINT = 9,

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class ParseRule(Enum):
    R1 = [ParseToken.PROGRAM, [[ParseToken.DECLARATION_LIST, ParseToken.DOLLAR], ]],
    R2 = [ParseToken.DECLARATION_LIST, [[ParseToken.DECLARATION, ParseToken.DECLARATION_LIST], [ParseToken.EPSILON, ]]],
    R3 = [ParseToken.DECLARATION, [[ParseToken.DECLARATION_INITIAL, ParseToken.DECLARATION_PRIME], ]],
    R4 = [ParseToken.DECLARATION_INITIAL, [[ParseToken.TYPE_SPECIFIER, ParseToken.ID], ]],
    R5 = [ParseToken.DECLARATION_PRIME, [[ActionSymbol.ASSIGN, ParseToken.FUN_DECLARATION_PRIME, ],
                                         [ParseToken.VAR_DECLARATION_PRIME, ]]],
    R6 = [ParseToken.VAR_DECLARATION_PRIME, [[ParseToken.SEMICOLON, ActionSymbol.ASSIGN],
                                             [ParseToken.BRACKET_OPEN, ParseToken.NUM, ParseToken.BRACKET_CLOSE,
                                              ParseToken.SEMICOLON, ActionSymbol.ASSIGN]]],
    R7 = [ParseToken.FUN_DECLARATION_PRIME, [[ParseToken.PARENTHESIS_OPEN, ParseToken.PARAMS,
                                              ParseToken.PARENTHESIS_CLOSE, ParseToken.COMPOUND_STMT], ]],
    R8 = [ParseToken.TYPE_SPECIFIER, [[ParseToken.INT, ], [ParseToken.VOID, ]]],
    R9 = [ParseToken.PARAMS, [[ParseToken.INT, ParseToken.ID, ActionSymbol.ASSIGN, ParseToken.PARAM_PRIME,
                               ParseToken.PARAM_LIST], [ParseToken.VOID, ]]],
    R10 = [ParseToken.PARAM_LIST,
           [[ParseToken.COMMA, ParseToken.PARAM, ParseToken.PARAM_LIST], [ParseToken.EPSILON, ]]],
    R11 = [ParseToken.PARAM, [[ParseToken.DECLARATION_INITIAL, ParseToken.PARAM_PRIME], ]],
    R12 = [ParseToken.PARAM_PRIME, [[ParseToken.BRACKET_OPEN, ParseToken.BRACKET_CLOSE], [ParseToken.EPSILON, ]]],
    R13 = [ParseToken.COMPOUND_STMT, [[ParseToken.BRACE_OPEN, ParseToken.DECLARATION_LIST, ParseToken.STATEMENT_LIST,
                                       ParseToken.BRACE_CLOSE], ]],
    R14 = [ParseToken.STATEMENT_LIST, [[ParseToken.STATEMENT, ParseToken.STATEMENT_LIST],
                                       [ParseToken.EPSILON, ]]],
    R15 = [ParseToken.STATEMENT, [[ParseToken.EXPRESSION_STMT, ], [ParseToken.COMPOUND_STMT, ],
                                  [ParseToken.SELECTION_STMT, ], [ParseToken.ITERATION_STMT, ],
                                  [ParseToken.RETURN_STMT, ]]],
    R16 = [ParseToken.EXPRESSION_STMT, [[ParseToken.EXPRESSION, ParseToken.SEMICOLON], [ParseToken.BREAK,
                                                                                        ActionSymbol.JP,
                                                                                        ParseToken.SEMICOLON],
                                        [ParseToken.SEMICOLON, ]]],
    R17 = [ParseToken.SELECTION_STMT, [[ParseToken.IF, ParseToken.PARENTHESIS_OPEN, ParseToken.EXPRESSION,
                                        ParseToken.PARENTHESIS_CLOSE, ActionSymbol.JPF, ParseToken.STATEMENT,
                                        ParseToken.ELSE_STMT], ]],
    R18 = [ParseToken.ELSE_STMT, [[ParseToken.ENDIF, ], [ParseToken.ELSE, ParseToken.STATEMENT, ParseToken.ENDIF], ]],
    R19 = [ParseToken.ITERATION_STMT, [[ParseToken.REPEAT, ActionSymbol.JP, ActionSymbol.JP, ParseToken.STATEMENT,
                                        ParseToken.UNTIL, ParseToken.PARENTHESIS_OPEN, ParseToken.EXPRESSION,
                                        ParseToken.PARENTHESIS_CLOSE, ActionSymbol.JPF, ActionSymbol.JP], ]],
    R20 = [ParseToken.RETURN_STMT, [[ParseToken.RETURN, ParseToken.RETURN_STMT_PRIME, ActionSymbol.JP], ]],
    R21 = [ParseToken.RETURN_STMT_PRIME, [[ParseToken.SEMICOLON, ], [ParseToken.EXPRESSION, ParseToken.SEMICOLON,
                                                                     ActionSymbol.ASSIGN]]],
    R22 = [ParseToken.EXPRESSION, [[ParseToken.SIMPLE_EXPRESSION_ZEGOND, ], [ParseToken.ID, ParseToken.B], ]],
    R23 = [ParseToken.B, [[ParseToken.IS, ParseToken.EXPRESSION, ActionSymbol.ASSIGN],
                          [ParseToken.BRACKET_OPEN, ParseToken.EXPRESSION, ParseToken.BRACKET_CLOSE, ParseToken.H],
                          [ParseToken.SIMPLE_EXPRESSION_PRIME, ]]],
    R24 = [ParseToken.H, [[ParseToken.IS, ParseToken.EXPRESSION, ActionSymbol.ASSIGN],
                          [ParseToken.G, ParseToken.D, ParseToken.C]]],
    R25 = [ParseToken.SIMPLE_EXPRESSION_ZEGOND, [[ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ParseToken.C], ]],
    R26 = [ParseToken.SIMPLE_EXPRESSION_PRIME, [[ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.C], ]],
    R27 = [ParseToken.C, [[ParseToken.LESS, ParseToken.ADDITIVE_EXPRESSION, ActionSymbol.LT],
                          [ParseToken.EQUALS, ParseToken.ADDITIVE_EXPRESSION, ActionSymbol.EQ],
                          [ParseToken.EPSILON, ]]],
    # R28 = [ParseToken.RELOP, [[ParseToken.LESS, ActionSymbol.LT], [ParseToken.EQUALS, ActionSymbol.EQ]]],
    R29 = [ParseToken.ADDITIVE_EXPRESSION, [[ParseToken.TERM, ParseToken.D], ]],
    R30 = [ParseToken.ADDITIVE_EXPRESSION_PRIME, [[ParseToken.TERM_PRIME, ParseToken.D], ]],
    R31 = [ParseToken.ADDITIVE_EXPRESSION_ZEGOND, [[ParseToken.TERM_ZEGOND, ParseToken.D], ]],
    R32 = [ParseToken.D, [[ParseToken.PLUS, ParseToken.TERM, ActionSymbol.ADD, ParseToken.D],
                          [ParseToken.MINUS, ParseToken.TERM, ActionSymbol.SUB, ParseToken.D], [ParseToken.EPSILON, ]]],
    # R33 = [ParseToken.ADDOP, [[ParseToken.PLUS, ActionSymbol.ADD], [ParseToken.MINUS, ActionSymbol.SUB]]],
    R34 = [ParseToken.TERM, [[ParseToken.FACTOR, ParseToken.G], ]],
    R35 = [ParseToken.TERM_PRIME, [[ParseToken.FACTOR_PRIME, ParseToken.G], ]],
    R36 = [ParseToken.TERM_ZEGOND, [[ParseToken.FACTOR_ZEGOND, ParseToken.G], ]],
    R37 = [ParseToken.G, [[ParseToken.ASTERISK, ParseToken.FACTOR, ActionSymbol.MULT, ParseToken.G],
                          [ParseToken.EPSILON, ]]],
    R38 = [ParseToken.FACTOR, [[ParseToken.PARENTHESIS_OPEN, ParseToken.EXPRESSION, ParseToken.PARENTHESIS_CLOSE],
                               [ParseToken.ID, ParseToken.VAR_CALL_PRIME], [ParseToken.NUM, ]]],
    R39 = [ParseToken.VAR_CALL_PRIME, [[ParseToken.PARENTHESIS_OPEN, ParseToken.ARGS, ParseToken.PARENTHESIS_CLOSE],
                                       [ParseToken.VAR_PRIME, ]]],
    R40 = [ParseToken.VAR_PRIME, [[ParseToken.BRACE_OPEN, ParseToken.EXPRESSION, ParseToken.BRACKET_CLOSE],
                                  [ParseToken.EPSILON, ]]],
    R41 = [ParseToken.FACTOR_PRIME, [[ParseToken.PARENTHESIS_OPEN, ParseToken.ARGS, ParseToken.PARENTHESIS_CLOSE],
                                     [ParseToken.EPSILON, ]]],
    R42 = [ParseToken.FACTOR_ZEGOND, [[ParseToken.PARENTHESIS_OPEN, ParseToken.EXPRESSION,
                                       ParseToken.PARENTHESIS_CLOSE], [ParseToken.NUM, ]]],
    R43 = [ParseToken.ARGS, [[ParseToken.ARG_LIST, ], [ParseToken.EPSILON, ], ]],
    R44 = [ParseToken.ARG_LIST, [[ParseToken.EXPRESSION, ParseToken.ARG_LIST_PRIME], ]],
    R45 = [ParseToken.ARG_LIST_PRIME, [[ParseToken.COMMA, ParseToken.EXPRESSION, ParseToken.ARG_LIST_PRIME],
                                       [ParseToken.EPSILON, ]]],

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
