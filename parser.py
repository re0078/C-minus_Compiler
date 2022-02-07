# from compiler import send_parser_error
import codegen
from codegen import _OFFSET_COE
from element_types import *
from element_types import SymbolStackElementType
from error_type import ParserErrorType
from parse_util import parse_table, epsilon_set, symbol_str_map
from syncrhonizing import synchronizing_table as st

prediction_table = {}
definite_table = {}
_return_val_address = -1
_scope_stack = [(0, 0)]
_NAME_KEY, _RET_KEY, _TYPE_KEY, _ARGS_COUNT_KEY, _START_LN_KEY = 0, 1, 2, 3, 4
_symbol_table_stack = []
_repeat_jump_state = 0
_finished_brace = False
_MODE_KEY, _AMOUNT_KEY = 0, 1
_assign_flag = [AssignMode.DECLARATION, 0]
_BASE_KEY, _ARG_ORDER_KEY = 1, 2
_selected_func = [None, -1, 1]
_ret_flag = [False, -1]
_print_flag = [False, None]


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


def get_nearest_definition(seq) -> (SymbolStackElementType, int):
    global _symbol_table_stack, _scope_stack
    for idx in range(len(_symbol_table_stack) - 1, -1, -1):
        record = _symbol_table_stack[idx]
        if record[_NAME_KEY] == seq:
            for scope_idx in range(len(_scope_stack) - 1, -1, -1):
                if _scope_stack[scope_idx][0] <= idx:
                    return record[_TYPE_KEY], idx
            break
    return None, _scope_stack[-1][0]


def is_function_param(seq: str, function_name) -> bool:
    global _symbol_table_stack
    element_type, scope = get_nearest_definition(function_name)
    if element_type == SymbolStackElementType.FUNCTION:
        function = _symbol_table_stack[scope]
        for param_idx in range(function[_ARGS_COUNT_KEY]):
            if _symbol_table_stack[scope + param_idx + 1][_NAME_KEY] == seq:
                return True
    return False


def get_current_func():
    global _symbol_table_stack, _scope_stack
    for idx in range(len(_symbol_table_stack) - 1, -1, -1):
        if _symbol_table_stack[idx][_TYPE_KEY] == SymbolStackElementType.FUNCTION and len(_scope_stack) > 1:
            return _symbol_table_stack[idx]
    return None


def handle_arg_valuing():
    global _assign_flag, _selected_func
    _assign_flag[_AMOUNT_KEY] = _selected_func[_BASE_KEY] + _selected_func[_ARG_ORDER_KEY] * _OFFSET_COE
    _selected_func[_ARG_ORDER_KEY] += 1


def check_num_id_for_ss(current_parse_token: ParseToken, seq: str) -> bool:
    global _return_val_address, _scope_stack, _assign_flag, _selected_func, _print_flag
    if current_parse_token in (ParseToken.ID, ParseToken.NUM):
        mode = _assign_flag[_MODE_KEY]
        if mode == AssignMode.ARG_VALUING:
            handle_arg_valuing()
        if current_parse_token == ParseToken.NUM:
            if mode == AssignMode.ARRAY_DECLARATION:
                _assign_flag[1] = int(seq)
            elif mode == AssignMode.ARRAY_VALUING:
                _assign_flag[1] = int(seq)
            else:
                _assign_flag = [AssignMode.NUM_VALUING, -1]
                codegen.push_ss('#' + seq)
        if current_parse_token == ParseToken.ID:
            element_type, scope = get_nearest_definition(seq)
            if mode == AssignMode.DECLARATION:
                if element_type is not None and element_type != SymbolStackElementType.UNKNOWN:
                    return False
                if get_current_func() is None:
                    codegen.get_addr('ret_' + seq, scope)
                    addr = codegen.get_addr(seq, scope)
                    _return_val_address = addr
                else:
                    addr = codegen.get_addr(seq, scope)
                _assign_flag[_AMOUNT_KEY] = addr
                codegen.push_ss(addr)
            if mode == AssignMode.VALUING:
                if element_type is None or element_type == SymbolStackElementType.UNKNOWN:
                    return False
                addr = codegen.get_addr(seq, scope)
                if element_type == SymbolStackElementType.FUNCTION:
                    _selected_func = [seq, addr, _symbol_table_stack[scope][_ARGS_COUNT_KEY]]
                    _assign_flag = [AssignMode.FUNCTION_CALL, addr]
                    codegen.push_ss(addr)
                    codegen.push_ss('#0')
                elif element_type in (SymbolStackElementType.PARAM_ARRAY, SymbolStackElementType.PARAM_SINGLE):
                    if is_function_param(seq, get_current_func()[_NAME_KEY]):
                        _assign_flag = [AssignMode.PARAM_VALUING, 0]
                        indirect_addr = '@' + str(addr)
                        codegen.push_ss(indirect_addr)
                        if _print_flag[0]:
                            _print_flag[1] = indirect_addr
                else:
                    if seq == "prtval":
                        _print_flag[0] = True
                    codegen.push_ss(addr)


