import scanner as scanner

input_file_name = "input.txt"
tokens_file_name = "tokens.txt"
errors_file_name = "lexical_errors.txt"
symbols_file_name = "symbol_table.txt"
scanner.run(input_file_name, tokens_file_name, errors_file_name, symbols_file_name)
