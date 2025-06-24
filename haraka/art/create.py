from haraka.art import TextFramer

class Create:
    @staticmethod
    def emoji(art: list[str], align: str = "left") -> None:
        frame = TextFramer(border_char_x="", border_char_y="", padding=0, align=align)
        frame.generate(art)

    @staticmethod
    def ascii(art: list[str], align: str = "left") -> None:
        frame = TextFramer(border_char_x="=", border_char_y="||", padding=2, align=align)
        frame.generate(art)

    @staticmethod
    def logo(art: list[str], align: str = "left") -> None:
        frame = TextFramer(border_char_x="", border_char_y="", padding=2, align=align)
        frame.generate(art)