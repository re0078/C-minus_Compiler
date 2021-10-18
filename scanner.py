from element_types import *
from error_type import *

_cur_seq = ""
_remained_char = ""
_cur_state_order = 0
_found_error = False
_token_type_determined = False


def flush():
    global _cur_seq, _remained_char, _cur_state_order, _token_type_determined
    _cur_seq = ""
    _remained_char = ""
    _cur_state_order = 0
    _token_type_determined = False


def scan_process(c: str, token_type: TokenType) -> (bool, bool):
    global _cur_seq, _remained_char, _cur_state_order, _token_type_determined
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
        if (cur_state.repeatable or cur_state.valid_set == empty_set) and _token_type_determined:
            _remained_char = c
            return False, True
        else:
            return False, False


def handle_keyword(keyword: str):
    pass


def send_error(error: ErrorType, seq, file):
    global _line_idx, _found_error
    error.write_to_file(file, seq, _line_idx)
    _found_error = True


# todo make sure to handle _remained_char while facing errors
def get_next_token(file, error_file) -> (bool, Enum, str):
    global _cur_seq, _remained_char, _line_idx, _found_error, _token_type_determined

    def get_accepted_token(token_type):
        global _cur_seq
        if (token_type is TokenType.ID) and (_cur_seq in keywords_set):
            return False, TokenType.KEYWORD
        return False, token_type

    """initial character"""
    c = _remained_char if len(_remained_char) != 0 else file.read(1)
    if not c:
        return True, TokenType.EOF
    asterisk_flag = False
    if c in asterisk_set:
        asterisk_flag = True

    token_accepted = False
    for token_type in list(TokenType)[:-2]:
        flush()
        read, accepted = scan_process(c, token_type)
        if asterisk_flag:
            read = True
        if accepted:
            _token_type_determined = True
            token_accepted = True
            _cur_seq += c
        else:
            continue
        while read:
            """ scan function is reading, token accepted """
            c = file.read(1)
            if not c:
                if accepted:
                    return get_accepted_token(token_type)
                return True, TokenType.EOF
            read, accepted = scan_process(c, token_type)
            _cur_seq += c
        if _token_type_determined:
            _cur_seq = _cur_seq[0:len(_cur_seq) - len(_remained_char)]
            if asterisk_flag and c in comment_set:
                _remained_char = c
                send_error(ErrorType.UNMATCHED_COMMENT, _cur_seq[:7], error_file)
                return False, TokenType.ERROR
            elif asterisk_flag:
                return False, TokenType.SYMBOL
            if not token_accepted:
                send_error(ErrorType.INVALID_INPUT, _cur_seq, error_file)
                return False, TokenType.ERROR
            if accepted:
                return get_accepted_token(token_type)
            else:
                if token_type is TokenType.COMMENT:
                    send_error(ErrorType.UNCLOSED_COMMENT, _cur_seq[:7], error_file)
                if token_type is TokenType.NUM:
                    send_error(ErrorType.INVALID_NUMBER, _cur_seq + str(_remained_char), error_file)
                return False, TokenType.ERROR


DEBUG = False
_line_idx = 1


def dprint(*string):  # debug print
    global DEBUG
    if DEBUG:
        print(*string)


def run(input_fn: str, tokens_fnf: str, errors_fn: str, symbols_fn: str):
    global DEBUG, _line_idx, _found_error
    _found_error = False
    next_line_flag = True
    printing_started = False
    with open(input_fn, 'r') as input_f, open(tokens_fnf, 'w') as tokens_f, open(errors_fn, 'w') as errors_f, \
            open(symbols_fn, 'w') as symbols_f:
        while True:
            eof, token = get_next_token(input_f, errors_f)
            if not eof:
                if token is TokenType.WHITESPACE and _cur_seq == "\n":
                    next_line_flag = True
                    _line_idx += 1
                if token is TokenType.WHITESPACE or token is TokenType.COMMENT:
                    continue
                if next_line_flag:
                    if printing_started:
                        tokens_f.write('\n{lineno:d}. '.format(lineno=_line_idx))
                    else:
                        tokens_f.write('{lineno:d}. '.format(lineno=_line_idx))
                        printing_started = True
                    next_line_flag = False
                tokens_f.write(str(token).format(seq=_cur_seq) + ' ')
                if token is TokenType.KEYWORD or token is TokenType.ID:
                    symbols_f.write(_cur_seq + ',\n')
            else:
                dprint("End of compilation.")
                if not _found_error:
                    errors_f.write("There is no lexical error.")
                break
        input_f.close()
        tokens_f.close()
        errors_f.close()
        symbols_f.close()
