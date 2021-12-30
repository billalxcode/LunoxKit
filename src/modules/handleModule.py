import importlib.util

from src.utils.terminal import Terminal
from src.utils.terminal import MESSAGE_ERROR, MESSAGE_NORMAL
from src.utils.utils import path_join, getcwd, isfile, openfile, isdir

class Handler:
    def __init__(self) -> None:
        self.MODULE_INSTALLED = []
        self.MODULE_DATA = {}
        self.current_module = ""

        self.terminal = Terminal()

    def find_module(self, reg):
        for modules in self.MODULE_INSTALLED:
            try:
                regmod = modules["reg"]
                if reg == regmod:
                    self.MODULE_DATA = modules
                    return True
            except KeyError:
                continue
        return False

    def find_reg(self):
        length = len(self.MODULE_DATA)
        if length == 0:
            return False
        else:
            return self.MODULE_DATA["reg"]

    def find_path(self, current_module):
        PATHS = [
            "src/modules", "modules", "/usr/share/lunoxkit/modules"
        ]

        for path in PATHS:
            join_path = path_join(getcwd(), path, current_module)
            if isdir(join_path):
                return join_path
        return False

    def find_path_with_reg(self, reg):
        for module in self.MODULE_INSTALLED:
            try:
                mdlreg = module["reg"]
                if reg == mdlreg:
                    return module["package"]
            except KeyError: continue
        return False

    def set_current(self, name):
        module_status = self.find_module(name)
        if module_status:
            self.current_module = name
        else:
            self.terminal.console(f"'{name}' module not found", MESSAGE_ERROR)

    def run(self, regcmd):
        module_status = self.find_module(self.current_module)
        if module_status:
            reg = self.find_reg()
            if reg is False:
                return False
            current_module_path = self.find_path_with_reg(reg)
            module_path = self.find_path(current_module_path)
            if module_path is False:
                self.terminal.console(f"'{reg}' module not found", MESSAGE_ERROR)
                return False
            module_path_init = path_join(module_path, "__init__.py")
            if isfile(module_path_init):
                source = openfile(module_path_init, "r")
                spec = importlib.util.spec_from_loader(reg, loader=False)
                mdl = importlib.util.module_from_spec(spec)
                exec(source, mdl.__dict__)
                try:
                    apps = mdl.Apps(regcmd)
                    apps.REG = reg
                    apps.run()
                    return True
                except AttributeError as attr:
                    self.terminal.console(f"Unable to call class 'Apps' on module '{reg}'", MESSAGE_ERROR, False)
                    self.terminal.console(f"Syntax error, message: {attr}", MESSAGE_ERROR, False)
                    return False
                except ImportError as mderr:
                    self.terminal.console(f"Failed to import module '{mderr.name}'", MESSAGE_ERROR, False)
                    return False
            else:
                self.terminal.console(f"Unable open module, file not found.", MESSAGE_ERROR, False)
                return False
        else:
            self.terminal.console(f"'{self.current_module}' module not found", MESSAGE_ERROR)
            return False