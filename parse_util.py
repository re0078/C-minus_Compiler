from element_types import ParseToken, ParseRule

parse_table = {
    (ParseToken.PROGRAM, ParseToken.INT): ParseRule.R1.get_prods()[0],
    (ParseToken.PROGRAM, ParseToken.VOID): ParseRule.R1.get_prods()[0],

    (ParseToken.DECLARATION_LIST, ParseToken.INT): ParseRule.R2.get_prods()[0],
    (ParseToken.DECLARATION_LIST, ParseToken.VOID): ParseRule.R2.get_prods()[0],

    (ParseToken.DECLARATION, ParseToken.INT): ParseRule.R3.get_prods()[0],
    (ParseToken.DECLARATION, ParseToken.VOID): ParseRule.R3.get_prods()[0],

    (ParseToken.DECLARATION_INITIAL, ParseToken.INT): ParseRule.R4.get_prods()[0],
    (ParseToken.DECLARATION_INITIAL, ParseToken.VOID): ParseRule.R4.get_prods()[0],

    (ParseToken.DECLARATION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R5.get_prods()[0],
    (ParseToken.DECLARATION_PRIME, ParseToken.SEMICOLON): ParseRule.R5.get_prods()[1],
    (ParseToken.DECLARATION_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R5.get_prods()[1],

    (ParseToken.VAR_DECLARATION_PRIME, ParseToken.SEMICOLON): ParseRule.R6.get_prods()[0],
    (ParseToken.VAR_DECLARATION_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R6.get_prods()[1],

    (ParseToken.FUN_DECLARATION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R7.get_prods()[0],

    (ParseToken.TYPE_SPECIFIER, ParseToken.INT): ParseRule.R8.get_prods()[0],
    (ParseToken.TYPE_SPECIFIER, ParseToken.VOID): ParseRule.R8.get_prods()[1],

    (ParseToken.PARAMS, ParseToken.INT): ParseRule.R9.get_prods()[0],
    (ParseToken.PARAMS, ParseToken.VOID): ParseRule.R9.get_prods()[1],

    (ParseToken.PARAM_LIST, ParseToken.COMMA): ParseRule.R10.get_prods()[0],

    (ParseToken.PARAM, ParseToken.INT): ParseRule.R11.get_prods()[0],
    (ParseToken.PARAM, ParseToken.VOID): ParseRule.R11.get_prods()[0],

    (ParseToken.PARAM_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R12.get_prods()[0],

    (ParseToken.COMPOUND_STMT, ParseToken.BRACE_OPEN): ParseRule.R13.get_prods()[0],

    (ParseToken.STATEMENT_LIST, ParseToken.BREAK): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.SEMICOLON): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.ID): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.PARENTHESIS_OPEN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.NUM): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.IF): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.RETURN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.BRACE_OPEN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.REPEAT): ParseRule.R14.get_prods()[0],

    (ParseToken.STATEMENT, ParseToken.BREAK): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.SEMICOLON): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.ID): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.PARENTHESIS_OPEN): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.NUM): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.BRACE_OPEN): ParseRule.R15.get_prods()[1],
    (ParseToken.STATEMENT, ParseToken.IF): ParseRule.R15.get_prods()[2],
    (ParseToken.STATEMENT, ParseToken.REPEAT): ParseRule.R15.get_prods()[3],
    (ParseToken.STATEMENT, ParseToken.RETURN): ParseRule.R15.get_prods()[4],

    (ParseToken.EXPRESSION_STMT, ParseToken.ID): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.PARENTHESIS_OPEN): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.NUM): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.BREAK): ParseRule.R16.get_prods()[1],
    (ParseToken.EXPRESSION_STMT, ParseToken.SEMICOLON): ParseRule.R16.get_prods()[2],

    (ParseToken.SELECTION_STMT, ParseToken.IF): ParseRule.R17.get_prods()[0],

    (ParseToken.ELSE_STMT, ParseToken.ENDIF): ParseRule.R18.get_prods()[0],
    (ParseToken.ELSE_STMT, ParseToken.ELSE): ParseRule.R18.get_prods()[1],

    (ParseToken.ITERATION_STMT, ParseToken.REPEAT): ParseRule.R19.get_prods()[0],

    (ParseToken.RETURN_STMT, ParseToken.RETURN): ParseRule.R20.get_prods()[0],

    (ParseToken.RETURN_STMT_PRIME, ParseToken.SEMICOLON): ParseRule.R21.get_prods()[0],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.ID): ParseRule.R21.get_prods()[1],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R21.get_prods()[1],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.NUM): ParseRule.R21.get_prods()[1],

    (ParseToken.EXPRESSION, ParseToken.PARENTHESIS_OPEN): ParseRule.R22.get_prods()[0],
    (ParseToken.EXPRESSION, ParseToken.NUM): ParseRule.R22.get_prods()[0],
    (ParseToken.EXPRESSION, ParseToken.ID): ParseRule.R22.get_prods()[1],

    (ParseToken.B, ParseToken.IS): ParseRule.R23.get_prods()[0],
    (ParseToken.B, ParseToken.BRACKET_OPEN): ParseRule.R23.get_prods()[1],
    (ParseToken.B, ParseToken.PARENTHESIS_OPEN): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.ASTERISK): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.MINUS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.PLUS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.LESS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.EQUALS): ParseRule.R23.get_prods()[2],

    (ParseToken.H, ParseToken.IS): ParseRule.R24.get_prods()[0],
    (ParseToken.H, ParseToken.ASTERISK): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.PLUS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.MINUS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.LESS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.EQUALS): ParseRule.R24.get_prods()[1],

    (ParseToken.SIMPLE_EXPRESSION_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R25.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_ZEGOND, ParseToken.NUM): ParseRule.R25.get_prods()[0],

    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.ASTERISK): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.PLUS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.MINUS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.LESS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.EQUALS): ParseRule.R26.get_prods()[0],

    (ParseToken.C, ParseToken.LESS): ParseRule.R27.get_prods()[0],
    (ParseToken.C, ParseToken.EQUALS): ParseRule.R27.get_prods()[0],

    # (ParseToken.RELOP, ParseToken.LESS): ParseRule.R28.get_prods()[0],
    # (ParseToken.RELOP, ParseToken.EQUALS): ParseRule.R28.get_prods()[1],

    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.PARENTHESIS_OPEN): ParseRule.R29.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.ID): ParseRule.R29.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.NUM): ParseRule.R29.get_prods()[0],

    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.ASTERISK): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.PLUS): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.MINUS): ParseRule.R30.get_prods()[0],

    (ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R31.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ParseToken.NUM): ParseRule.R31.get_prods()[0],

    (ParseToken.D, ParseToken.PLUS): ParseRule.R32.get_prods()[0],
    (ParseToken.D, ParseToken.MINUS): ParseRule.R32.get_prods()[0],

    # (ParseToken.ADDOP, ParseToken.PLUS): ParseRule.R33.get_prods()[0],
    # (ParseToken.ADDOP, ParseToken.MINUS): ParseRule.R33.get_prods()[1],

    (ParseToken.TERM, ParseToken.PARENTHESIS_OPEN): ParseRule.R34.get_prods()[0],
    (ParseToken.TERM, ParseToken.ID): ParseRule.R34.get_prods()[0],
    (ParseToken.TERM, ParseToken.NUM): ParseRule.R34.get_prods()[0],

    (ParseToken.TERM_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R35.get_prods()[0],
    (ParseToken.TERM_PRIME, ParseToken.ASTERISK): ParseRule.R35.get_prods()[0],

    (ParseToken.TERM_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R36.get_prods()[0],
    (ParseToken.TERM_ZEGOND, ParseToken.NUM): ParseRule.R36.get_prods()[0],

    (ParseToken.G, ParseToken.ASTERISK): ParseRule.R37.get_prods()[0],

    (ParseToken.FACTOR, ParseToken.PARENTHESIS_OPEN): ParseRule.R38.get_prods()[0],
    (ParseToken.FACTOR, ParseToken.ID): ParseRule.R38.get_prods()[1],
    (ParseToken.FACTOR, ParseToken.NUM): ParseRule.R38.get_prods()[2],

    (ParseToken.VAR_CALL_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R39.get_prods()[0],
    (ParseToken.VAR_CALL_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R39.get_prods()[1],

    (ParseToken.VAR_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R40.get_prods()[0],

    (ParseToken.FACTOR_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R41.get_prods()[0],

    (ParseToken.FACTOR_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R42.get_prods()[0],
    (ParseToken.FACTOR_ZEGOND, ParseToken.NUM): ParseRule.R42.get_prods()[1],

    (ParseToken.ARGS, ParseToken.ID): ParseRule.R43.get_prods()[0],
    (ParseToken.ARGS, ParseToken.PARENTHESIS_OPEN): ParseRule.R43.get_prods()[0],
    (ParseToken.ARGS, ParseToken.NUM): ParseRule.R43.get_prods()[0],

    (ParseToken.ARG_LIST, ParseToken.ID): ParseRule.R44.get_prods()[0],
    (ParseToken.ARG_LIST, ParseToken.PARENTHESIS_OPEN): ParseRule.R44.get_prods()[0],
    (ParseToken.ARG_LIST, ParseToken.NUM): ParseRule.R44.get_prods()[0],

    (ParseToken.ARG_LIST_PRIME, ParseToken.COMMA): ParseRule.R45.get_prods()[0],

}

parse_table = {
    (ParseToken.PROGRAM, ParseToken.INT): ParseRule.R1.get_prods()[0],
    (ParseToken.PROGRAM, ParseToken.VOID): ParseRule.R1.get_prods()[0],

    (ParseToken.DECLARATION_LIST, ParseToken.INT): ParseRule.R2.get_prods()[0],
    (ParseToken.DECLARATION_LIST, ParseToken.VOID): ParseRule.R2.get_prods()[0],

    (ParseToken.DECLARATION, ParseToken.INT): ParseRule.R3.get_prods()[0],
    (ParseToken.DECLARATION, ParseToken.VOID): ParseRule.R3.get_prods()[0],

    (ParseToken.DECLARATION_INITIAL, ParseToken.INT): ParseRule.R4.get_prods()[0],
    (ParseToken.DECLARATION_INITIAL, ParseToken.VOID): ParseRule.R4.get_prods()[0],

    (ParseToken.DECLARATION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R5.get_prods()[0],
    (ParseToken.DECLARATION_PRIME, ParseToken.SEMICOLON): ParseRule.R5.get_prods()[1],
    (ParseToken.DECLARATION_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R5.get_prods()[1],

    (ParseToken.VAR_DECLARATION_PRIME, ParseToken.SEMICOLON): ParseRule.R6.get_prods()[0],
    (ParseToken.VAR_DECLARATION_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R6.get_prods()[1],

    (ParseToken.FUN_DECLARATION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R7.get_prods()[0],

    (ParseToken.TYPE_SPECIFIER, ParseToken.INT): ParseRule.R8.get_prods()[0],
    (ParseToken.TYPE_SPECIFIER, ParseToken.VOID): ParseRule.R8.get_prods()[1],

    (ParseToken.PARAMS, ParseToken.INT): ParseRule.R9.get_prods()[0],
    (ParseToken.PARAMS, ParseToken.VOID): ParseRule.R9.get_prods()[1],

    (ParseToken.PARAM_LIST, ParseToken.COMMA): ParseRule.R10.get_prods()[0],

    (ParseToken.PARAM, ParseToken.INT): ParseRule.R11.get_prods()[0],
    (ParseToken.PARAM, ParseToken.VOID): ParseRule.R11.get_prods()[0],

    (ParseToken.PARAM_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R12.get_prods()[0],

    (ParseToken.COMPOUND_STMT, ParseToken.BRACE_OPEN): ParseRule.R13.get_prods()[0],

    (ParseToken.STATEMENT_LIST, ParseToken.BREAK): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.SEMICOLON): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.ID): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.PARENTHESIS_OPEN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.NUM): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.IF): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.RETURN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.BRACE_OPEN): ParseRule.R14.get_prods()[0],
    (ParseToken.STATEMENT_LIST, ParseToken.REPEAT): ParseRule.R14.get_prods()[0],

    (ParseToken.STATEMENT, ParseToken.BREAK): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.SEMICOLON): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.ID): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.PARENTHESIS_OPEN): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.NUM): ParseRule.R15.get_prods()[0],
    (ParseToken.STATEMENT, ParseToken.BRACE_OPEN): ParseRule.R15.get_prods()[1],
    (ParseToken.STATEMENT, ParseToken.IF): ParseRule.R15.get_prods()[2],
    (ParseToken.STATEMENT, ParseToken.REPEAT): ParseRule.R15.get_prods()[3],
    (ParseToken.STATEMENT, ParseToken.RETURN): ParseRule.R15.get_prods()[4],

    (ParseToken.EXPRESSION_STMT, ParseToken.ID): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.PARENTHESIS_OPEN): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.NUM): ParseRule.R16.get_prods()[0],
    (ParseToken.EXPRESSION_STMT, ParseToken.BREAK): ParseRule.R16.get_prods()[1],
    (ParseToken.EXPRESSION_STMT, ParseToken.SEMICOLON): ParseRule.R16.get_prods()[2],

    (ParseToken.SELECTION_STMT, ParseToken.IF): ParseRule.R17.get_prods()[0],

    (ParseToken.ELSE_STMT, ParseToken.ENDIF): ParseRule.R18.get_prods()[0],
    (ParseToken.ELSE_STMT, ParseToken.ELSE): ParseRule.R18.get_prods()[1],

    (ParseToken.ITERATION_STMT, ParseToken.REPEAT): ParseRule.R19.get_prods()[0],

    (ParseToken.RETURN_STMT, ParseToken.RETURN): ParseRule.R20.get_prods()[0],

    (ParseToken.RETURN_STMT_PRIME, ParseToken.SEMICOLON): ParseRule.R21.get_prods()[0],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.ID): ParseRule.R21.get_prods()[1],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R21.get_prods()[1],
    (ParseToken.RETURN_STMT_PRIME, ParseToken.NUM): ParseRule.R21.get_prods()[1],

    (ParseToken.EXPRESSION, ParseToken.PARENTHESIS_OPEN): ParseRule.R22.get_prods()[0],
    (ParseToken.EXPRESSION, ParseToken.NUM): ParseRule.R22.get_prods()[0],
    (ParseToken.EXPRESSION, ParseToken.ID): ParseRule.R22.get_prods()[1],

    (ParseToken.B, ParseToken.IS): ParseRule.R23.get_prods()[0],
    (ParseToken.B, ParseToken.BRACKET_OPEN): ParseRule.R23.get_prods()[1],
    (ParseToken.B, ParseToken.PARENTHESIS_OPEN): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.ASTERISK): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.MINUS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.PLUS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.LESS): ParseRule.R23.get_prods()[2],
    (ParseToken.B, ParseToken.EQUALS): ParseRule.R23.get_prods()[2],

    (ParseToken.H, ParseToken.IS): ParseRule.R24.get_prods()[0],
    (ParseToken.H, ParseToken.ASTERISK): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.PLUS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.MINUS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.LESS): ParseRule.R24.get_prods()[1],
    (ParseToken.H, ParseToken.EQUALS): ParseRule.R24.get_prods()[1],

    (ParseToken.SIMPLE_EXPRESSION_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R25.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_ZEGOND, ParseToken.NUM): ParseRule.R25.get_prods()[0],

    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.ASTERISK): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.PLUS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.MINUS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.LESS): ParseRule.R26.get_prods()[0],
    (ParseToken.SIMPLE_EXPRESSION_PRIME, ParseToken.EQUALS): ParseRule.R26.get_prods()[0],

    (ParseToken.C, ParseToken.LESS): ParseRule.R27.get_prods()[0],
    (ParseToken.C, ParseToken.EQUALS): ParseRule.R27.get_prods()[0],

    # (ParseToken.RELOP, ParseToken.LESS): ParseRule.R28.get_prods()[0],
    # (ParseToken.RELOP, ParseToken.EQUALS): ParseRule.R28.get_prods()[1],

    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.PARENTHESIS_OPEN): ParseRule.R29.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.ID): ParseRule.R29.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION, ParseToken.NUM): ParseRule.R29.get_prods()[0],

    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.ASTERISK): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.PLUS): ParseRule.R30.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_PRIME, ParseToken.MINUS): ParseRule.R30.get_prods()[0],

    (ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R31.get_prods()[0],
    (ParseToken.ADDITIVE_EXPRESSION_ZEGOND, ParseToken.NUM): ParseRule.R31.get_prods()[0],

    (ParseToken.D, ParseToken.PLUS): ParseRule.R32.get_prods()[0],
    (ParseToken.D, ParseToken.MINUS): ParseRule.R32.get_prods()[0],

    # (ParseToken.ADDOP, ParseToken.PLUS): ParseRule.R33.get_prods()[0],
    # (ParseToken.ADDOP, ParseToken.MINUS): ParseRule.R33.get_prods()[1],

    (ParseToken.TERM, ParseToken.PARENTHESIS_OPEN): ParseRule.R34.get_prods()[0],
    (ParseToken.TERM, ParseToken.ID): ParseRule.R34.get_prods()[0],
    (ParseToken.TERM, ParseToken.NUM): ParseRule.R34.get_prods()[0],

    (ParseToken.TERM_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R35.get_prods()[0],
    (ParseToken.TERM_PRIME, ParseToken.ASTERISK): ParseRule.R35.get_prods()[0],

    (ParseToken.TERM_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R36.get_prods()[0],
    (ParseToken.TERM_ZEGOND, ParseToken.NUM): ParseRule.R36.get_prods()[0],

    (ParseToken.G, ParseToken.ASTERISK): ParseRule.R37.get_prods()[0],

    (ParseToken.FACTOR, ParseToken.PARENTHESIS_OPEN): ParseRule.R38.get_prods()[0],
    (ParseToken.FACTOR, ParseToken.ID): ParseRule.R38.get_prods()[1],
    (ParseToken.FACTOR, ParseToken.NUM): ParseRule.R38.get_prods()[2],

    (ParseToken.VAR_CALL_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R39.get_prods()[0],
    (ParseToken.VAR_CALL_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R39.get_prods()[1],

    (ParseToken.VAR_PRIME, ParseToken.BRACKET_OPEN): ParseRule.R40.get_prods()[0],

    (ParseToken.FACTOR_PRIME, ParseToken.PARENTHESIS_OPEN): ParseRule.R41.get_prods()[0],

    (ParseToken.FACTOR_ZEGOND, ParseToken.PARENTHESIS_OPEN): ParseRule.R42.get_prods()[0],
    (ParseToken.FACTOR_ZEGOND, ParseToken.NUM): ParseRule.R42.get_prods()[1],

    (ParseToken.ARGS, ParseToken.ID): ParseRule.R43.get_prods()[0],
    (ParseToken.ARGS, ParseToken.PARENTHESIS_OPEN): ParseRule.R43.get_prods()[0],
    (ParseToken.ARGS, ParseToken.NUM): ParseRule.R43.get_prods()[0],

    (ParseToken.ARG_LIST, ParseToken.ID): ParseRule.R44.get_prods()[0],
    (ParseToken.ARG_LIST, ParseToken.PARENTHESIS_OPEN): ParseRule.R44.get_prods()[0],
    (ParseToken.ARG_LIST, ParseToken.NUM): ParseRule.R44.get_prods()[0],

    (ParseToken.ARG_LIST_PRIME, ParseToken.COMMA): ParseRule.R45.get_prods()[0],

}

epsilon_set = {
    ParseToken.ARGS: list(),
    ParseToken.ARG_LIST_PRIME: list(),
    ParseToken.DECLARATION_LIST: list(),
    ParseToken.FACTOR_PRIME: list(),
    ParseToken.VAR_PRIME: list(),
    ParseToken.VAR_CALL_PRIME: ParseRule.R39.get_prods()[1],
    ParseToken.B: ParseRule.R23.get_prods()[2],
    ParseToken.C: list(),
    ParseToken.D: list(),
    ParseToken.G: list(),
    ParseToken.H: ParseRule.R24.get_prods()[1],
    ParseToken.TERM_PRIME: ParseRule.R35.get_prods()[0],
    ParseToken.ADDITIVE_EXPRESSION_PRIME: ParseRule.R30.get_prods()[0],
    ParseToken.SIMPLE_EXPRESSION_PRIME: ParseRule.R26.get_prods()[0],
    ParseToken.STATEMENT_LIST: list(),
    ParseToken.PARAM_PRIME: list(),
    ParseToken.PARAM_LIST: list()
}

symbol_str_map = {
    ParseToken.ASTERISK: "*",
    ParseToken.PLUS: "+",
    ParseToken.MINUS: "-",
    ParseToken.LESS: "<",
    ParseToken.EQUALS: "==",
    ParseToken.IS: "=",
    ParseToken.COMMA: ",",
    ParseToken.SEMICOLON: ";",
    ParseToken.PARENTHESIS_OPEN: "(",
    ParseToken.PARENTHESIS_CLOSE: ")",
    ParseToken.BRACE_OPEN: "{",
    ParseToken.BRACE_CLOSE: "}",
    ParseToken.BRACKET_OPEN: "[",
    ParseToken.BRACKET_CLOSE: "]"}
