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
    if c not in valid_chars_set:
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


def send_error(error: ErrorType, error_file):
    global _line_idx, _found_error, _cur_seq, _remained_char
    seq = _cur_seq + _remained_char
    if error != ErrorType.UNCLOSED_COMMENT:
        error.write_to_file(error_file, seq, _line_idx)
    else:
        error.write_to_file(error_file, seq[0:min(len(seq), 7)] + "...", _line_idx)
    _found_error = True
    flush()


# todo make sure to handle _remained_char while facing errors
def get_next_token(file) -> (bool, Enum, ErrorType):
    global _cur_seq, _remained_char, _line_idx, _found_error, _token_type_determined

    def get_accepted_token(token_type):
        global _cur_seq
        if (token_type is TokenType.ID) and (_cur_seq in keywords_set):
            return False, TokenType.KEYWORD, None
        return False, token_type, None

    """initial character"""
    c = _remained_char if len(_remained_char) != 0 else file.read(1)
    if not c:
        return True, TokenType.EOF, None
    asterisk_flag = False
    if c in asterisk_set:
        asterisk_flag = True

    # token_accepted = False
    for token_type in list(TokenType)[:-3]:
        flush()
        read, accepted = scan_process(c, token_type)
        if asterisk_flag:
            read = True
        if accepted:
            _token_type_determined = True
            # token_accepted = True
            _cur_seq += c
        else:
            continue
        while read:
            """ scan function is reading, token accepted """
            c = file.read(1)
            if not c:
                if accepted:
                    return get_accepted_token(token_type)
                return True, TokenType.ERROR, ErrorType.UNCLOSED_COMMENT
            read, accepted = scan_process(c, token_type)
            _cur_seq += c
        if _token_type_determined:
            _cur_seq = _cur_seq[0:len(_cur_seq) - len(_remained_char)]
            if asterisk_flag and c in comment_set:
                _remained_char = c
                return False, TokenType.ERROR, ErrorType.UNMATCHED_COMMENT
            elif asterisk_flag:
                return False, TokenType.SYMBOL, None
            if not accepted:
                return False, TokenType.ERROR, ErrorType.INVALID_INPUT
            if accepted:
                return get_accepted_token(token_type)
            else:
                if token_type is TokenType.NUM:
                    return False, TokenType.ERROR, ErrorType.INVALID_NUMBER
    _remained_char = c
    return False, TokenType.ERROR, ErrorType.INVALID_INPUT


DEBUG = True
_line_idx = 1
_symbol_idx = 1


def dprint(*string):  # debug print
    global DEBUG
    if DEBUG:
        print(*string)


def run(input_fn: str, tokens_fnf: str, errors_fn: str, symbols_fn: str):
    global DEBUG, _line_idx, _found_error, _symbol_idx
    _found_error = False
    next_line_flag = True
    printing_started = False
    with open(input_fn, 'r') as input_f, open(tokens_fnf, 'w') as tokens_f, open(errors_fn, 'w') as errors_f, \
            open(symbols_fn, 'w') as symbols_f:
        while True:
            eof, token, error = get_next_token(input_f)
            if token is TokenType.ERROR:
                send_error(error, errors_f)
                continue
            if not eof:
                if token is TokenType.WHITESPACE and _cur_seq == "\n":
                    next_line_flag = True
                    _line_idx += 1
                if token is TokenType.WHITESPACE or token is TokenType.COMMENT:
                    continue
                if next_line_flag:
                    if printing_started:
                        tokens_f.write('\n{lineno:d}.\t'.format(lineno=_line_idx))
                    else:
                        tokens_f.write('{lineno:d}.\t'.format(lineno=_line_idx))
                        printing_started = True
                    next_line_flag = False
                tokens_f.write(str(token).format(seq=_cur_seq) + ' ')
                if token is TokenType.KEYWORD or token is TokenType.ID:
                    symbols_f.write(f"{_symbol_idx}.\t{_cur_seq},\n")
                    _symbol_idx += 1
            else:
                dprint("End of compilation.")
                if not _found_error:
                    errors_f.write("There is no lexical error.")
                break
        input_f.close()
        tokens_f.close()
        errors_f.close()
        symbols_f.close()
