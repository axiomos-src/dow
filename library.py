"""
Command library - command definitions and help text
"""


LIBRARY = {
    "DIR": {
        "desc": "Display a list of files and subdirectories in a directory.",
        "usage": "DIR [drive:][path][filename] [/A] [/P] [/W]",
        "aliases": [],
    },
    "CD": {
        "desc": "Display the name of or change the current directory.",
        "usage": "CD [drive:][path]  |  CD ..",
        "aliases": ["CHDIR"],
    },
    "MD": {
        "desc": "Create a directory.",
        "usage": "MD [drive:]path",
        "aliases": ["MKDIR"],
    },
    "RD": {
        "desc": "Remove a directory.",
        "usage": "RD [drive:]path",
        "aliases": ["RMDIR"],
    },
    "DEL": {
        "desc": "Delete one or more files.",
        "usage": "DEL [drive:][path]filename",
        "aliases": ["ERASE"],
    },
    "REN": {
        "desc": "Rename a file.",
        "usage": "REN [drive:][path]filename filename",
        "aliases": ["RENAME"],
    },
    "TYPE": {
        "desc": "Display the contents of a text file.",
        "usage": "TYPE [drive:][path]filename",
        "aliases": [],
    },
    "COPY": {
        "desc": "Copy one or more files to another location.",
        "usage": "COPY source destination",
        "aliases": [],
    },
    "MOVE": {
        "desc": "Move files.",
        "usage": "MOVE source destination",
        "aliases": [],
    },
    "CLS": {
        "desc": "Clear the screen.",
        "usage": "CLS",
        "aliases": [],
    },
    "ECHO": {
        "desc": "Display messages or turn command echoing on/off.",
        "usage": "ECHO [ON|OFF|message]",
        "aliases": [],
    },
    "SET": {
        "desc": "Display, set, or remove environment variables.",
        "usage": "SET [variable=[value]]",
        "aliases": [],
    },
    "VER": {
        "desc": "Display the DOS version.",
        "usage": "VER",
        "aliases": [],
    },
    "HELP": {
        "desc": "Display help for a command.",
        "usage": "HELP [command]",
        "aliases": ["?"],
    },
    "EXIT": {
        "desc": "Quit DOW.",
        "usage": "EXIT",
        "aliases": ["QUIT"],
    },
    "DATE": {
        "desc": "Display or set the system date.",
        "usage": "DATE",
        "aliases": [],
    },
    "TIME": {
        "desc": "Display or set the system time.",
        "usage": "TIME",
        "aliases": [],
    },
    "PROMPT": {
        "desc": "Change the command prompt.",
        "usage": "PROMPT [text]",
        "aliases": [],
    },
    "PATH": {
        "desc": "Display or set a search path.",
        "usage": "PATH [path]",
        "aliases": [],
    },
    "PROMPT": {
        "desc": "Change the command prompt.",
        "usage": "PROMPT [text]",
        "aliases": [],
    },
    "PAUSE": {
        "desc": "Suspend processing of a batch file.",
        "usage": "PAUSE",
        "aliases": [],
    },
    "TREE": {
        "desc": "Graphically display directory structure.",
        "usage": "TREE [drive:][path]",
        "aliases": [],
    },
}


def find_command(name: str):
    """Look up a command by name or alias (case-insensitive)."""
    name = name.upper()
    for cmd, meta in LIBRARY.items():
        if cmd == name or name in [a.upper() for a in meta.get("aliases", [])]:
            return cmd, meta
    return None, None