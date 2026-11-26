"""
System-level helpers: platform detection, environment info.
"""
import os
import platform


class SysInfo:
    """Platform/system helpers."""

    @staticmethod
    def platform_name() -> str:
        return platform.system()

    @staticmethod
    def is_windows() -> bool:
        return os.name == "nt"

    @staticmethod
    def os_version() -> str:
        return platform.version()

    @staticmethod
    def python_version() -> str:
        return platform.python_version()

    @staticmethod
    def cwd() -> str:
        return os.getcwd()

    @staticmethod
    def chdir(path: str):
        os.chdir(path)

    @staticmethod
    def env(key: str, default=None):
        return os.environ.get(key, default)

    @staticmethod
    def set_env(key: str, value: str):
        os.environ[key] = value