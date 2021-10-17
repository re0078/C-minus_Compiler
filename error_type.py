from enum import Enum


class ErrorType(Enum):
    INVALID_INPUT = (0, "Invalid Input")
    UNCLOSED_COMMENT = (1, "Unclosed Comment")
    UNMATCHED_COMMENT = (2, "Unmatched Comment")
    INVALID_NUMBER = (3, "Invalid Number")

    def write_to_file(self, file, seq, lineno):
        file.write(f"{lineno}.\t({seq},{self.value[1]})\n")
