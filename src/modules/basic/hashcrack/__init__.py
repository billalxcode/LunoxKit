import hashlib
from threading import Thread
from src.modules.base.api import BaseModules
from src.core.handler import RegisterCommand
from src.utils.terminal import Terminal
from src.utils.terminal import MESSAGE_NORMAL, MESSAGE_ERROR, MESSAGE_INFO, MESSAGE_WARNING
from src.utils.terminal import COLOR_RED, COLOR_RESET, COLOR_GREEN, COLOR_CYAN, COLOR_WHITE
from src.utils.utils import isfile, getcwd, basename, isdir
from src.utils.dateutil import get_timestamp, calculate_worker

class LocalError(Exception):
    pass

class Core:
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal

        self.TARGET = None
        self.WORDLISTS = []
        self.ALGORITHM = ["md4", "md5"]
        self.HASHTYPE = self.ALGORITHM[0]

        self.index = 0
        self.threads = []
        self.isrunning = True
        self.dataString = None
        
    def set_target(self, target: str):
        self.TARGET = target

    def set_type(self, type_code: int = 0):
        self.HASHTYPE = self.ALGORITHM[type_code]

    def process(self):
        while self.isrunning:
            password = self.WORDLISTS[self.index]
            hashcore = hashlib.new(self.HASHTYPE)
            hashcore.update(password.encode())
            hashres = hashcore.hexdigest()
            if hashres == self.TARGET:
                self.isrunning = False
                self.dataString = password

            if self.index > len(self.WORDLISTS):
                self.isrunning = False
            else:
                self.index += 1

    def set_wordlist(self, wordlist: list = []):
        self.WORDLISTS = wordlist

    def run(self):
        start_time = get_timestamp()
        self.terminal.console(f"Process target {self.TARGET}, type: {self.HASHTYPE}")
        th = Thread(target=self.process)
        th.setDaemon(True)
        th.start()
        while th.is_alive():
            print (f"\rProcess index {self.index}/{len(self.WORDLISTS)}", end="", flush=True)
        th.join()
        print(f"\nTime elapsed: {calculate_worker(start_time)}s")
        if self.dataString is None:
            self.terminal.console(f"Password not found", self.terminal.warning, False)
            return False
        else:
            self.terminal.console(f"Password found: {self.dataString}", self.terminal.info, False)
            return True

