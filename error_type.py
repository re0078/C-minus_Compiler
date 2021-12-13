from enum import Enum


class ScanerErrorType(Enum):
    INVALID_INPUT = "Invalid input"
    UNCLOSED_COMMENT = "Unclosed comment"
    UNMATCHED_COMMENT = "Unmatched comment"
    INVALID_NUMBER = "Invalid number"

    def write_to_file(self, file, seq, lineno, new_line):
        if new_line:
            file.write(f"{lineno}.\t({seq}, {self.value})")
        else:
            file.write(f" ({seq}, {self.value})")


class ParserErrorType(Enum):
    MISSING = "missing"
    ILLEGAL = "illegal"
