# from compiler import send_parser_error
from element_types import *
from error_type import ParserErrorType
from parse_util import parse_table, epsilon_set, symbol_str_map
from syncrhonizing import synchronizing_table as st

prediction_table = {}
definite_table = {}


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


error_found = False


def send_parser_error(file, error_type: ParserErrorType, _line_idx: int, info: str):
    global error_found
    error = "\n" if error_found else ""
    error_found = True
    error += f"#{_line_idx} : syntax error, {error_type.value} {info}"
    file.write(error)


def apply_rule(seq: str, scan_token_type: ScanTokenType, parse_tokens: tuple, depth: list, parse_tree_f,
               syntax_error_f, _line_idx, tree_entries: list) -> (tuple, list, bool, bool):
    parse_token_equivalent = get_parse_token_for_seq(seq, scan_token_type)
    init_token: ParseToken
    init_token = parse_tokens[0]
    # is_last = (len(depth) == 1 or depth[0] != depth[1])
    if init_token.get_type() != ParseTokenType.NON_TERMINAL and init_token == parse_token_equivalent:
        if parse_token_equivalent == ParseToken.DOLLAR:
            tree_entries.append((str(parse_token_equivalent).format(seq=seq), depth[0]))
            # print_tree_row(str(parse_token_equivalent).format(seq=seq), depth, parse_tree_f, is_last, True)
        else:
            # cur_depth = depth[0]
            # for entry_depth in previous_tree_entries:
            #     if entry_depth == cur_depth:
            #         entry = previous_tree_entries[entry_depth]
            #         for i in range(0, len(entry)):
            #             print_tree_row(entry[i], entry_depth, parse_tree_f, False, False)
            #     elif entry_depth < cur_depth:
            #         entry = previous_tree_entries[entry_depth]
            #         for i in range(0, len(entry)):
            #             print_tree_row(entry[i], entry_depth, parse_tree_f, i == len(entry) - 1, False)
            #     else:
            #         continue
            #     del previous_tree_entries[entry_depth]
            # if cur_depth not in previous_tree_entries.keys():
            #     previous_tree_entries[cur_depth] = []
            # previous_tree_entries[cur_depth].append(str(scan_token_type).format(seq=seq))
            tree_entries.append((str(scan_token_type).format(seq=seq), depth[0]))
            # print_tree_row(str(scan_token_type).format(seq=seq), depth, parse_tree_f, is_last, False)
        return parse_tokens[1:], depth[1:], tree_entries, False, False
    else:
        pair = (init_token, parse_token_equivalent)
        if pair in parse_table.keys():
            tree_entries.append((str(init_token), depth[0]))
            # print_tree_row(str(init_token), depth, parse_tree_f, is_last, False)
            prods: tuple
            prods = parse_table[pair]
            new_depth = [depth[0] + 1 for _ in prods]
            return apply_rule(seq, scan_token_type, prods.__add__(parse_tokens[1:]), new_depth.__add__(depth[1:]),
                              parse_tree_f, syntax_error_f, _line_idx, tree_entries)
        elif pair[0] in epsilon_set and pair[1] in st[pair[0]]:
            tree_entries.append((str(init_token), depth[0]))
            # print_tree_row(str(init_token), depth, parse_tree_f, is_last, False)
            prods = epsilon_set[init_token]
            if len(prods) == 0:
                tree_entries.append((str(ParseToken.EPSILON).format(seq=seq), depth[0] + 1))
                # print_tree_row(str(ParseToken.EPSILON).format(seq=seq), [depth[0] + 1] + depth[1:], parse_tree_f, True,
                #                False)
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

    # TODO panic-mode and skipping
    # print(f"Error at {seq} and {init_token}")
