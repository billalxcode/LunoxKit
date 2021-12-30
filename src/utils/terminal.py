import colorama
import os
import sys

try:
    from src.utils.dateutil import timenow
    from src.utils.banner import random_banner
    from src.core.exceptions import TerminalConsoleException
except ImportError:
    from core.exceptions import TerminalConsoleException
    from utils.dateutil import timenow
    from utils.banner import random_banner

MESSAGE_INFO    = 0
MESSAGE_WARNING = 1
MESSAGE_ERROR   = 2
MESSAGE_NORMAL  = 3

COLOR_RED       = colorama.Fore.RED
COLOR_GREEN     = colorama.Fore.GREEN
COLOR_BLUE      = colorama.Fore.BLUE
COLOR_CYAN      = colorama.Fore.CYAN
COLOR_WHITE     = colorama.Fore.WHITE
COLOR_YELLOW    = colorama.Fore.YELLOW
COLOR_RESET     = colorama.Fore.RESET

class Terminal:
    def __init__(self, environment = None) -> None:
        global MESSAGE_INFO, MESSAGE_ERROR, MESSAGE_NORMAL, MESSAGE_WARNING
        global COLOR_RED,COLOR_GREEN, COLOR_BLUE, COLOR_CYAN, COLOR_WHITE, COLOR_YELLOW, COLOR_RESET
        
        self.RED                = COLOR_RED
        self.GREEN              = COLOR_GREEN
        self.BLUE               = COLOR_BLUE
        self.CYAN               = COLOR_CYAN
        self.WHITE              = COLOR_WHITE
        self.YELLOW             = COLOR_YELLOW
        self.RESET              = COLOR_RESET

        self.MESSAGE_INFO       = MESSAGE_INFO
        self.MESSAGE_WARNING    = MESSAGE_WARNING
        self.MESSAGE_ERROR      = MESSAGE_ERROR
        self.MESSAGE_NORMAL     = MESSAGE_NORMAL

        self.ENVIRONMENT        = environment

    @property
    def info(self):
        return self.MESSAGE_INFO

    @property
    def warning(self):
        return self.MESSAGE_WARNING

    @property
    def error(self):
        return self.MESSAGE_ERROR
    
    @property
    def normal(self):
        return self.MESSAGE_NORMAL

    def execute(self, cmds: str):
        return os.system(cmds)

    def clear(self):
        cmd = ("cls" if os.name == "nt" else "clear")
        return self.execute(cmd)

    def cursor_up(self):
        # Reference: https://stackoverflow.com/questions/5290994/remove-and-replace-printed-items
        sys.stdout.write("\033[F") # Cursor up one line

    def clear_end_line(self):
        sys.stdout.write("\033[K") # CLear end line

    def quit(self):
        # if self.ENVIRONMENT is not None:
        #     self.ENVIRONMENT.close()
        sys.exit()

    def console(self, message: str, message_type: int = 0, includeTime: bool = True, afterQuit: bool = False):
        output = ""
        if includeTime is True:
            output += f"{self.WHITE}[{self.CYAN}{timenow()}{self.WHITE}] "
        if message_type == self.MESSAGE_INFO:
            output += f"{self.WHITE}["
            output += f"{self.GREEN}INFO"
            output += f"{self.WHITE}] "
        elif message_type == self.MESSAGE_WARNING:
            output += f"{self.WHITE}["
            output += f"{self.YELLOW}WARNING"
            output += f"{self.WHITE}] "
        elif message_type == self.MESSAGE_ERROR:
            output += f"{self.WHITE}["
            output += f"{self.RED}ERROR"
            output += f"{self.WHITE}] "
        elif message_type == self.MESSAGE_NORMAL:
            pass
        else:
            raise TerminalConsoleException("Unknown message type")
        output += message
        output += self.RESET
        output += "\n"
        sys.stdout.write(output)
        sys.stdout.flush()
        if afterQuit:
            self.quit()

    def show_banner(self, random: bool = False):
        banner = random_banner()
        self.console(banner, MESSAGE_NORMAL, False)

    def spinner(self, total_spin: int = 100, sec: float = 0.2):
        index = 0
        while index < total_spin:
            self.console(f"")
            
def print(message: str, message_type: int = 0, includeTime: bool = True, afterQuit: bool = False):
    terminal = Terminal()
    terminal.console(message, message_type, includeTime, afterQuit)