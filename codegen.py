from element_types import ActionSymbol, _VARS_OFFSET, _TEMP_OFFSET, _OFFSET_COE, BraceElementType, AssignMode

_ADDR_KEY = _MODE_KEY = 0
_AMOUNT_KEY = 1
_ss = []
_lexeme_map = {}
_val_map = {}
_new_temp = _TEMP_OFFSET - _OFFSET_COE
_new_var = _VARS_OFFSET - _OFFSET_COE

_ACTION_KEY, _RES_KEY = 1, 2
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
    global _new_var, _ADDR_KEY, _lexeme_map, _val_map
    pair = (lexeme, scope)
    if pair in _lexeme_map.keys():
        return _lexeme_map[pair][_ADDR_KEY]
    else:
        _new_var += _OFFSET_COE
        _lexeme_map[pair] = [_new_var]
        _val_map[_new_var] = 0
        return _new_var


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
    return [o2, o1, t]


def arithmetic_exec(action: ActionSymbol, params: list):
    global _pb_i
    o1, o2, t = params[0], params[1], params[2]
    v1 = get_value(o1)
    v2 = get_value(o2)
    if action == ActionSymbol.ADD:
        _val_map[t] = v1 + v2
    elif action == ActionSymbol.SUB:
        _val_map[t] = v1 - v2
    elif action == ActionSymbol.MULT:
        _val_map[t] = v1 * v2
    elif action == ActionSymbol.LT:
        _val_map[t] = int(v1 < v2)
    else:
        _val_map[t] = int(v1 == v2)
    _pb_i += 1


def assign(mode, offset: int) -> list:
    if mode == AssignMode.DECLARATION:
        o1 = "#0"
        if offset <= 0:
            o2 = pop_ss()
        else:
            o2 = offset
    else:
        o1 = pop_ss()
        if offset == 0:
            o2 = pop_ss()
        else:
            o2 = offset
        if mode == AssignMode.ARG_VALUING:
            if type(o1) == str and o1[0] == '@':
                o1 = int(o1[1:])
            else:
                o1 = '#' + str(o1)
        if mode == AssignMode.NUM_VALUING:
            o2 = get_temp()
            push_ss(o2)
    return [o1, o2]


def assign_exec(params: list):
    global _val_map, _pb_i
    o1, o2 = params[0], params[1]
    v1 = get_value(o1)
    if type(o2) == str and o2[0] == '@':
        o2 = int(o2[1:])
        o2 = get_value(o2)
    _val_map[o2] = v1
    _pb_i += 1


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
        o1 = params[0]
        if type(o1) == str and '@' == o1[0]:
            o1 = int(o1[1:])
        _pb_i = get_value(o1)
    if action == ActionSymbol.JPF:
        if _val_map[params[0]] == 0:
            o1 = params[1]
            if type(o1) == str and '@' == o1[0]:
                o1 = int(o1[1:])
            _pb_i = get_value(o1)
        else:
            _pb_i += 1


def prt(amount) -> list:
    return [amount, ]


def prt_exec(params: list, expected_f):
    global _val_map, _pb_i
    o1 = get_value(params[0])
    expected_f.write(f"PRINT    {o1}\n")
    _pb_i += 1


def fill_jp(brace_element: tuple):
    global _pb, _MODE_KEY, _AMOUNT_KEY
    be_type, start_line = brace_element[_MODE_KEY], brace_element[_AMOUNT_KEY]
    inst_idx, amount = 0, -1
    if be_type in (BraceElementType.REPEAT, BraceElementType.IF):
        inst_idx, amount = start_line - 1, get_pb_idx()
    if be_type == BraceElementType.MAIN:
        amount = start_line
    _pb[inst_idx][-1][-1] = amount


_routine_map = {ActionSymbol.ADD: arithmetic, ActionSymbol.SUB: arithmetic, ActionSymbol.MULT: arithmetic,
                ActionSymbol.LT: arithmetic, ActionSymbol.EQ: arithmetic, ActionSymbol.ASSIGN: assign,
                ActionSymbol.JPF: jump, ActionSymbol.JP: jump, ActionSymbol.PRINT: prt}

_routine_exec_map = {ActionSymbol.ADD: arithmetic_exec, ActionSymbol.SUB: arithmetic_exec,
                     ActionSymbol.MULT: arithmetic_exec, ActionSymbol.LT: arithmetic_exec,
                     ActionSymbol.EQ: arithmetic_exec, ActionSymbol.ASSIGN: assign_exec,
                     ActionSymbol.JPF: jump_exec, ActionSymbol.JP: jump_exec, ActionSymbol.PRINT: prt_exec}


def general_routine(action_symbol: ActionSymbol, arg: tuple = (None, 0)):
    global _pb_i, _pb, _MODE_KEY, _AMOUNT_KEY
    routine = _routine_map[action_symbol]
    mode = arg[_MODE_KEY]
    amount = arg[_AMOUNT_KEY]
    if routine == assign:
        if mode == AssignMode.ARRAY_DECLARATION:
            amount = max(1, amount)
            base = pop_ss()
            for i in range(amount):
                res = assign(AssignMode.DECLARATION, base + i * _OFFSET_COE)
                push_pb(action_symbol, res)
        elif mode == AssignMode.FUNCTION_CALL:
            res = assign(AssignMode.NUM_VALUING, -1)
            push_pb(action_symbol, res)
            res = assign(AssignMode.ARG_VALUING, 0)
            push_pb(action_symbol, res)
        else:
            res = assign(mode, amount)
            push_pb(action_symbol, res)
    else:
        if routine == jump:
            res = jump(action_symbol, amount)
        elif routine == prt:
            res = routine(amount)
        else:
            res = routine()
        push_pb(action_symbol, res)


def initiation_routine():
    action = ActionSymbol.JP
    res = jump(action, -1)
    push_pb(action, res)


def exec_pb(output_f, expected_f):
    global _pb, _routine_exec_map, _val_map, _pb_i
    _pb_i = 0
    _pb = _pb[:-1]
    while _pb_i < len(_pb):
        routine = _pb[_pb_i]
        action: ActionSymbol
        action = routine[_ACTION_KEY]
        params: list
        params = routine[_RES_KEY]
        exec_routine = _routine_exec_map[action]
        if exec_routine == prt_exec:
            exec_routine(params, expected_f)
        elif exec_routine == assign_exec:
            exec_routine(params)
        else:
            exec_routine(action, params)
    for routine in _pb:
        row_idx = routine[_ADDR_KEY]
        action: ActionSymbol
        action = routine[_ACTION_KEY]
        params: list
        params = routine[_RES_KEY]
        while len(params) < 3:
            params.append(' ')
        output_f.write(f"{row_idx}	({action.name}, {params[0]}, {params[1]}, {params[2]})\n")
