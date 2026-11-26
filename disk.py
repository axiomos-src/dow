"""
Virtual disk / drive management
"""
import os


class Disk:
    """Virtual disk with drive letters mapped to real directories."""

    def __init__(self):
        # Map drive letters to real paths (user can change)
        self.drives = {
            "C:": os.path.abspath("."),
            "A:": os.path.abspath("./floppy"),
        }
        self.drive = "C:"
        self.cwd = "\\"
        # Track current real dir per drive for convenience
        self._real_dirs = {"C:": os.path.abspath(".")}

    def real_path(self, path: str) -> str:
        """Convert a DOS path to a real filesystem path."""
        # Normalize separators
        path = path.replace("/", "\\")
        # Handle drive letter
        if len(path) >= 2 and path[1] == ":":
            drive = path[:2].upper() + ":"
            rest = path[2:]
            if drive not in self.drives:
                raise FileNotFoundError(f"Invalid drive: {drive}")
            base = self.drives[drive]
            rest = rest.lstrip("\\")
            return os.path.join(base, rest)
        # Relative to current drive
        base = self.drives.get(self.drive)
        if base is None:
            raise FileNotFoundError(f"Current drive {self.drive} not mapped")
        # Handle absolute DOS paths (leading backslash)
        if path.startswith("\\"):
            path = path[1:]
        return os.path.join(base, path)

    def change_drive(self, drive: str):
        """Change current drive (e.g. 'C:')."""
        drive = drive.upper()
        if len(drive) == 2 and drive[1] == ":":
            drive = drive[0] + ":"
        if drive not in self.drives:
            raise FileNotFoundError(f"Invalid drive: {drive}")
        self.drive = drive
        # Restore previous cwd for that drive if possible
        self.cwd = self._real_dirs.get(drive, "\\")
        if not self.cwd.startswith("\\"):
            self.cwd = "\\" + self.cwd

    def change_dir(self, path: str):
        """Change directory."""
        if not path:
            path = "\\"
        real = self.real_path(path)
        real = os.path.abspath(real)
        if not os.path.isdir(real):
            raise NotADirectoryError(f"Invalid directory: {path}")
        # Store cwd as DOS-style path relative to drive root
        base = self.drives[self.drive]
        rel = os.path.relpath(real, base)
        if rel == ".":
            self.cwd = "\\"
        else:
            self.cwd = "\\" + rel.replace("/", "\\")
        # Remember for this drive
        self._real_dirs[self.drive] = self.cwd

    def make_dir(self, path: str):
        real = self.real_path(path)
        os.makedirs(real, exist_ok=True)

    def remove_dir(self, path: str):
        real = self.real_path(path)
        os.rmdir(real)

    def list_dir(self, path: str = None):
        """Return list of (name, is_dir, size) tuples."""
        real = self.real_path(path) if path else self.real_path(self.cwd)
        if not os.path.isdir(real):
            raise NotADirectoryError(f"Invalid directory: {path or self.cwd}")
        result = []
        for entry in os.listdir(real):
            full = os.path.join(real, entry)
            try:
                size = 0 if os.path.isdir(full) else os.path.getsize(full)
            except OSError:
                size = 0
            result.append((entry, os.path.isdir(full), size))
        return result

    def exists(self, path: str) -> bool:
        try:
            return os.path.exists(self.real_path(path))
        except Exception:
            return False