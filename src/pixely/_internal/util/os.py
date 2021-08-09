# ========================= #
# PIXELY OS UTILITY         #
# ========================= #

import os

def __get_clear_command__():
    return ("clear","cls")[os.name == "nt"]

def get_clear():
    def clear():
        os.system(__get_clear_command__())
    return clear

def get_getch():
    
    if os.name == "nt":
        import msvcrt
        def getch():
            while True:
                try:
                    return msvcrt.getch().decode()
                except UnicodeDecodeError: # A keypress couldn't be decoded, ignore it
                    continue
    else:
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        def getch():
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
    
    return getch