import os
import sys


def getch():
    """
    Function used to get keyboard input https://stackoverflow.com/a/47548992
    """
    if os.name == "nt":
        import msvcrt

        while True:
            try:
                return msvcrt.getch().decode()
            except UnicodeDecodeError:  # A keypress couldn't be decoded, ignore it
                continue
    else:
        import sys, tty, termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def clear():
    """
    Clear the terminal
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\x1b[?25h")
    sys.stdout.flush()