def handle_repeat_brace(amount: int) -> int:
    global _repeat_jump_state
    if _repeat_jump_state == 1:
        amount = -1
    if _repeat_jump_state == 2:
        amount = codegen.get_pb_idx() + 2
    _repeat_jump_state = (_repeat_jump_state + 1) % 4
    return amount


def get_func_start_line(scope: int):
    global _scope_stack
    for record in _scope_stack:
        if record[0] == scope:
            return record[1]
    return -1


def handle_action_symbol(action):
    global _brace_list, _return_val_address, _assign_flag, _selected_func, _symbol_table_stack, _print_flag
    if action == ActionSymbol.ASSIGN:
        if _assign_flag[_MODE_KEY] == AssignMode.ARG_VALUING:
            handle_arg_valuing()
    mode, amount = _assign_flag[_MODE_KEY], _assign_flag[_AMOUNT_KEY]
    if action == ActionSymbol.JP or action == ActionSymbol.JPF:
        be_type, amount = _brace_list[-1]
        if be_type == BraceElementType.REPEAT:
            amount = handle_repeat_brace(amount)
        if be_type == BraceElementType.IF:
            amount = -1
        if _selected_func[_NAME_KEY] is not None:
            scope = get_nearest_definition(_selected_func[_NAME_KEY])[1]
            func = _symbol_table_stack[scope]
            amount = func[_START_LN_KEY]
            codegen.push_ss('@' + str(_selected_func[_BASE_KEY]))
            _selected_func = [None, -1, 0]
        if _ret_flag[0]:
            amount = '@' + str(_return_val_address - _OFFSET_COE)
            _ret_flag[0] = False
    codegen.general_routine(action, (mode, amount))
    if action == ActionSymbol.ASSIGN and _print_flag[1] is not None:
        amount = _print_flag[1]
        _print_flag = [False, None]
        codegen.general_routine(ActionSymbol.PRINT, (mode, amount))
    _assign_flag = [AssignMode.VALUING, 0]


