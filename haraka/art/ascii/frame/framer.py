"""
High-level «drop-in» that turns a list[str] into a fully framed banner.
"""
from __future__ import annotations

import shutil
import textwrap
from typing import List

from .border import BorderBuilder


class TextFramer:
    """
    Build a rectangular frame:

      • configurable borders (x / y chars)
      • configurable padding and alignment
      • automatically wraps lines to fit inside

    Example
    -------
    >>> framer = TextFramer(border_char_x="=", border_char_y="|")
    >>> print(framer.frame(["Hello", "world"]))
    """

    def __init__(
        self,
        *,
        border_char_x: str = "=",
        border_char_y: str = "|",
        padding: int = 1,
        align: str = "center",
        border_fraction: float = 0.80,
        center_border: bool = True,
        flex: bool = False,
        art: str = ""
    ):
        self.border_x = border_char_x
        self.border_y = border_char_y
        self.padding = max(0, padding)
        self.align = align.lower()
        self.border_fraction = border_fraction
        self.center_border = center_border
        self.flex = flex

    # ---- public façade ----------------------------------------------- #

    def frame(self, texts: List[str]) -> str:
        """
        Return one string with \n-separated lines ready for printing.
        """
        lines = self._normalise(texts)
        if not lines:
            return ""

        # 1️⃣  build top/bottom borders once
        bb = BorderBuilder(self.border_x, self.border_fraction, self.center_border)
        top_border = bb.build()
        bottom_border = top_border      # symmetrical
        target_width = bb.width
        if self.flex:
            margin = (self.term_width - target_width) // 2 if self.center_border else 0
        else :
            margin = (110 - target_width) // 2 if self.center_border else 0

        # 2️⃣  compute interior geometry
        side = self.border_y or ""
        side_w = len(side)
        interior_w = max(1, target_width - 2 * side_w - 2 * self.padding)

        # 3️⃣  iterate through wrapped chunks
        frame: list[str] = [top_border]
        for logical in lines:
            chunks = textwrap.wrap(logical, width=interior_w) or [""]
            for chunk in chunks:
                frame.append(self._compose_line(chunk, interior_w, side, side_w, margin, target_width))

        frame.append(bottom_border)
        return "\n".join(frame)

    # ---- helpers ------------------------------------------------------ #

    @property
    def term_width(self) -> int:
        return max(1, shutil.get_terminal_size(fallback=(80, 24)).columns)

    @staticmethod
    def _normalise(texts: List[str]):
        text = " ".join(texts)
        return textwrap.dedent(text).strip("\n").splitlines()

    # Build one interior line ------------------------------------------ #
    def _compose_line(
        self,
        chunk: str,
        interior_w: int,
        side: str,
        side_w: int,
        margin: int,
        target_w: int,
    ) -> str:
        extra = interior_w - len(chunk)
        if self.align == "left":
            left_x, right_x = 0, extra
        elif self.align == "right":
            left_x, right_x = extra, 0
        else:                   # centre
            left_x, right_x = divmod(extra, 2)

        left_pad  = " " * (self.padding + left_x)
        right_pad = " " * (self.padding + right_x)
        body = f"{side}{left_pad}{chunk}{right_pad}{side}"

        # pad / trim to exact width
        if len(body) < target_w:
            body = body[:-side_w] + " " * (target_w - len(body)) + body[-side_w:]
        elif len(body) > target_w:
            interior_allowed = target_w - 2 * side_w
            body = f"{side}{body[side_w : side_w + interior_allowed]}{side}"

        return " " * margin + body if margin else body

    def generate(self, texts: List[str]):
        return print(self.frame(texts))
