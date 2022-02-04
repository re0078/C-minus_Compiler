# from compiler import send_parser_error
import codegen
from element_types import *
from error_type import ParserErrorType
from parse_util import parse_table, epsilon_set, symbol_str_map
from syncrhonizing import synchronizing_table as st

prediction_table = {}
definite_table = {}
_declaration_flag = False
_array_flag = False


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


def init_parse_table():
    for entry in parse_table.keys():
        sanitized_prod = []
        for prod_i in parse_table[entry]:
            if type(prod_i) != ActionSymbol:
                sanitized_prod.append(prod_i)
        parse_table[entry] = sanitized_prod


error_found = False


def send_parser_error(file, error_type: ParserErrorType, _line_idx: int, info: str):
    global error_found
    error = "\n" if error_found else ""
    error_found = True
    error += f"#{_line_idx} : syntax error, {error_type.value} {info}"
    file.write(error)


scope_stack = []
symbol_table_stack = []
declared_flag = None
declared_name_flag = None
fun_declared_flag = None
var_declared_flag = None


class SymbolStackElementType(Enum):
    REPEAT = 0
    FUNCTION = 1
    VARIABLE_SINGLE = 2
    VARIABLE_ARRAY = 3
    PARAM_SINGLE = 4
    PARAM_ARRAY = 5
    UNKNOWN = 6


def semantic_check(seq: str, current_token, _line_idx, error_file):
    global _declaration_flag, _array_flag, symbol_table_stack
    if seq == str(ParseToken.INT).lower():
        _declaration_flag = True
    if seq == '[':
        _array_flag = True
    construct_sem_sym_table_and_scope_stack(seq, current_token)


_current_type_declared = None
_parameters_expected = None
_new_param_name = None
_new_param_type = None


def construct_sem_sym_table_and_scope_stack(seq, current_token):
    global scope_stack, symbol_table_stack, _current_type_declared, _parameters_expected, _new_param_name, _new_param_type

    # Handle Scope
    if current_token is ParseToken.BRACE_OPEN:
        start_scope_idx = 0
        for idx in range(len(symbol_table_stack), -1, -1):
            if symbol_table_stack[idx][2] is SymbolStackElementType.FUNCTION:
                start_scope_idx = idx
                break
            elif symbol_table_stack[idx][2] is SymbolStackElementType.REPEAT:
                start_scope_idx = idx
                break
        scope_stack.append(start_scope_idx)
    if current_token is ParseToken.BRACE_CLOSE:
        start_scope_idx = scope_stack[-1]
        scope_stack = scope_stack[:-1]
        symbol_table_stack = symbol_table_stack[:start_scope_idx]

    # Handle Function & Variable Declaration
    if _current_type_declared is not None:
        symbol_table_stack.append((seq, _current_type_declared, SymbolStackElementType.UNKNOWN))
        _current_type_declared = None
    if current_token is ParseToken.TYPE_SPECIFIER and _parameters_expected is None:  # just to be run for declarations
        _current_type_declared = seq
    if current_token is ParseToken.VAR_DECLARATION_PRIME:
        prev_dec_idx = 0
        for idx in range(len(symbol_table_stack), -1, -1):
            if symbol_table_stack[idx][2] is SymbolStackElementType.UNKNOWN:
                prev_dec_idx = idx
                break
        if seq == ";":
            symbol_table_stack[prev_dec_idx] = symbol_table_stack[prev_dec_idx][0], symbol_table_stack[prev_dec_idx][
                1], SymbolStackElementType.VARIABLE_SINGLE
        else:
            symbol_table_stack[prev_dec_idx] = symbol_table_stack[prev_dec_idx][0], symbol_table_stack[prev_dec_idx][
                1], SymbolStackElementType.VARIABLE_ARRAY
    if current_token is ParseToken.FUN_DECLARATION_PRIME:
        _parameters_expected = []
        for idx in range(len(symbol_table_stack), -1, -1):
            if symbol_table_stack[idx][2] is SymbolStackElementType.UNKNOWN:
                symbol_table_stack[idx] = symbol_table_stack[idx][0], symbol_table_stack[idx][
                    1], SymbolStackElementType.FUNCTION
                break

    #  Handle Parameters
    if current_token is ParseToken.PARAMS:
        if seq == "void":
            _parameters_expected = None
    if current_token is ParseToken.PARENTHESIS_CLOSE and _parameters_expected is not None:
        _parameters_expected.append((_new_param_name, "int", _new_param_type))
        symbol_table_stack += _parameters_expected
        _parameters_expected = None
        _new_param_name = None
        _new_param_type = None
    if _parameters_expected is not None:
        if current_token is ParseToken.ID:
            _new_param_name = seq
            _new_param_type = SymbolStackElementType.PARAM_SINGLE
        if current_token is ParseToken.BRACE_OPEN:
            _new_param_type = SymbolStackElementType.PARAM_ARRAY
        if current_token is ParseToken.COMMA:
            _parameters_expected.append((_new_param_name, "int", _new_param_type))
            _new_param_name = None
            _new_param_type = None

    # Handle Repeat
    if current_token is ParseToken.REPEAT:
        symbol_table_stack.append((None, None, SymbolStackElementType.REPEAT))


def apply_rule(seq: str, scan_token_type: ScanTokenType, parse_tokens: list, depth: list, parse_tree_f,
               syntax_error_f, _line_idx, tree_entries: list) -> (list, list, bool, bool):
    global _declaration_flag
    parse_token_equivalent = get_parse_token_for_seq(seq, scan_token_type)
    init_token: ParseToken
    init_token = parse_tokens[0]
    if type(init_token) == ActionSymbol:
        init_token: ActionSymbol
        codegen.general_routine(init_token, (_declaration_flag, _array_flag))
        if _declaration_flag:
            _declaration_flag = False
        return parse_tokens[1:], depth[1:], tree_entries, True, False
    semantic_check(seq, parse_tokens[0])
    if scan_token_type == ScanTokenType.ID:
        codegen.push(codegen.get_addr(seq))
    elif scan_token_type == ScanTokenType.NUM:
        codegen.push('#' + seq)
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
            prods: list
            prods = parse_table[pair]
            new_depth = [depth[0] + 1 for _ in prods]
            return apply_rule(seq, scan_token_type, prods.__add__(parse_tokens[1:]), new_depth.__add__(depth[1:]),
                              parse_tree_f, syntax_error_f, _line_idx, tree_entries)
        elif pair[0] in epsilon_set and pair[1] in st[pair[0]]:
            tree_entries.append((str(init_token), depth[0]))
            prods = epsilon_set[init_token]
            if len(prods) == 0:
                tree_entries.append((str(ParseToken.EPSILON).format(seq=seq), depth[0] + 1))
            new_depth = [depth[0] + 1 for _ in prods]
            return prods + parse_tokens[1:], new_depth.__add__(depth[1:]), tree_entries, True, False
        else:
            if (pair[0].get_type() != ParseTokenType.NON_TERMINAL) or (pair[1] in st[pair[0]]):
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
