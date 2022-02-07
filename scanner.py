from element_types import *
from error_type import *

_cur_seq = ""
_remained_char = ""
_cur_state_order = 0
_token_type_determined = False
_output_func = "int prtval; " \
               "void output(int val){" \
               "prtval = val;" \
               "}"
_output_func_it = 0


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
    global _cur_seq, _remained_char, _token_type_determined, _output_func, _output_func_it

    def look_ahead(file, is_asterisk: bool) -> (bool, ScanerErrorType):
        global _cur_seq, _remained_char, _output_func, _output_func_it
        if _output_func_it >= len(_output_func):
            look_ahead_c = file.read(1)
        else:
            look_ahead_c = _output_func[_output_func_it]
            _output_func_it += 1
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
            if _output_func_it >= len(_output_func):
                file.seek(file.tell() - 1, 0)
            else:
                _output_func_it -= 1
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
    if len(_remained_char) != 0:
        c = _remained_char
    else:
        if _output_func_it >= len(_output_func):
            c = file.read(1)
        else:
            c = _output_func[_output_func_it]
            _output_func_it += 1
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
            if _output_func_it >= len(_output_func):
                c = file.read(1)
            else:
                c = _output_func[_output_func_it]
                _output_func_it += 1
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