def determine_assign_flag(parse_tokens: list):
    global _assign_flag, _return_val_address, _selected_func, _brace_list
    if len(parse_tokens) >= 4 and parse_tokens[:4] == [ParseToken.BRACKET_OPEN, ParseToken.NUM,
                                                       ParseToken.BRACKET_CLOSE, ParseToken.SEMICOLON]:
        _assign_flag = [AssignMode.ARRAY_DECLARATION, -1]
    elif len(parse_tokens) >= 2 and (parse_tokens[:2] == [ParseToken.INT, ParseToken.ID] or
                                     parse_tokens[:2] == [ParseToken.VOID, ParseToken.ID]):
        _assign_flag = [AssignMode.DECLARATION, 0]
    if len(parse_tokens) >= 1 and parse_tokens[:1] == [ParseToken.BRACKET_CLOSE] and \
            _assign_flag[0] != AssignMode.ARRAY_DECLARATION:
        _assign_flag = [AssignMode.ARRAY_VALUING, 0]
    if len(parse_tokens) >= 2 and parse_tokens[:2] == [ActionSymbol.ASSIGN, ActionSymbol.JP]:
        codegen.push_ss(_selected_func[_BASE_KEY] - _OFFSET_COE)
        codegen.push_ss('#' + str(codegen.get_pb_idx() + 2))
    if len(parse_tokens) >= 2 and parse_tokens[:2] == [ActionSymbol.ASSIGN, ParseToken.ARG_LIST_PRIME]:
        _assign_flag = [AssignMode.ARG_VALUING, -1]
    if len(parse_tokens) >= 2 and (parse_tokens[:2] == [ParseToken.RETURN_STMT_PRIME, ActionSymbol.JP]):
        codegen.push_ss('@' + str(_return_val_address))
        _assign_flag = [AssignMode.VALUING, 0]
        _ret_flag[0] = True
    if len(parse_tokens) >= 2 and (parse_tokens[:2] == [ParseToken.BRACE_CLOSE, ParseToken.DECLARATION_LIST]):
        codegen.push_ss('@' + str(_return_val_address))
        _assign_flag = [AssignMode.VALUING, 0]
        _ret_flag[0] = True
        _brace_list.append((BraceElementType.FUNCTION, -1))
        handle_action_symbol(ActionSymbol.JP)


_current_type_declared = None
_parameters_expected = None
_new_param_name = None
_new_param_type = None
_func_declared = False
_brace_func_list = []


def construct_sem_sym_table_and_scope_stack(seq, current_token):
    global _scope_stack, _symbol_table_stack, _current_type_declared, _parameters_expected, _new_param_name, \
        _new_param_type, _func_declared, _brace_func_list, _brace_list, _assign_flag

    # Handle Scope
    if current_token is ParseToken.BRACE_OPEN:
        if _func_declared:
            # start_scope_idx = 0
            # for idx in range(len(_symbol_table_stack) - 1, -1, -1):
            #     if _symbol_table_stack[idx][_TYPE_KEY] is SymbolStackElementType.FUNCTION:
            #         start_scope_idx = idx + 1
            #         break
            # _brace_func_list.append(True)
            # _scope_stack.append((start_scope_idx, codegen.get_pb_idx()))
            _func_declared = False
        else:
            _brace_func_list.append(False)
    if current_token is ParseToken.BRACE_CLOSE:
        if _brace_func_list[-1]:
            start_scope_idx, _ = _scope_stack[-1]
            _scope_stack = _scope_stack[:-1]
            _symbol_table_stack = _symbol_table_stack[:start_scope_idx]
            _brace_list = _brace_list[:-1]
            _assign_flag = [AssignMode.DECLARATION, 0]
        _brace_func_list = _brace_func_list[:-1]

    # Handle Function & Variable Declaration
    if _current_type_declared is not None and current_token == ParseToken.ID:
        _symbol_table_stack.append([seq, _current_type_declared, SymbolStackElementType.UNKNOWN])
        _current_type_declared = None
    if current_token is ParseToken.TYPE_SPECIFIER and _parameters_expected is None:  # just to be run for declarations
        _current_type_declared = seq
    if current_token is ParseToken.VAR_DECLARATION_PRIME:
        prev_dec_idx = 0
        for idx in range(len(_symbol_table_stack) - 1, -1, -1):
            if _symbol_table_stack[idx][_TYPE_KEY] is SymbolStackElementType.UNKNOWN:
                prev_dec_idx = idx
                break
        # TODO check for error b
        if seq == ";":
            _symbol_table_stack[prev_dec_idx][_TYPE_KEY] = SymbolStackElementType.VARIABLE_SINGLE
        else:
            _symbol_table_stack[prev_dec_idx][_TYPE_KEY] = SymbolStackElementType.VARIABLE_ARRAY
    if current_token is ParseToken.FUN_DECLARATION_PRIME:
        _parameters_expected = []
        _func_declared = True
        for idx in range(len(_symbol_table_stack) - 1, -1, -1):
            if _symbol_table_stack[idx][_TYPE_KEY] is SymbolStackElementType.UNKNOWN:
                _symbol_table_stack[idx][_TYPE_KEY] = SymbolStackElementType.FUNCTION
                break
        _brace_func_list.append(True)
        _scope_stack.append([len(_symbol_table_stack), codegen.get_pb_idx()])

    #  Handle Parameters
    if current_token is ParseToken.PARAMS:
        if seq == "void":
            _parameters_expected = None
    if current_token is ParseToken.PARENTHESIS_CLOSE and _parameters_expected is not None:
        _parameters_expected.append([_new_param_name, "int", _new_param_type])
        _symbol_table_stack[-1].append(len(_parameters_expected))
        _symbol_table_stack[-1].append(codegen.get_pb_idx())
        _symbol_table_stack += _parameters_expected
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


