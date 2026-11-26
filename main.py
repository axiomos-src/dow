"""
DOW - DOS on Windows
Main entry point
"""
import sys
from dow import DOW


def main():
    try:
        shell = DOW()
        shell.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting DOW...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()