class Action:
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal
        self.core = Core(self.terminal)

        self.environments = {
            "raw": True,
            "type": 0,
            "target": None,
            "pathlist": None,
            "wordlist": None,
            "chunksize": 1024,
            "encoding": "utf-8",
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

    def onSet(self, argument: dict = {}):
        user_argument = argument["user"]
        if user_argument is None:
            self.terminal.console(f"set <type> <value>", self.terminal.normal, False)
            return False
        else:
            argument_length = len(user_argument)
            if argument_length == 0 or argument_length == 1 or argument_length > 3:
                self.terminal.console(f"set <type> <value>", self.terminal.normal, False)
                return False
            else:
                if user_argument[0] == "pathlist":
                    val = user_argument[1]
                    if val.strip() == "":
                        self.terminal.console(f"set <type> <value>", self.terminal.normal, False)
                        return False
                    elif isfile(val):
                        self.environments["pathlist"] = val
                        return True
                    elif isdir(val):
                        self.terminal.console(f"{val}: is a directory", MESSAGE_NORMAL, False)
                    else:
                        self.terminal.console(f"{val}: No such file or directory", MESSAGE_NORMAL, False)
                        return False
                elif user_argument[0] == "target":
                    val = user_argument[1]
                    self.environments["target"] = val
                    return True
                elif user_argument[0] == "raw":
                    val = user_argument[1]
                    if val.lower() == "true" or val == "1":
                        self.environments["raw"] = True
                        return True
                    elif val.lower() == "false" or val == "0":
                        self.environments["raw"] = False
                        return True
                    else:
                        self.terminal.console(f"Invalid value, 'true', 'false', '1', '0'", MESSAGE_NORMAL, False)
                        return False
                elif user_argument[0] == "chunksize":
                    val = user_argument[1]
                    if val.isdigit():
                        self.environments["chunksize"] = int(val)
                        return True
                    else:
                        self.terminal.console(f"Invalid value", MESSAGE_NORMAL, False)
                        return False
                elif user_argument[0] == "encoding":
                    val = user_argument[1]
                    self.environments["encoding"] = val
                    return True
                elif user_argument[0] == "type":
                    val = user_argument[1]
                    if val.isdigit():
                        valint = int(val)
                        if valint > len(self.core.ALGORITHM):
                            self.terminal.console(f"Value a large", MESSAGE_NORMAL, False)
                            return False
                        else:
                            self.environments["type"] = valint
                            return True
                    else:
                        self.terminal.console(f"Invalid value", MESSAGE_NORMAL, False)
                        return False

    def onOptions(self, argument: dict = {}):
        environments = self.environments
        user_argument = argument["user"]
        try:
            if user_argument is None: raise LocalError
            else:
                argument_length = len(user_argument)
                if argument_length == 0 or argument_length > 1:
                    raise LocalError
                else:
                    if user_argument[0] in self.environments:
                        environments = {}
                        environments[user_argument[0]] = self.environments[user_argument[0]]
                        raise LocalError
        except LocalError:
            output = ""
            for environment in environments:
                value = ""
                if self.environments[environment] is None:
                    value += COLOR_RED
                    value += f"{self.environments[environment]}"
                else:
                    value += COLOR_GREEN
                    if environment == "wordlist":
                        value += f"{len(self.environments[environment])}"
                    elif environment == "pathlist":
                        value += f"{basename(self.environments[environment])}"
                    elif environment == "type":
                        value += f"{self.environments[environment]} {COLOR_WHITE}({COLOR_CYAN}{self.core.ALGORITHM[self.environments[environment]]}{COLOR_WHITE})"
                    else:
                        value += f"{self.environments[environment]}"
                value += COLOR_RESET
                output += f"{environment}:{value}"
                output += " " * 4
            self.terminal.console(output, MESSAGE_NORMAL, False)

    def onRead(self, argument: dict = {}):
        if self.environments["pathlist"] is None:
            self.terminal.console(f"Pathlist is not definied", self.terminal.error, False)
        else:
            temp = ""
            chunksize = self.environments["chunksize"]
            encoding = self.environments["encoding"]
            mode = "r"
            if self.environments["raw"] is not True:
                mode += "b"
            with open(self.environments["pathlist"], mode, encoding=encoding) as File:
                while True:
                    data = File.read(chunksize)
                    if not data: break
                    else:
                        temp += data
            self.environments["wordlist"] = temp.splitlines()

    def onRun(self, argument: dict = {}):
        if self.check_isNone() is False: return False
        else:
            if self.environments["wordlist"] is None or len(self.environments["wordlist"]) == 0:
                self.terminal.console(f"Wordlist is empty", MESSAGE_NORMAL, False)
                return False
            else:
                self.core.set_target(self.environments["target"])
                self.core.set_wordlist(self.environments["wordlist"])
                self.core.set_type(self.environments["type"])
                self.core.run()

class Apps(BaseModules):
    def __init__(self, regcmd: RegisterCommand = None) -> None:
        BaseModules.__init__(self)

        self.AUTHOR     = "billalxcode"
        self.VERSION    = "1.0"
        self.LICENSE    = "General Public License v2"
        
        self.action = Action(self.terminal)
        self.regcmd = regcmd
        
    def initialize(self):
        self.regcmd.register(self.REG)
        self.regcmd.handle(self.REG, "set", self.action.onSet, self.action.dict2tuple(["wordlist"]))
        self.regcmd.handle(self.REG, "options", self.action.onOptions, self.action.dict2tuple())
        self.regcmd.handle(self.REG, "read", self.action.onRead)
        self.regcmd.handle(self.REG, "run", self.action.onRun)