"""
Command processor - implements each DOS command.
"""
import os
import shutil
import datetime
import sys
from library import LIBRARY, find_command


class CommandProcessor:
    def __init__(self, shell):
        self.shell = shell
        self.terminal = shell.terminal
        self.disk = shell.disk

        # Dispatch table
        self.handlers = {
            "DIR": self.cmd_dir,
            "CD": self.cmd_cd,
            "CHDIR": self.cmd_cd,
            "MD": self.cmd_md,
            "MKDIR": self.cmd_md,
            "RD": self.cmd_rd,
            "RMDIR": self.cmd_rd,
            "DEL": self.cmd_del,
            "ERASE": self.cmd_del,
            "REN": self.cmd_ren,
            "RENAME": self.cmd_ren,
            "TYPE": self.cmd_type,
            "COPY": self.cmd_copy,
            "MOVE": self.cmd_move,
            "CLS": self.cmd_cls,
            "ECHO": self.cmd_echo,
            "SET": self.cmd_set,
            "VER": self.cmd_ver,
            "HELP": self.cmd_help,
            "EXIT": self.cmd_exit,
            "QUIT": self.cmd_exit,
            "DATE": self.cmd_date,
            "TIME": self.cmd_time,
            "PROMPT": self.cmd_prompt,
            "PATH": self.cmd_path,
            "PAUSE": self.cmd_pause,
            "TREE": self.cmd_tree,
        }

    # ---------------- public ----------------
    def execute(self, line: str):
        tokens = self._tokenize(line)
        if not tokens:
            return
        cmd = tokens[0].upper()
        args = tokens[1:]
        # Change drive shortcut: "C:"
        if len(cmd) == 2 and cmd[1] == ":":
            try:
                self.disk.change_drive(cmd)
            except Exception as e:
                self.terminal.error(str(e))
            return
        handler = self.handlers.get(cmd)
        if handler is None:
            self.terminal.print(f"Bad command or file name: {tokens[0]}")
            return
        try:
            handler(args)
        except Exception as e:
            self.terminal.error(str(e))

    # ---------------- helpers ----------------
    @staticmethod
    def _tokenize(line: str):
        """Split respecting double quotes."""
        tokens = []
        buf = []
        in_quote = False
        for ch in line:
            if ch == '"':
                in_quote = not in_quote
            elif ch.isspace() and not in_quote:
                if buf:
                    tokens.append("".join(buf))
                    buf = []
            else:
                buf.append(ch)
        if buf:
            tokens.append("".join(buf))
        return tokens

    def _resolve(self, path):
        """Resolve relative path against cwd (returns DOS path)."""
        if not path:
            return self.disk.cwd
        p = path.replace("/", "\\")
        if len(p) >= 2 and p[1] == ":":
            return p
        if p.startswith("\\"):
            return p
        base = self.disk.cwd.rstrip("\\")
        return base + "\\" + p

    # ---------------- commands ----------------
    def cmd_dir(self, args):
        wide = False
        path = None
        for a in args:
            u = a.upper()
            if u in ("/W", "/-W"):
                wide = u == "/W"
            elif u in ("/P",):
                pass
            elif u.startswith("/"):
                continue
            else:
                path = a
        target = self._resolve(path) if path else self.disk.cwd
        try:
            entries = self.disk.list_dir(target)
        except Exception as e:
            self.terminal.error(str(e))
            return

        drive = self.disk.drive
        label = f" Directory of {drive}{target if target != '\\\\' else '\\\\'}"
        self.terminal.print("")
        self.terminal.print(label)
        self.terminal.print("")
        if not entries:
            self.terminal.print("File Not Found")
            return

        dirs = sorted([e for e in entries if e[1]], key=lambda x: x[0].lower())
        files = sorted([e for e in entries if not e[1]], key=lambda x: x[0].lower())
        ordered = dirs + files

        if wide:
            line = "  "
            col = 0
            for name, is_dir, _ in ordered:
                display = f"[{name}]" if is_dir else name
                if len(display) > 12:
                    display = display[:12]
                if col + 13 > 78:
                    self.terminal.print(line)
                    line = "  "
                    col = 0
                line += display.ljust(13)
                col += 13
            if line.strip():
                self.terminal.print(line)
        else:
            self.terminal.print(f"  {'.'.ljust(10)} {'<DIR>'.rjust(10)}")
            self.terminal.print(f"  {'..'.ljust(10)} {'<DIR>'.rjust(10)}")
            for name, is_dir, size in ordered:
                if is_dir:
                    self.terminal.print(f"  {name[:8].ljust(8)} {'<DIR>'.rjust(10)}")
                else:
                    self.terminal.print(f"  {name[:8].ljust(8)} {size:>10,}")

        total = len(ordered)
        file_count = len(files)
        total_bytes = sum(s for _, d, s in ordered if not d)
        self.terminal.print(f"  {file_count:>5} file(s) {total_bytes:>15,} bytes")
        self.terminal.print(f"  {'':>5} dir(s)")
        self.terminal.print("")

    def cmd_cd(self, args):
        if not args:
            self.terminal.print(self.disk.drive + self.disk.cwd)
            return
        path = args[0]
        if path == ".":
            return
        if path == "..":
            parts = [p for p in self.disk.cwd.split("\\") if p]
            if parts:
                parts.pop()
            self.disk.cwd = "\\" + "\\".join(parts) if parts else "\\"
            real = self.disk.real_path(self.disk.cwd)
            if not os.path.isdir(real):
                self.disk.cwd = "\\"
            return
        self.disk.change_dir(path)

    def cmd_md(self, args):
        if not args:
            self.terminal.print("Required parameter missing")
            return
        for p in args:
            self.disk.make_dir(self._resolve(p))

    def cmd_rd(self, args):
        if not args:
            self.terminal.print("Required parameter missing")
            return
        for p in args:
            self.disk.remove_dir(self._resolve(p))

    def cmd_del(self, args):
        if not args:
            self.terminal.print("Required parameter missing")
            return
        for p in args:
            real = self.disk.real_path(self._resolve(p))
            if os.path.isdir(real):
                self.terminal.error(f"{p} is a directory")
                continue
            if os.path.exists(real):
                os.remove(real)
            else:
                self.terminal.print(f"File not found - {p}")

    def cmd_ren(self, args):
        if len(args) < 2:
            self.terminal.print("Required parameter missing")
            return
        src, dst = args[0], args[1]
        src_real = self.disk.real_path(self._resolve(src))
        if not os.path.exists(src_real):
            self.terminal.print(f"File not found - {src}")
            return
        if "\\" in dst or "/" in dst:
            self.terminal.error("Invalid destination")
            return
        dst_real = os.path.join(os.path.dirname(src_real), dst)
        os.rename(src_real, dst_real)

    def cmd_type(self, args):
        if not args:
            self.terminal.print("Required parameter missing")
            return
        for p in args:
            real = self.disk.real_path(self._resolve(p))
            if not os.path.isfile(real):
                self.terminal.print(f"File not found - {p}")
                continue
            try:
                with open(real, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        self.terminal.write(line)
                self.terminal.print("")
            except Exception as e:
                self.terminal.error(str(e))

    def cmd_copy(self, args):
        if len(args) < 2:
            self.terminal.print("Required parameter missing")
            return
        src, dst = args[0], args[1]
        src_real = self.disk.real_path(self._resolve(src))
        dst_real = self.disk.real_path(self._resolve(dst))
        if os.path.isdir(dst_real):
            dst_real = os.path.join(dst_real, os.path.basename(src_real))
        shutil.copy2(src_real, dst_real)
        self.terminal.print("        1 file(s) copied")

    def cmd_move(self, args):
        if len(args) < 2:
            self.terminal.print("Required parameter missing")
            return
        src, dst = args[0], args[1]
        src_real = self.disk.real_path(self._resolve(src))
        dst_real = self.disk.real_path(self._resolve(dst))
        shutil.move(src_real, dst_real)

    def cmd_cls(self, args):
        self.terminal.clear()

    def cmd_echo(self, args):
        if not args:
            self.terminal.print("ECHO is on.")
            return
        text = " ".join(args)
        if text.upper() in ("ON", "OFF"):
            self.terminal.print(f"ECHO is {text.lower()}.")
            return
        self.terminal.print(text)

    def cmd_set(self, args):
        if not args:
            for k, v in sorted(self.shell.env.items()):
                self.terminal.print(f"{k}={v}")
            return
        text = " ".join(args)
        if "=" in text:
            k, v = text.split("=", 1)
            k = k.strip().upper()
            if v == "":
                self.shell.env.pop(k, None)
            else:
                self.shell.env[k] = v
        else:
            k = text.strip().upper()
            if k in self.shell.env:
                self.terminal.print(f"{k}={self.shell.env[k]}")
            else:
                self.terminal.print(f"Environment variable {k} not defined")

    def cmd_ver(self, args):
        self.terminal.print("")
        self.terminal.print("DOW [Version 1.0.0]")
        self.terminal.print("(DOS on Windows) - Python implementation")
        self.terminal.print("")

    def cmd_help(self, args):
        if not args:
            self.terminal.print("")
            self.terminal.print("For more information on a specific command, type HELP command-name")
            self.terminal.print("")
            for name in sorted(LIBRARY.keys()):
                meta = LIBRARY[name]
                aliases = f"  (alias: {', '.join(meta['aliases'])})" if meta.get("aliases") else ""
                self.terminal.print(f"{name:<10} {meta['desc']}{aliases}")
            self.terminal.print("")
            return
        name = args[0].upper()
        cmd, meta = find_command(name)
        if not meta:
            self.terminal.print(f"No help available for {name}")
            return
        self.terminal.print("")
        self.terminal.print(f"{cmd} - {meta['desc']}")
        if meta.get("aliases"):
            self.terminal.print(f"Aliases: {', '.join(meta['aliases'])}")
        self.terminal.print(f"Usage: {meta['usage']}")
        self.terminal.print("")

    def cmd_exit(self, args):
        self.shell.quit()

    def cmd_date(self, args):
        now = datetime.datetime.now()
        self.terminal.print(f"The current date is: {now.strftime('%a %m/%d/%Y')}")

    def cmd_time(self, args):
        now = datetime.datetime.now()
        self.terminal.print(f"The current time is: {now.strftime('%H:%M:%S.%f')[:-3]}")

    def cmd_prompt(self, args):
        if not args:
            self.terminal.print(f"PROMPT={self.shell.env.get('PROMPT', '$P$G')}")
            return
        self.shell.env["PROMPT"] = " ".join(args)

    def cmd_path(self, args):
        if not args:
            self.terminal.print(f"PATH={self.shell.env.get('PATH', '')}")
            return
        self.shell.env["PATH"] = " ".join(args)

    def cmd_pause(self, args):
        input("Press any key to continue . . .")

    def cmd_tree(self, args):
        path = args[0] if args else self.disk.cwd
        root = self._resolve(path)
        real = self.disk.real_path(root)
        if not os.path.isdir(real):
            self.terminal.print(f"Invalid path - {path}")
            return
        self.terminal.print(f"Directory PATH listing for {self.disk.drive}{root}")
        self.terminal.print("")

        def walk(p, prefix=""):
            entries = sorted(os.listdir(p))
            for i, e in enumerate(entries):
                full = os.path.join(p, e)
                last = i == len(entries) - 1
                conn = "└───" if last else "├───"
                self.terminal.print(prefix + conn + e)
                if os.path.isdir(full):
                    walk(full, prefix + ("    " if last else "│   "))

        walk(real)