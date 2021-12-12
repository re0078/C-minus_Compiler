from element_types import *
from error_type import *
import math
import scanner
import parser

input_file_name = "input.txt"
tokens_file_name = 'tokens.txt'
lexical_errors_file_name = "lexical_errors.txt"
symbols_file_name = 'symbol_table.txt'
parse_tree_file_name = "parse_tree.txt"
syntax_errors_file_name = "syntax_errors.txt"
DEBUG = True
_line_idx = 1
_symbol_idx = 1
_found_error = False


def send_error(error: ErrorType, error_file, new_line: bool, cur_seq: str, remained_char: str):
    global _line_idx, _found_error
    seq = cur_seq + remained_char
    if error != ErrorType.UNCLOSED_COMMENT:
        error.write_to_file(error_file, seq, _line_idx, new_line)
    else:
        error.write_to_file(error_file, seq[0:min(len(seq), 7)] + "...", _line_idx, new_line)
    _found_error = True
    scanner.flush()


def dprint(*string):  # debug print
    global DEBUG
    if DEBUG:
        print(*string)


def run(input_fn: str, tokens_fn: str, lexical_errors_fn: str, symbols_fn: str, parse_tree_fn: str,
        syntax_errors_fn: str):
    global DEBUG, _line_idx, _found_error, _symbol_idx
    _found_error = False
    next_line_flag = True
    printing_started = False
    prev_err_line_idx = math.inf
    with open(input_fn, 'r') as input_f, open(tokens_fn, 'w') as tokens_f, open(lexical_errors_fn, 'w') as \
            lexical_errors_f, open(symbols_fn, 'w') as symbols_f, open(parse_tree_fn, 'w') as parse_tree_f, \
            open(syntax_errors_fn, 'w') as syntax_errors_f:
        ids_table = list()
        parser.build_prediction_table()
        parse_tokens, depth = (ParseRule.R1.get_token(),), [0]
        while True:
            eof, scan_token, error, cur_seq, remained_char = scanner.get_next_token(input_f)
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
                        parse_tokens, depth, epsilon = parser.apply_rule(cur_seq, scan_token, parse_tokens, depth, parse_tree_f)
            else:
                epsilon = True
                tokens_f.write(str(ScanTokenType.EOF).format(seq="$") + ' ')
                dprint("End of compilation.")
                if not _found_error:
                    lexical_errors_f.write("There is no lexical error.")
                while epsilon:
                    parse_tokens, depth, epsilon = parser.apply_rule(cur_seq, scan_token, parse_tokens, depth,
                                                                     parse_tree_f)
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
        lexical_errors_f.close()
        symbols_f.close()


run(input_file_name, tokens_file_name, lexical_errors_file_name, symbols_file_name, parse_tree_file_name,
    syntax_errors_file_name)
