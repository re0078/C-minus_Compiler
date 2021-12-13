# from compiler import send_parser_error
from element_types import *
from error_type import ParserErrorType
from syncrhonizing import synchronizing_table as st

prediction_table = {}
definite_table = {}


def print_tree_row(info: str, depth: list, parse_tree_f, is_last: bool):
    row = ''
    cur_depth = depth[0]
    if cur_depth > 0:
        for i in range(0, cur_depth - 1):
            if (i + 1) in depth:
                row += '│   '
            else:
                row += '    '
        if is_last:
            row += '└── '
        else:
            row += '├── '
    row += info + '\n'
    parse_tree_f.write(row)


def build_prediction_for_rule(rule: ParseRule):
    global prediction_table, definite_table
    rule_token = rule.get_token()
    prods = rule.get_prods()
    for prod in prods:
        can_loop = True
        prod_item_order = 0
        while can_loop:
            can_loop = False
            init_token: ParseToken
            init_token = prod[prod_item_order]
            if init_token != ParseToken.EPSILON:
                if init_token.get_type() != ParseTokenType.NON_TERMINAL:
                    prediction_table[(rule_token, init_token)] = prod
                    definite_table[(rule_token, init_token)] = True
                else:
                    build_prediction_for_rule(find_rule_by_token(init_token))
                    token: ParseToken
                    for token in ParseToken:
                        pair = (rule_token, token)
                        n_pair = (init_token, token)
                        if token != ParseToken.EPSILON and token.get_type() != ParseTokenType.NON_TERMINAL:
                            if n_pair in definite_table:
                                prediction_table[pair] = prod
                                definite_table[(rule_token, token)] = True
                            elif (init_token, token) in prediction_table.keys():
                                if pair not in prediction_table.keys():
                                    prediction_table[pair] = prod
                    if (init_token, ParseToken.EPSILON) in prediction_table.keys():
                        if prod_item_order == len(prod) - 1:
                            prediction_table[(rule_token, ParseToken.EPSILON)] = prods[0]
                        else:
                            can_loop = True
                            prod_item_order += 1


def build_prediction_table():
    global prediction_table
    rule: ParseRule
    for rule in ParseRule:
        for token in ParseToken:
            if token != ParseToken.EPSILON and token.get_type() != ParseTokenType.NON_TERMINAL and \
                    (ParseToken.EPSILON,) in rule.get_prods():
                prediction_table[(rule.get_token(), token)] = (ParseToken.EPSILON,)
                prediction_table[(rule.get_token(), ParseToken.EPSILON)] = (ParseToken.EPSILON,)
    for rule in ParseRule:
        build_prediction_for_rule(rule)


def send_parser_error(file, error_type: ParserErrorType, _line_idx: int, info: str):
    error = f"#{_line_idx}  : syntax error, {error_type.value} {info}"
    error += "\n"
    file.write(error)


def apply_rule(seq: str, scan_token_type: ScanTokenType, parse_tokens: tuple, depth: list, parse_tree_f,
               syntax_error_f, _line_idx) -> (tuple, list
                                              , bool):
    parse_token_equivalent = get_parse_token_for_seq(seq, scan_token_type)
    init_token: ParseToken
    init_token = parse_tokens[0]
    is_last = (len(depth) == 1 or depth[0] != depth[1])
    if init_token.get_type() != ParseTokenType.NON_TERMINAL and init_token == parse_token_equivalent:
        if parse_token_equivalent == ParseToken.DOLLAR:
            print_tree_row(str(parse_token_equivalent).format(seq=seq), depth, parse_tree_f, is_last)
        else:
            print_tree_row(str(scan_token_type).format(seq=seq), depth, parse_tree_f, is_last)
        return parse_tokens[1:], depth[1:], False, False
    else:
        pair = (init_token, parse_token_equivalent)
        print_tree_row(str(init_token), depth, parse_tree_f, is_last)
        if pair in prediction_table.keys():
            prods: tuple
            prods = prediction_table[pair]
            if prods[0] == ParseToken.EPSILON:
                depth[0] += 1
                print_tree_row(str(ParseToken.EPSILON).format(seq=seq), depth, parse_tree_f, True)
                return parse_tokens[1:], depth[1:], True, False
            else:
                new_depth = [depth[0] + 1 for _ in prods]
                return apply_rule(seq, scan_token_type, prods.__add__(parse_tokens[1:]), new_depth.__add__(depth[1:]),
                                  parse_tree_f, syntax_error_f, _line_idx)
        else:
            if (pair[0].get_type() != ParseTokenType.NON_TERMINAL) or (pair[1] in st[pair[0]]):
                if pair[0].get_type() == ParseTokenType.NON_TERMINAL:
                    info = str(init_token)
                else:
                    if scan_token_type in {ScanTokenType.ID, ScanTokenType.NUM}:
                        info = scan_token_type.name
                    else:
                        info = seq
                send_parser_error(syntax_error_f, ParserErrorType.MISSING, _line_idx, info)
                res = apply_rule(seq, scan_token_type, parse_tokens[1:], depth,
                                 parse_tree_f, syntax_error_f, _line_idx)
                return res[:3] + (True,)
            else:
                # info = str(parse_token_equivalent)
                info = str(parse_token_equivalent).format(seq=seq)
                send_parser_error(syntax_error_f, ParserErrorType.ILLEGAL, _line_idx,
                                  info)
                return parse_tokens, depth, False, True

    # TODO panic-mode and skipping
    # print(f"Error at {seq} and {init_token}")
