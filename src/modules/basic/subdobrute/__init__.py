import requests
from urllib.parse import urlparse
from src.modules.base.api import BaseModules
from src.core.handler import RegisterCommand
from src.utils.terminal import Terminal
from src.utils.terminal import MESSAGE_NORMAL, MESSAGE_ERROR, MESSAGE_INFO, MESSAGE_WARNING
from src.utils.terminal import COLOR_RED, COLOR_RESET, COLOR_GREEN
from src.utils.utils import isfile, getcwd, basename, isdir

class LocalError(Exception):
    pass

class Core:
    def __init__(self, terminal: Terminal) -> None:
        self.TARGET = ""
        self.SCHEMA = "http"
        self.WORDLISTS = []
        self.SUCCESS = []
        self.HEADERS = {
            "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; de) Opera 8.0"
        }
        self.terminal = Terminal()

    def set_schema(self, schema):
        self.SCHEMA = schema

    def set_target(self, target):
        self.TARGET = target

    def set_wordlists(self, wordlists: list = []):
        self.WORDLISTS = wordlists

    def build_url(self, scheme: str, hostname: str, subdomain: str = ""):
        url = ""
        url += scheme
        url += "://"
        if subdomain != "":
            url += subdomain
            url += "."
        url += hostname
        return url

    def process(self):
        HOSTNAME = ""
        urlparser = urlparse(self.TARGET)
        if urlparser.scheme:
            user_input = input(f"Looks like the schema is already defined, do you want to replace it? (Y/n): ")
            if user_input.lower() == "y":
                self.SCHEMA = urlparser.scheme
                HOSTNAME = urlparser.hostname
            else:
                HOSTNAME = urlparser.hostname
        else:
            HOSTNAME = urlparser.path
        index = 0
        for subdo in self.WORDLISTS:
            index += 1
            url = self.build_url(self.SCHEMA, HOSTNAME, subdo)
            print (f"\rRunning test {index}/{len(self.WORDLISTS)}, OK: {len(self.SUCCESS)}", end="")
            try:
                status_code = requests.get(url, headers=self.HEADERS)
                if status_code >= 200 and status_code <= 300:
                    msg = f"\nTesting url '{url}' -> "
                    msg += COLOR_GREEN
                    msg += "OK"
                    self.terminal.console(msg, includeTime=False)
                    self.SUCCESS.append({"url": url, "code": status_code})
            except KeyboardInterrupt: break
            except:
                pass

class Action:
    def __init__(self, terminal: Terminal = None) -> None:
        if terminal is None:
            self.terminal = Terminal()
        else:
            self.terminal = terminal

        self.core = Core(self.terminal)
        self.environments = {
            "raw": True,
            "target": None,
            "pathlist": None,
            "wordlist": None,
            "encoding": "utf-8",
            "schema": "http",
            "chunksize": 1024,
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
                elif user_argument[0] == "schema":
                    val = user_argument[1]
                    self.environments["schema"] = val.lower()
                    return True
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
                    else:
                        value += f"{self.environments[environment]}"
                value += COLOR_RESET
                output += f"{environment}:{value}"
                output += " " * 4
            self.terminal.console(output, MESSAGE_NORMAL, False)

    def onOpen(self, argument: dict = {}):
        pathlist = self.environments["pathlist"]
        if pathlist is None:
            self.terminal.console(f"'pathlist' is not defined", MESSAGE_NORMAL, False)
            return False
        else:
            chunksize = self.environments["chunksize"]
            outputs = ""
            mode = "r"
            if self.environments["raw"] is False:
                mode += "b"
            with open(pathlist, mode, encoding="utf-8") as File:
                while True:
                    data = File.read(chunksize)
                    if not data: break
                    outputs += data
            wordlists = outputs.splitlines()
            self.environments["wordlist"] = wordlists
 
    def run(self, argument: dict = {}):
        if self.check_isNone() is False: return False
        else:
            if self.environments["wordlist"] is None or len(self.environments["wordlist"]) == 0:
                self.terminal.console(f"Wordlist is empty", MESSAGE_NORMAL, False)
                return False
            else:
               self.core.set_target(self.environments["target"])
               self.core.set_wordlists(self.environments["wordlist"])
               self.core.set_schema(self.environments["schema"])
               self.core.process()

class Apps(BaseModules):
    def __init__(self, regcmd: RegisterCommand = None) -> None:
        BaseModules.__init__(self)
        
        self.AUTHOR = "billalxcode"
        self.VERSION = "1.0"
        self.DESCRIPTION = "Fast Subdomain Brute Force"

        self.action = Action(self.terminal)
        self.regcmd = regcmd

    def initialize(self):
        self.regcmd.register(self.REG)
        self.regcmd.handle(self.REG, "set", self.action.onSet, self.action.dict2tuple(["wordlist"]))
        self.regcmd.handle(self.REG, "options", self.action.onOptions, self.action.dict2tuple())
        self.regcmd.handle(self.REG, "read", self.action.onOpen)
        self.regcmd.handle(self.REG, "run", self.action.run)