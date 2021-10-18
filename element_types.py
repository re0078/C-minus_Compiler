from enum import Enum

num_set = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
alphabet_set = {'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g', 'H', 'h', 'I', 'i', 'J', 'j', 'K',
                'k', 'L', 'l', 'M', 'm', 'N', 'n', 'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't', 'U', 'u',
                'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z'}
alphanumeric_set = alphabet_set.union(num_set)
keywords_set = {'if', 'else', 'return', 'break', 'until', 'repeat', 'int', 'void'}
asterisk_set = {'*'}
symbols_set = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<'}.union(asterisk_set)
equal_char_set = {'='}
comment_set = {'/'}
next_line_set = {'\n'}
whitespaces_set = {' ', '\r', '\t', '\v', '\f'}.union(next_line_set)
empty_set = set()
valid_chars_set = alphanumeric_set.union(symbols_set).union(equal_char_set).union(comment_set).union(whitespaces_set)


class State:
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


class TokenType(Enum):
    """ id, tuple of valid states """
    NUM = (1, (State(num_set, ends=False, repeatable=True),)),
    ID = (2, (State(alphabet_set, ends=False), State(alphanumeric_set, ends=False, repeatable=True))),
    SYMBOL = (3, (State(symbols_set, ends=True, otherwise_state=1, universal_set=equal_char_set),
                  State(equal_char_set, ends=True, universal_set=valid_chars_set))),
    COMMENT = (4, (State(comment_set, ends=False),
                   State(asterisk_set, ends=False, otherwise_state=4, universal_set=comment_set),
                   State(asterisk_set, ends=False, otherwise_state=2, universal_set=valid_chars_set),
                   State(comment_set, ends=True, otherwise_state=2, universal_set=valid_chars_set),
                   State(empty_set, ends=True, otherwise_state=4, universal_set=valid_chars_set - next_line_set))),
    WHITESPACE = (5, (State(whitespaces_set, ends=True),)),
    KEYWORD = (6, (State(keywords_set, ends=True, repeatable=False),)),
    EOF = (7, ()),
    ERROR = (8, ())

    def get_state(self, state_order: int) -> State:
        return self.value[0][1][state_order]

    def __str__(self):
        return '(' + self.name + ', {seq:s})'
