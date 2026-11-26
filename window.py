"""
Window / UI helpers for banner and formatting.
"""
import os


class Window:
    def __init__(self):
        self.width = self._detect_width()

    @staticmethod
    def _detect_width() -> int:
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 80

    def show_banner(self):
        banner = r"""
  ____   _____  _    _ 
 |  _ \ / ____|| |  | |
 | | | | |  __ | |  | |
 | |_| | | |_ || |__| |
 |____/ \_____| \____/ 
    DOW - DOS on Windows
    Version 1.0.0
    Type HELP for a list of commands.
"""
        print(banner)

    def horizontal_rule(self, ch="─"):
        print(ch * self.width)

    def box(self, text: str, pad: int = 1):
        line = "┌" + "─" * (len(text) + pad * 2) + "┐"
        mid = "│" + " " * pad + text + " " * pad + "│"
        bot = "└" + "─" * (len(text) + pad * 2) + "┘"
        print(line)
        print(mid)
        print(bot)