from element_types import *
from error_type import *
import math

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
    if _token_type_determined and (token_type is TokenType.COMMENT):
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


def send_error(error: ErrorType, error_file, new_line: bool):
    global _line_idx, _found_error, _cur_seq, _remained_char
    seq = _cur_seq + _remained_char
    if error != ErrorType.UNCLOSED_COMMENT:
        error.write_to_file(error_file, seq, _line_idx, new_line)
    else:
        error.write_to_file(error_file, seq[0:min(len(seq), 7)] + "...", _line_idx, new_line)
    _found_error = True
    flush()


# todo make sure to handle _remained_char while facing errors
def get_next_token(file) -> (bool, TokenType, ErrorType):
    global _cur_seq, _remained_char, _line_idx, _found_error, _token_type_determined

    def look_ahead(file, is_asterisk: bool) -> (bool, ErrorType):
        global _cur_seq, _remained_char
        look_ahead_c = file.read(1)
        if not look_ahead_c:
            return True, None
        if look_ahead_c not in valid_chars_set:
            _cur_seq += look_ahead_c
            return False, ErrorType.INVALID_INPUT
        if is_asterisk:
            if look_ahead_c in comment_set:
                _cur_seq += look_ahead_c
                return False, ErrorType.UNMATCHED_COMMENT
            _remained_char = look_ahead_c
            return False, None
        else:
            file.seek(file.tell() - 1, 0)
            if look_ahead_c in asterisk_set.union(comment_set):
                return False, None
            if look_ahead_c in valid_chars_set:
                return False, ErrorType.INVALID_INPUT

    def get_accepted_token(token_type):
        global _cur_seq
        if (token_type is TokenType.ID) and (_cur_seq in keywords_list):
            return False, TokenType.KEYWORD, None
        return False, token_type, None

    """initial character"""
    c = _remained_char if len(_remained_char) != 0 else file.read(1)
    if not c:
        return True, TokenType.EOF, None
    if c in asterisk_set:
        flush()
        _cur_seq += c
        look_ahead_eof, look_ahead_err = look_ahead(file, True)
        if look_ahead_err is None:
            return look_ahead_eof, TokenType.SYMBOL, None
        return look_ahead_eof, TokenType.ERROR, look_ahead_err

    if c in comment_set:
        flush()
        _cur_seq += c
        look_ahead_eof, look_ahead_err = look_ahead(file, False)
        if look_ahead_err is not None:
            return look_ahead_eof, TokenType.ERROR, look_ahead_err

    for token_type in list(TokenType)[:-3]:
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
                return True, TokenType.ERROR, ErrorType.UNCLOSED_COMMENT
            read, accepted = scan_process(c, token_type)
            _cur_seq += c
        if _token_type_determined:
            _cur_seq = _cur_seq[0:len(_cur_seq) - len(_remained_char)]
            if accepted:
                return get_accepted_token(token_type)
            else:
                if token_type is TokenType.NUM:
                    return False, TokenType.ERROR, ErrorType.INVALID_NUMBER
                return False, TokenType.ERROR, ErrorType.INVALID_INPUT
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
    prev_err_line_idx = math.inf
    with open(input_fn, 'r') as input_f, open(tokens_fnf, 'w') as tokens_f, open(errors_fn, 'w') as errors_f, \
            open(symbols_fn, 'w') as symbols_f:
        ids_table = list()
        while True:
            eof, token, error = get_next_token(input_f)
            if token is TokenType.ERROR:
                if _remained_char in next_line_set:
                    _line_idx += 1
                if prev_err_line_idx < _line_idx:
                    errors_f.write("\n")
                    send_error(error, errors_f, True)
                elif prev_err_line_idx == math.inf:
                    send_error(error, errors_f, True)
                else:
                    send_error(error, errors_f, False)
                prev_err_line_idx = _line_idx
                continue
            if not eof:
                if token is TokenType.WHITESPACE and _cur_seq in next_line_set:
                    next_line_flag = True
                    _line_idx += 1
                if token is TokenType.COMMENT and list(next_line_set)[0] in _cur_seq:
                    for _ in range(_cur_seq.count(list(next_line_set)[0])):
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
                if token is TokenType.ID:
                    if _cur_seq not in ids_table:
                        ids_table.append(_cur_seq)
            else:
                dprint("End of compilation.")
                if not _found_error:
                    errors_f.write("There is no lexical error.")
                break
        item_no = 1
        for sym in keywords_list:
            symbols_f.write(f"{item_no}.\t{sym}\n")
            item_no += 1
        for sym in ids_table:
            symbols_f.write(f"{item_no}.\t{sym}\n")
            item_no += 1
        input_f.close()
        tokens_f.close()
        errors_f.close()
        symbols_f.close()
