from element_types import ActionSymbol, _VARS_OFFSET, _TEMP_OFFSET, _OFFSET_COE

_ADDR_KEY = _OFFSET_KEY = 0
_SCOPE_KEY = _MODE_KEY = 1
_ss = []
_lexeme_map = {}
_val_map = {}
_new_temp = _TEMP_OFFSET - 1
_new_var = _VARS_OFFSET - 1


def push(val):
    _ss.append(val)


def pop():
    val = _ss[-1]
    del _ss[-1]
    return val


def print_info():
    print("# Semantic stack")
    print(_ss)
    print("# PB")
    print(_pb)
    print("# Lexeme map")
    print(_lexeme_map)


def get_addr(lexeme: str) -> int:
    global _new_var
    if lexeme in _lexeme_map.keys():
        return _lexeme_map[lexeme][_ADDR_KEY]
    else:
        _new_var += 1
        _lexeme_map[lexeme] = [_new_var, 0]
        return _new_var


def get_temp():
    global _new_temp
    _new_temp += 1
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
    t = get_temp()
    o1 = pop()
    o2 = pop()
    push(t)
    v1 = get_value(o1)
    v2 = get_value(o2)
    if action == ActionSymbol.ADD:
        _lexeme_map[t] = v1 + v2
    elif action == ActionSymbol.SUB:
        _lexeme_map[t] = v1 - v2
    elif action == ActionSymbol.MULT:
        _lexeme_map[t] = v1 * v2
    elif action == ActionSymbol.LT:
        _lexeme_map[t] = int(v1 < v2)
    else:
        _lexeme_map[t] = int(v1 == v2)
    return o1, o2, t


def assign(declarative: bool, offset: int) -> tuple:
    if declarative:
        o1 = "#0"
    else:
        o1 = pop()
    o2 = pop()
    _lexeme_map[o2 + offset * _OFFSET_COE] = get_value(o1)
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
    global _pb_i, _pb
    routine = _routine_map[action_symbol]
    mode = arg[_MODE_KEY]
    offset = arg[_OFFSET_KEY]
    if routine == assign:
        if mode:
            for i in range(offset):
                res = assign(mode, offset)
                _pb[_pb_i] = (_pb_i, action_symbol, res)
        else:
            res = assign(mode, offset)
            _pb[_pb_i] = (_pb_i, action_symbol, res)
    else:
        if routine == arithmetic:
            res = routine(action_symbol)
        else:
            res = routine()
        _pb[_pb_i] = (_pb_i, action_symbol, res)
