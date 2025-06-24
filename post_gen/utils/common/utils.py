import os

def _term_width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 60

# -------- pretty printing ------------------------------------------ #
def divider(title: str, *, char: str = "=") -> None:
    width = _term_width()
    print("\n" + char * width)
    print(title)
    print(char * width + "\n")