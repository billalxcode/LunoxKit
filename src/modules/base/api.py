import os
import sys
from typing import Callable

try:
    from src.utils.terminal import Terminal
    from src.utils.terminal import COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_WHITE, COLOR_RESET, MESSAGE_NORMAL, MESSAGE_WARNING
    from src.core.shell import Shell
    from src.core.handler import RegisterCommand
except ImportError:
    from utils.terminal import Terminal
    from utils.terminal import COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_WHITE, COLOR_RESET, MESSAGE_NORMAL, MESSAGE_WARNING
    from core.shell import Shell
    from core.handler import RegisterCommand

class BaseAction:
    def __init__(self) -> None:
        self.terminal = None
        self.environments = {

        }

    def dict2tuple(self, remove: list = []):
        envlist = list(self.environments)
        if len(remove) == 0:
            return envlist
        for rem in remove:
            envlist.remove(rem)
        return envlist
        
    def check_isNone(self):
        for environment in self.environments:
            if self.environments[environment] is None:
                self.terminal.console(f"'{environment}' is not defined", MESSAGE_NORMAL, False)
                return False
        return True

class BaseModules:
    def __init__(self) -> None:
        self.REG         = ""
        self.AUTHOR      = "unknown"
        self.VERSION     = "unknown"
        self.LICENSE     = "unknown"
        self.DESCRIPTION = ""
        self.WARNING_MSG = None
        self._BANNER     = None
        self.terminal    = Terminal()

    def set_banner_callback(self, callback: Callable):
        self._BANNER = callback

    def run(self):
        if self._BANNER is not None:
            self._BANNER()
        if self.WARNING_MSG is not None:
            self.terminal.console(self.WARNING_MSG, MESSAGE_WARNING, False)
        self.initialize()