import sys
import zipfile
from datetime import datetime
from prettytable import PrettyTable
from threading import Thread
from src.core.handler import RegisterCommand
from src.modules.base.api import BaseAction, BaseModules
from src.utils.terminal import Terminal
from src.utils.utils import isfile, isdir, basename
from src.utils.dateutil import get_timestamp, calculate_worker
from src.utils.terminal import (
    MESSAGE_INFO, MESSAGE_WARNING, MESSAGE_ERROR,
    MESSAGE_NORMAL, COLOR_BLUE, COLOR_CYAN, COLOR_YELLOW,
    COLOR_GREEN, COLOR_RED, COLOR_RESET, COLOR_WHITE,
)
class LocalError(Exception):
    pass

class Core:
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal

        self.FILENAME   = None
        self.WORDLISTS  = []
        self.first_file = None
        self.isrunning  = True
        self.index      = 0
        self.password   = None

        self.ZIP_CORE = None

    def set_filename(self, filename: str):
        self.FILENAME = filename
    
    def set_wordlists(self, wordlists: list):
        self.index = 0
        self.WORDLISTS = wordlists

    def initialize(self):
        self.ZIP_CORE = zipfile.ZipFile(self.FILENAME)
        members = self.ZIP_CORE.filelist
        if len(members) == 0:
            self.terminal.console(f"Bad zip error, code: 1")
            return False
        else:
            self.first_file = members[0].filename
            return True

    def show_pretty(self):
        i = 0
        print ("File list: ")
        tables = PrettyTable(["#", "Filename", "Size", "Date time"])
        for filelist in self.ZIP_CORE.filelist:
            i += 1
            filename = filelist.filename
            filesize = filelist.file_size
            filedate = filelist.date_time
            if filedate is not None:
                dates = f"{filedate[2]}-{filedate[1]}-{filedate[0]}"
            else:
                dates = "Unk"
            tables.add_row([str(i), basename(filename), str(filesize), dates])
        print (tables)

    def process(self):
        while self.isrunning:
            try:
                password = self.WORDLISTS[self.index]
                if isinstance(password, str):
                    password = password.encode()
                self.ZIP_CORE.read(self.first_file, pwd=password)
                self.password = password
                self.isrunning = False
            except: pass
            try:
                if self.index >= len(self.WORDLISTS):
                    self.isrunning = False
                else:
                    self.index += 1
            except IndexError: self.isrunning = False

    def run(self):
        start_time = get_timestamp()
        init_status = self.initialize()
        if init_status is False: self.terminal.quit()
        else:
            th = Thread(target=self.process)
            th.setDaemon(True)
            th.start()

            while th.is_alive():
                print (f"Process index {self.index}/{len(self.WORDLISTS)}")
                self.terminal.cursor_up()
            try:
                th.join()
            except: pass
            print(f"\nTime elapsed: {calculate_worker(start_time)}s")
            if self.password is None:
                self.terminal.console(f"Password not found", self.terminal.warning, False)
                return False
            else:
                self.terminal.console(f"Filename: {self.FILENAME}")
                self.terminal.console(f"Password: {self.password.decode()}")
                self.terminal.console(f"Compress Level: {self.ZIP_CORE.compresslevel}")
                self.show_pretty()
                return True

class Action(BaseAction):
    def __init__(self, terminal: Terminal):
        self.terminal = terminal
        self.core = Core(terminal)

        self.environments = {
            "raw": True,
            "filename": None,
            "pathlist": None,
            # "output": None,
            "wordlist": None,
            "encoding": "utf-8",
            "chunksize": 1024
        }

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
                elif user_argument[0] == "filename":
                    val = user_argument[1]
                    if val.strip() == "":
                        self.terminal.console(f"set <type> <value>", self.terminal.normal, False)
                        return False
                    elif isfile(val):
                        self.environments["filename"] = val
                        return True
                    elif isdir(val):
                        self.terminal.console(f"{val}: is a directory", MESSAGE_NORMAL, False)
                    else:
                        self.terminal.console(f"{val}: No such file or directory", MESSAGE_NORMAL, False)
                        return False
                elif user_argument[0] == "encoding":
                    val = user_argument[1]
                    self.environments["encoding"] = val
                    return True
                elif user_argument[0] == "chunksize":
                    val = user_argument[1]
                    if val.isdigit():
                        self.environments["chunksize"] = int(val)
                        return True
                    else:
                        self.terminal.console(f"Invalid value", MESSAGE_NORMAL, False)
                        return False
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
                    elif environment == "pathlist" or environment == "filename":
                        value += f"{basename(self.environments[environment])}"
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
            self.core.set_filename(self.environments["filename"])
            self.core.set_wordlists(self.environments["wordlist"])
            self.core.run()

class Apps(BaseModules):
    def __init__(self, regcmd: RegisterCommand):
        BaseModules.__init__(self)

        self.AUTHOR = "billalxcode"
        self.VERSION = "1.0"
        self.DESCRIPTION = "Brute Force zip password authentication"
        
        self.action = Action(self.terminal)
        self.regcmd = regcmd

    def initialize(self):
        self.regcmd.register(self.REG)
        self.regcmd.handle(self.REG, "set", self.action.onSet, self.action.dict2tuple(["wordlist"]))
        self.regcmd.handle(self.REG, "options", self.action.onOptions, self.action.dict2tuple())
        self.regcmd.handle(self.REG, "read", self.action.onRead)
        self.regcmd.handle(self.REG, "run", self.action.onRun)