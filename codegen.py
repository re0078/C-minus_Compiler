from element_types import ActionSymbol, _VARS_OFFSET, _TEMP_OFFSET, _OFFSET_COE

_ADDR_KEY = _MODE_KEY = 0
_SCOPE_KEY = _OFFSET_KEY = 1
_ss = []
_lexeme_map = {}
_val_map = {}
_new_temp = _TEMP_OFFSET - _OFFSET_COE
_new_var = _VARS_OFFSET - _OFFSET_COE


def push(val):
    global _ss
    _ss.append(val)


def pop():
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


def get_addr(lexeme: str) -> int:
    global _new_var, _ADDR_KEY
    if lexeme in _lexeme_map.keys():
        return _lexeme_map[lexeme][_ADDR_KEY]
    else:
        _new_var += _OFFSET_COE
        _lexeme_map[lexeme] = [_new_var, 0]
        return _new_var


def get_temp():
    global _new_temp
    _new_temp += _OFFSET_COE
    return _new_temp


def get_value(o: str):
    if '#' == o[0]:
        val = int(o[1:])
    elif '?' == o:
        val = -1
    else:
        o = int(o)
        if o >= _VARS_OFFSET:
            val = int(_val_map[o])
        else:
            val = o
    return val


def arithmetic(action: ActionSymbol) -> tuple:
    global _val_map
    t = get_temp()
    o1 = pop()
    o2 = pop()
    push(t)
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
    return o1, o2, t


def assign(declarative: bool, offset: int) -> tuple:
    global _val_map
    if declarative:
        o1 = "#0"
        o2 = pop()
    else:
        o1 = pop()
        if offset <= 1:
            o2 = pop()
        else:
            o2 = 0
    _val_map[o2 + offset] = get_value(o1)
    return o1, o2


def jpf() -> tuple:
    o1 = pop()
    o2 = pop()
    return o1, o2


def jp() -> tuple:
    o1 = pop()
    return o1,


def prt() -> tuple:
    o1 = pop()
    return get_value(o1),


_pb_i = 0
_pb = []
_routine_map = {ActionSymbol.ADD: arithmetic, ActionSymbol.SUB: arithmetic, ActionSymbol.MULT: arithmetic,
                ActionSymbol.LT: arithmetic, ActionSymbol.EQ: arithmetic, ActionSymbol.ASSIGN: assign,
                ActionSymbol.JPF: jpf, ActionSymbol.JP: jp, ActionSymbol.PRINT: prt}


def general_routine(action_symbol: ActionSymbol, arg: tuple = (False, 0)):
    global _pb_i, _pb, _MODE_KEY, _OFFSET_KEY
    routine = _routine_map[action_symbol]
    mode = arg[_MODE_KEY]
    offset = arg[_OFFSET_KEY]
    if routine == assign:
        if mode:
            for i in range(offset):
                res = assign(mode, i * _OFFSET_COE)
                _pb.append((_pb_i, action_symbol, res))
                _pb_i += 1
        else:
            res = assign(mode, offset)
            _pb.append((_pb_i, action_symbol, res))
            _pb_i += 1
    else:
        if routine == arithmetic:
            res = routine(action_symbol)
        else:
            res = routine()
        _pb.append((_pb_i, action_symbol, res))
        _pb_i += 1
