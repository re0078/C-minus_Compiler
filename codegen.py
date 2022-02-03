from element_types import ActionSymbol, _VARS_OFFSET, _TEMP_OFFSET

_ss = []
_val_map = {}
_new_temp = _TEMP_OFFSET - 1


def push(val):
    _ss.append(val)


def pop():
    val = _ss[-1]
    del _ss[-1]
    return val


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


def assign() -> tuple:
    o1 = pop()
    o2 = pop()
    _val_map[o2] = get_value(o1)
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


def general_routine(action_symbol: ActionSymbol):
    global _pb_i, _pb
    routine = _routine_map[action_symbol]
    if routine == arithmetic:
        res = routine(action_symbol)
    else:
        res = routine()
    _pb[_pb_i] = (_pb_i, action_symbol, res)
