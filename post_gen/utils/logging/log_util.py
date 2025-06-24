import sys
from typing import TextIO

class Logger:
    def __init__(self, label: str):
        self.label = label

    def info(self, msg: str) -> None:
        print(f"{self.label} INFO: {msg}")

    def warn(self, msg: str, file: TextIO = sys.stderr) -> None:
        print(f"{self.label} WARNING: {msg}", file=file)

    def error(self, msg: str, file: TextIO = sys.stderr) -> None:
        print(f"{self.label} ERROR: {msg}", file=file)


def get_label(language: str) -> str:
    if language == "go":
        return f"[🔥Go Fast: post_gen]"
    return f"[🔥post_gen ({language})]"