_brace_list = []
_new_repeat = False
_new_if = False
_new_else = False


def construct_brace_tracking_stack(current_token):
    global _new_repeat, _new_if, _new_else, _brace_list, _brace_func_list, _finished_brace, _symbol_table_stack, \
        _ret_flag, _assign_flag
    if current_token is ParseToken.BRACE_OPEN:
        _finished_brace = False
        if _brace_func_list[-1]:
            _ret_flag[1] = codegen.get_pb_idx()
            if _symbol_table_stack[-1][_NAME_KEY] == "main":
                codegen.fill_jp((BraceElementType.MAIN, codegen.get_pb_idx()))
            _brace_list.append([BraceElementType.FUNCTION, codegen.get_pb_idx()])
        if _new_repeat:
            _new_repeat = False
        if _new_if:
            _new_if = False
    elif current_token is ParseToken.BRACE_CLOSE:
        _finished_brace = True
        if len(_brace_func_list) == len(_brace_list) == 0:
            _finished_brace = False
    elif current_token is ParseToken.REPEAT:
        _brace_list.append([BraceElementType.REPEAT, codegen.get_pb_idx() + 2])
        _new_repeat = True
    elif _finished_brace and _brace_list[-1][0] == BraceElementType.REPEAT and \
            current_token == ParseToken.STATEMENT_LIST:
        codegen.fill_jp(_brace_list[-1])
        _finished_brace = False
        _brace_list = _brace_list[:-1]
    elif current_token is ParseToken.IF:
        _brace_list.append([BraceElementType.IF, -1])
        _new_if = True
    elif current_token is ParseToken.ELSE_STMT:
        codegen.fill_jp(_brace_list[-1])
        _finished_brace = False
        _brace_list = _brace_list[:-1]
    elif current_token is ParseToken.STATEMENT and _brace_list[-1][0] == BraceElementType.IF \
            and _brace_list[-1][1] == -1:
        _brace_list[-1][1] = codegen.get_pb_idx()


def apply_rule(seq: str, scan_token_type: ScanTokenType, parse_tokens: list, depth: list, parse_tree_f,
               syntax_error_f, _line_idx, tree_entries: list) -> (list, list, bool, bool):
    parse_token_equivalent = get_parse_token_for_seq(seq, scan_token_type)
    init_token: ParseToken
    init_token = parse_tokens[0]
    construct_sem_sym_table_and_scope_stack(seq, init_token)
    determine_assign_flag(parse_tokens)
    check_num_id_for_ss(init_token, seq)
    construct_brace_tracking_stack(init_token)
    if type(init_token) == ActionSymbol:
        handle_action_symbol(init_token)
        return parse_tokens[1:], depth[1:], tree_entries, True, False
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
