"""
DOW core shell class
"""
import os
from terminal import Terminal
from disk import Disk
from commands import CommandProcessor
from window import Window
from library import LIBRARY
import sys as _sys


class DOW:
    """Main DOW shell - orchestrates all components."""

    def __init__(self):
        self.terminal = Terminal()
        self.disk = Disk()
        self.processor = CommandProcessor(self)
        self.window = Window()
        self.running = True
        self.env = {
            "PROMPT": "$P$G",
            "PATH": "C:\\DOS;C:\\",
            "COMSPEC": "C:\\COMMAND.COM",
            "VER": "DOW 1.0",
        }

    def get_prompt(self) -> str:
        """Build the DOS prompt string based on PROMPT env var."""
        cwd = self.disk.cwd
        drive = self.disk.drive
        prompt_tpl = self.env.get("PROMPT", "$P$G")
        result = ""
        i = 0
        while i < len(prompt_tpl):
            ch = prompt_tpl[i]
            if ch == "$" and i + 1 < len(prompt_tpl):
                nxt = prompt_tpl[i + 1]
                if nxt == "P":
                    result += drive + cwd
                elif nxt == "G":
                    result += ">"
                elif nxt == "N":
                    result += drive
                elif nxt == "L":
                    result += "<"
                elif nxt == "B":
                    result += "|"
                elif nxt == "T":
                    from datetime import datetime
                    result += datetime.now().strftime("%H:%M:%S")
                elif nxt == "D":
                    from datetime import datetime
                    result += datetime.now().strftime("%a %m/%d/%Y")
                elif nxt == "$":
                    result += "$"
                else:
                    result += "$" + nxt
                i += 2
            else:
                result += ch
                i += 1
        return result

    def run(self):
        """Main REPL loop."""
        self.window.show_banner()
        while self.running:
            try:
                prompt = self.get_prompt()
                line = self.terminal.read_line(prompt)
                if line is None:
                    continue
                line = line.strip()
                if not line:
                    continue
                self.processor.execute(line)
            except KeyboardInterrupt:
                print("^C")
                continue
            except EOFError:
                self.quit()
            except Exception as e:
                self.terminal.error(str(e))

    def quit(self):
        self.running = False
        self.terminal.print("")
        self.terminal.print("DOW terminated.")