"""
Everything about the **horizontal** border (top / bottom).
"""
import shutil


class BorderBuilder:
    """
    Builds a single horizontal line – optionally centred – that is
    `pattern`-wide and `fraction` of the terminal width.
    """

    def __init__(self, pattern: str = "=", fraction: float = 0.80, center: bool = True):
        self.pattern = pattern
        self.fraction = fraction
        self.center = center

    # ------- public API ------------------------------------------------ #

    def build(self) -> str:
        """Return the fully formed border line."""
        horiz = self._repeat_pattern(self.width)

        if not self.center:
            return horiz

        margin = (self.term_width - self.width) // 2
        return " " * margin + horiz if margin > 0 else horiz

    # ------- internals -------------------------------------------------- #

    @property
    def term_width(self) -> int:
        return max(1, shutil.get_terminal_size(fallback=(80, 24)).columns)

    @property
    def width(self) -> int:
        return max(1, int(self.term_width * self.fraction))

    def _repeat_pattern(self, target: int) -> str:
        if not self.pattern:
            return " " * target
        reps = (target // len(self.pattern)) + 1
        return (self.pattern * reps)[:target]
