from element_types import ActionSymbol, _VARS_OFFSET, _TEMP_OFFSET, _OFFSET_COE, BraceElementType, AssignMode

_ADDR_KEY = _MODE_KEY = 0
_AMOUNT_KEY = 1
_ss = []
_lexeme_map = {}
_val_map = {}
_new_temp = _TEMP_OFFSET - _OFFSET_COE
_new_var = _VARS_OFFSET - _OFFSET_COE

_pb_i = 0
_pb = []


def push_pb(action: ActionSymbol, res: list):
    global _pb, _pb_i
    _pb.append([_pb_i, action, res])
    _pb_i += 1


def get_pb_idx():
    global _pb_i
    return _pb_i


def get_pb():
    global _pb
    return _pb


def push_ss(val):
    global _ss
    _ss.append(val)


def pop_ss():
    global _ss
    val = _ss[-1]
    del _ss[-1]
    return val


def get_ss():
    global _ss
    return _ss


def get_stack_idx():
    global _ss
    return len(_ss)


def print_info():
    print("# Semantic stack")
    print(_ss)
    print("# PB")
    print(_pb)
    print("# Lexeme map")
    print(_lexeme_map)


def get_addr(lexeme: str, scope: int) -> int:
    global _new_var, _ADDR_KEY, _lexeme_map
    pair = (lexeme, scope)
    if pair in _lexeme_map.keys():
        return _lexeme_map[pair][_ADDR_KEY]
    else:
        _new_var += _OFFSET_COE
        _lexeme_map[pair] = [_new_var]
        return _new_var


def addr_exists(lexeme: str, scope: int) -> bool:
    global _lexeme_map
    return (lexeme, scope) in _lexeme_map.keys()


def get_temp():
    global _new_temp
    _new_temp += _OFFSET_COE
    return _new_temp


def get_value(o):
    global _val_map
    if type(o) == int:
        if o >= _VARS_OFFSET:
            val = int(_val_map[o])
        else:
            val = o
    elif '#' in o:
        val = int(o[1:])
    elif '@' in o:
        val = _val_map[_val_map[int(o[1:])]]
    else:
        val = -1
    return val


def arithmetic() -> list:
    global _val_map
    t = get_temp()
    o1 = pop_ss()
    o2 = pop_ss()
    push_ss(t)
    return [o1, o2, t]


def arithmetic_exec(action: ActionSymbol, o1, o2, t):
    v1 = get_value(o1)
    v2 = get_value(o2)
    if action == ActionSymbol.ADD:
        _val_map[t] = v1 + v2
    elif action == ActionSymbol.SUB:
        _val_map[t] = v1 - v2
    elif action == ActionSymbol.MULT:
        _val_map[t] = v1 * v2
    elif action == ActionSymbol.LT:
        _val_map[t] = int(v2 < v1)
    else:
        _val_map[t] = int(v1 == v2)


def assign(mode, offset: int) -> list:
    if mode == AssignMode.DECLARATION:
        o1 = "#0"
        o2 = pop_ss()
    else:
        o1 = pop_ss()
        if offset == 0:
            o2 = pop_ss()
        else:
            o2 = offset
        if mode == AssignMode.PARAM_VALUING:
            o2 = '@' + str(o2)
        if mode == AssignMode.ARG_VALUING:
            o1 = '#' + str(o1)
        if mode == AssignMode.NUM_VALUING:
            o2 = get_temp()
    return [o1, o2]


def assign_exec(o1, o2):
    global _val_map
    v1 = get_value(o1)
    _val_map[o2] = v1


def jump(action: ActionSymbol, line: int) -> list:
    if line == -1:
        line = '?'
    if action == ActionSymbol.JP:
        return [line, ]
    if action == ActionSymbol.JPF:
        o1 = pop_ss()
        return [o1, line]


def jump_exec(action: ActionSymbol, params: list):
    global _pb_i, _val_map
    if action == ActionSymbol.JP:
        _pb_i = params[0]
    if action == ActionSymbol.JPF and _val_map[params[0]] == 0:
        _pb_i = params[1]


def prt() -> tuple:
    o1 = pop_ss()
    return o1,


def prt_exec(o1):
    print(_val_map[o1])


def fill_jp(brace_element: tuple):
    global _pb, _MODE_KEY, _AMOUNT_KEY
    be_type, start_line = brace_element[_MODE_KEY], brace_element[_AMOUNT_KEY]
    inst_idx, amount = 0, -1
    if be_type in (BraceElementType.REPEAT, BraceElementType.IF):
        inst_idx, amount = start_line - 1, get_pb_idx()
    if be_type == BraceElementType.MAIN:
        amount = start_line
    _pb[inst_idx][-1] = amount


_routine_map = {ActionSymbol.ADD: arithmetic, ActionSymbol.SUB: arithmetic, ActionSymbol.MULT: arithmetic,
                ActionSymbol.LT: arithmetic, ActionSymbol.EQ: arithmetic, ActionSymbol.ASSIGN: assign,
                ActionSymbol.JPF: jump, ActionSymbol.JP: jump, ActionSymbol.PRINT: prt}


def general_routine(action_symbol: ActionSymbol, arg: tuple = (None, 0)):
    global _pb_i, _pb, _MODE_KEY, _AMOUNT_KEY
    routine = _routine_map[action_symbol]
    mode = arg[_MODE_KEY]
    amount = arg[_AMOUNT_KEY]
    if routine == assign:
        if mode == AssignMode.ARRAY_DECLARATION:
            amount = max(1, amount)
            for i in range(amount):
                res = assign(mode, i * _OFFSET_COE)
                push_pb(action_symbol, res)
        elif mode == AssignMode.FUNCTION_CALL:
            res = assign(AssignMode.NUM_VALUING, -1)
            push_pb(action_symbol, res)
            push_ss(res[-1])
            res = assign(AssignMode.ARG_VALUING, amount)
            push_pb(action_symbol, res)
        else:
            res = assign(mode, amount * _OFFSET_COE)
            push_pb(action_symbol, res)
    else:
        if routine == jump:
            res = jump(action_symbol, amount)
        else:
            res = routine()
        push_pb(action_symbol, res)


def initiation_routine():
    action = ActionSymbol.JP
    res = jump(action, -1)
    push_pb(action, res)
