from enum import Enum


class ErrorType(Enum):
    INVALID_INPUT = "Invalid Input"
    UNCLOSED_COMMENT = "Unclosed Comment"
    UNMATCHED_COMMENT = "Unmatched Comment"
    INVALID_NUMBER = "Invalid Number"

    def write_to_file(self, file, seq, lineno):
        file.write(f"{lineno}.\t({seq},{self.value})\n")
