from __future__ import annotations
import sys
from typing import TextIO


class Logger:
    def __init__(self, label: str = ""):
        self.label = label

    def start_logger(self) -> Logger:
        label = Logger.get_label(self.label)
        return Logger(label)

    def info(self, msg: str) -> None:
        print(f"{self.label} INFO: {msg}")

    def warn(self, msg: str, file: TextIO = sys.stderr) -> None:
        print(f"{self.label} WARNING: {msg}", file=file)

    def error(self, msg: str, file: TextIO = sys.stderr) -> None:
        print(f"{self.label} ERROR: {msg}", file=file)

    @staticmethod
    def get_label(variant: str) -> str:
        if variant == "go":
            return f"[🔥Go Fast: post_gen]"
        return f"[🔥post_gen ({variant})]"

