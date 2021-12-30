import csv
import pathlib
import struct
import socket
import requests
from prettytable import PrettyTable
from threading import Thread
from src.utils.terminal import Terminal
from src.utils.utils import isfile, getcwd, path_join, basename
from src.utils.dateutil import get_timestamp, calculate_worker
from src.modules.base.api import BaseAction, BaseModules
from src.core.handler import RegisterCommand
from src.utils.terminal import (
    MESSAGE_WARNING, MESSAGE_ERROR, MESSAGE_INFO, MESSAGE_NORMAL,
    COLOR_RESET, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_RED,
    COLOR_WHITE, COLOR_YELLOW
)

class LocalError(Exception):
    pass

class Manager:
    def __init__(self, terminal: Terminal = None) -> None:
        # Database: https://github.com/maraisr/ports-list/blob/master/all.csv
        path_cwd = getcwd()
        self.DATABASE_URL = "https://raw.githubusercontent.com/maraisr/ports-list/master/all.csv"
        self.DATABASE_PATH = path_join(path_cwd, "data", "ports-list.csv")
    
        if terminal is None:
            self.terminal = Terminal()
        else:
            self.terminal = terminal

    def default_headers(self):
        HEADERS = {}
        HEADERS["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"
        HEADERS["Connection"] = "keep-alive"
        HEADERS["Referer"] = "https://github.com/maraisr/ports-list/blob/master/all.csv"
        return HEADERS

    def download_database(self):
        urls = self.DATABASE_URL
        path = self.DATABASE_PATH
        self.terminal.console(f"Connecting to github...")
        try:
            req = requests.get(urls, headers=self.default_headers())
            self.terminal.console(f"Downloading file csv...")
            text = req.text
            text = text.replace('"', '')
            text_list = text.splitlines()
            text = "\n".join(text_list[1:])
            with open(path, "w") as File:
                File.write(text)
                File.close()
            self.terminal.console(f"All in done.")
            return True
        except:
            self.terminal.console(f"Failed connect to github, please check your connection.", MESSAGE_ERROR, False)
            return False

    def read_database(self):
        if self.check_files() is True:
            results = []
            with open(self.DATABASE_PATH, "r") as File:    
                csv_reader = csv.reader(File, delimiter=",")
                for row in csv_reader:
                    port_type = row[0]
                    port_number = row[1]
                    port_name = row[2]
                    results.append({"port": int(port_number), "type": port_type, "vendor": port_name})
                return results
        
    def check_files(self):
        if isfile(self.DATABASE_PATH) is not True:
            self.terminal.console(f"Database not found, download from github...", MESSAGE_WARNING)
            download_status = self.download_database()
            return download_status
        else: return True

class Core:
    def __init__(self, terminal: Terminal) -> None:
        self.terminal = terminal

        self.TARGET = ""
        self.PORTS = []
        self.TIMEOUT = 30
        self.FILTERS = {
            "open": True,
            "filtered": True,
            "close": False
        }
        self.DATABASES = []
        self.RESULTS = []
        self.INDEX = 0
        self.isRunning = True

        self.manager = Manager(self.terminal)
        
    def reset(self):
        self.TARGET = ""
        self.PORTS = []
        self.TIMEOUT = 30
        self.FILTERS = {
            "open": True,
            "filtered": True,
            "close": False
        }
        self.DATABASES = []
        self.RESULTS = []
        self.INDEX = 0
        self.isRunning = True

    def set_target(self, target: str):
        self.TARGET = target

    def set_ports(self, ports: list = []):
        self.PORTS = ports

    def set_timeout(self, timeout: int = 30):
        self.TIMEOUT = timeout

    def read_database(self):
        database = self.manager.read_database()
        self.DATABASES = database

    def find_vendor(self, port: int = 80):
        for database in self.DATABASES:
            if port == database["port"]:
                return database["vendor"]
        return "Unknown"

    def show_pretty(self):
        result_length = len(self.RESULTS)
        if result_length == 0:
            self.terminal.console(f"Failed to resolve '{self.TARGET}', no targets were specified.", MESSAGE_WARNING, False)
            return False
        else:
            index = 0
            tables = PrettyTable(["#", "Port", "Vendor", "Status"])
            tables.align["Vendor"] = "l"
            for result in self.RESULTS:
                port = result["port"]
                vendor = result["vendor"]
                if vendor == "Unknown": pass
                status = result["status"]
                isOpen = self.FILTERS["open"]
                isFilter = self.FILTERS["filtered"]
                isClose = self.FILTERS["close"]
                color = ""
                if status == "error": continue
                elif status == "open" and isOpen:
                    index += 1
                    color = COLOR_GREEN
                    rows = [
                        f"{index}", f"{port}", vendor, f"{color}{status}{COLOR_RESET}"
                    ]
                    tables.add_row(rows)
                elif status == "filtered" and isFilter:
                    index += 1
                    color = COLOR_YELLOW
                    rows = [
                        f"{index}", f"{port}", vendor, f"{color}{status}{COLOR_RESET}"
                    ]
                    tables.add_row(rows)
                elif status == "closed" and isClose:
                    index += 1
                    color = COLOR_CYAN
                    rows = [
                        f"{index}", f"{port}", vendor, f"{color}{status}{COLOR_RESET}"
                    ]
                    tables.add_row(rows)
            jsons = []
            if len(jsons) == 1:
                self.terminal.console(f"Failed to resolve '{self.TARGET}', no targets were specified.", MESSAGE_WARNING, False)
                return False
            else:
                self.terminal.console(tables.get_string(), MESSAGE_NORMAL, False)
                return True

    def process(self):
        while self.isRunning:
            try:
                port = self.PORTS[self.INDEX]
            except IndexError: self.isRunning = False
            vendor = self.find_vendor(port)
            data = {}
            data["target"] = self.TARGET
            data["port"] = port
            data["vendor"] = vendor
            try:
                # Reference: https://github.com/m57/piescan/blob/master/piescan.py
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # conn.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.unpack("ii", 1.0))
                conn.settimeout(self.TIMEOUT)
                ret = conn.connect_ex((self.TARGET, port))
                if ret == 0:
                    data["status"] = "open"
                elif ret == 111:
                    data["status"] = "closed"
                elif ret == 11:
                    data["status"] = "filtered"
            except socket.timeout:
                data["status"] = "filtered"
            except Exception as e:
                data["status"] = "error"
                # self.isRunning = False
            self.RESULTS.append(data)
            if self.INDEX >= len(self.PORTS):
                self.isRunning = False
            else:
                self.INDEX += 1

    def run(self):
        start_time = get_timestamp()
        
        self.read_database()
        self.terminal.console(f"Starting scanner {self.TARGET}")
        # self.process()
        th = Thread(target=self.process)
        th.setDaemon(True)
        th.start()
        
        while th.is_alive():
            print (f"Process index {self.INDEX}/{len(self.PORTS)}")
            self.terminal.cursor_up()
        th.join()
        
        self.terminal.clear_end_line()
        print(f"Time elapsed: {calculate_worker(start_time)}s")
        self.show_pretty()

class Action(BaseAction):
    def __init__(self, terminal: Terminal) -> None:
        super().__init__()
        self.terminal = terminal
        self.core = Core(terminal)
        
        self.environments = {
            "target": "localhost",
            "minRange": 0,
            "maxRange": 80,
            "timeout": 30,
            "ports": [],
            "show_open": True,
            "show_filtered": True,
            "show_close": False
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
                if user_argument[0] == "target":
                    val = user_argument[1]
                    if val.strip() == "":
                        self.terminal.console(f"set <type> <value>", self.terminal.normal, False)
                        return False
                    self.environments["target"] = val
                    return True
                elif user_argument[0] == "minRange":
                    val = user_argument[1]
                    if val.isdigit():
                        valint = int(val)
                        self.environments["minRange"] = valint
                        return True
                    else:
                        self.terminal.console(f"Invalid value")
                        return False
                elif user_argument[0] == "maxRange":
                    val = user_argument[1]
                    if val.isdigit():
                        valint = int(val)
                        self.environments["maxRange"] = valint
                        return True
                    else:
                        self.terminal.console(f"Invalid value")
                        return False
                elif user_argument[0] == "show_open" or user_argument[0] == "show_filtered" or user_argument[0] == "show_close":
                    val = user_argument[1]
                    if val.isdigit():
                        if val == "0":
                            self.environments[user_argument[0].lower()] = False
                            return True
                        elif val == "1":
                            self.environments[user_argument[0].lower()] = True
                            return True
                        else:
                            self.environments[user_argument[0].lower()] = False
                            return True
                    else:
                        if val.lower() == "true":
                            self.environments[user_argument[0].lower()] = True
                            return True
                        elif val.lower() == "false":
                            self.environments[user_argument[0].lower()] = False
                            return True
                        else:
                            self.terminal.console(f"Invalid value", MESSAGE_ERROR, False)
                            return False
                elif user_argument[0] == "timeout":
                    val = user_argument[1]
                    if val.isdigit():
                        self.environments["timeout"] = int(val)
                        return True
                    else:
                        self.terminal.console(f"Invalid value", MESSAGE_ERROR, False)
                        return False
                elif user_argument[0] == "range":
                    val = user_argument[1]
                    if "-" in val:
                        split_strip = val.split("-")
                        if len(split_strip) == 2:
                            self.environments["minRange"] = int(split_strip[0])
                            self.environments["maxRange"] = int(split_strip[1])
                            return True
                        else:
                            self.terminal.console(f"Invalid syntax, failed parse min and max range", MESSAGE_ERROR, False)
                            return False
                    else:
                        if val.isdigit():
                            self.environments["minRange"] = 0
                            self.environments["maxRange"] = int(val)

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
                    if environment == "ports":
                        rangeList = self.environments["ports"]
                        if len(rangeList) == 0:
                            value += COLOR_RED
                            value += f"{None}"
                        else:
                            minRange = min(rangeList)
                            maxRange = max(rangeList)
                            join_string = f"{minRange}-{maxRange}"
                            value += f"{join_string}"
                    else:
                        value += f"{self.environments[environment]}"
                value += COLOR_RESET
                output += f"{environment}:{value}"
                output += " " * 4
            self.terminal.console(output, MESSAGE_NORMAL, False)

    def onBuild(self, argument: dict = {}):
        minRange = self.environments["minRange"]
        maxRange = self.environments["maxRange"]
        if minRange > maxRange:
            self.terminal.console(f"Min option is bigger than max opsi option", MESSAGE_WARNING, False)
            return False
        else:
            for x in range(minRange, maxRange):
                self.environments["ports"].append(x + 1)
            self.terminal.console(f"All in done.", MESSAGE_NORMAL, False)
            return True

    def onRun(self, argument: dict = {}):
        if len(self.environments["ports"]) == 0:
            self.terminal.console(f"Ports not defined.", MESSAGE_ERROR, False)
            return False
        if self.environments["target"] is None:
            self.terminal.console(f"'target' is not defined.", MESSAGE_ERROR, False)
            return False
        show_open = self.environments["show_open"]
        show_filter = self.environments["show_filtered"]
        show_close = self.environments["show_close"]
        self.core.reset()
        self.core.FILTERS["open"] = show_open
        self.core.FILTERS["filtered"] = show_filter
        self.core.FILTERS["close"] = show_close
        self.core.set_target(self.environments["target"])
        self.core.set_ports(self.environments["ports"])
        self.core.run()

class Apps(BaseModules):
    def __init__(self, regcmd: RegisterCommand) -> None:
        BaseModules.__init__(self)

        self.AUTHOR = "billalxcode"
        self.VERSION = "1.0"
        self.DESCRIPTION = "Fast ports scanner"

        self.action = Action(self.terminal)
        self.regcmd = regcmd

    def initialize(self):
        self.regcmd.register(self.REG)
        self.regcmd.handle(self.REG, "set", self.action.onSet, self.action.dict2tuple())
        self.regcmd.handle(self.REG, "options", self.action.onOptions, self.action.dict2tuple())
        self.regcmd.handle(self.REG, "build", self.action.onBuild)
        self.regcmd.handle(self.REG, "run", self.action.onRun)