"""
Terminal I/O abstraction
"""
import os


class Terminal:
    """Handles input/output for the DOS shell."""

    def __init__(self):
        self.history = []
        self.color = None

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def write(self, text: str):
        print(text, end="")

    def error(self, msg: str):
        print(f"Error: {msg}")

    def read_line(self, prompt: str) -> str:
        """Read a line from user with the given prompt."""
        try:
            line = input(prompt)
        except EOFError:
            return None
        if line.strip():
            self.history.append(line)
        return line

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def gotoxy(self, x: int, y: int):
        """Emulate DOS GOTOXY via ANSI escape."""
        print(f"\033[{y};{x}H", end="")

    def set_color(self, fg=None, bg=None):
        """ANSI color setting (Windows 10+)."""
        codes = []
        if fg is not None:
            codes.append(str(30 + fg))
        if bg is not None:
            codes.append(str(40 + bg))
        if codes:
            print(f"\033[{';'.join(codes)}m", end="")

    def reset_color(self):
        print("\033[0m", end="")