import sys
import os
from urllib.parse import urlparse
import requests
from colorama import Fore
from utils import createHeaders
from prettytable import PrettyTable

moduleDir = os.path.join(os.getcwd())
sys.path.insert(0, moduleDir)
from utils import createHeaders

class AdminFinder:
    def __init__(self) -> None:
        from src.terminal import Terminal
        from src.wordlist import Wordlist
        from src.handler import Handler

        self.terminal = Terminal()
        self.wordlist = Wordlist()
        self.handler = Handler()

        self.result_ok = []
        self.result_bad = []

    def checkConnection(self, domain: str = ""):
        while True:
            self.terminal.console(f"Test connection '{domain}'", "info")
            try:
                status_code = requests.get(domain).status_code
                self.terminal.console(f"Status Code: {status_code}")
                return domain
            except (requests.exceptions.MissingSchema):
                self.terminal.console("Missing scheme, change to default scheme (http)", "error")
                domain = f"http://{domain}"
            except (requests.exceptions.ConnectionError):
                parsers = urlparse(domain)
                scheme = parsers.scheme
                port = parsers.port
                if port is None:
                    if scheme == "http":
                        port = 80
                    elif scheme == "https":
                        port = 443
                self.handler.connectionError(parsers.hostname, port, isQuit=True)

    def showAll(self):
        if len(self.result_ok) > 1:
            tables = PrettyTable(["#", "URL", "Status Code"])
            for i, result_ok in zip(range(len(self.result_ok)), self.result_ok):
                tables.add_row([i+1, result_ok["urls"], result_ok["status_code"]])
            print (tables)
            self.terminal.quit(isUser=False)
        

    def brute(self, domain: str = "", wordlist: list = []):
        urlparser = urlparse(domain)
        self.terminal.console("Starting brute force ...")
        scheme = urlparser.scheme
        hostname = urlparser.hostname
        try:
            for i, path in zip(range(len(wordlist)), wordlist):
                if isinstance(path, bytes):
                    path = path.decode()
                urls = f"{scheme}://{hostname}/{path}"
                status_code = 0
                try:
                    status_code = requests.get(urls, timeout=3, headers=createHeaders()).status_code
                    if status_code == 200:
                        self.result_ok.append({"urls": urls, "status_code": status_code})
                except UnicodeDecodeError:
                    self.result_ok.append({"urls": urls, "status_code": status_code})
                except requests.exceptions.ConnectionError:
                    self.result_bad.append(urls)
                except KeyboardInterrupt: break
                print (f"{Fore.WHITE}[{Fore.CYAN}BRUTE{Fore.WHITE}] OK {len(self.result_ok)} BAD {len(self.result_bad)} TEST {i+1}/{len(wordlist)} PATH '{path}'" + " " * 10)
                sys.stdout.write("\033[F")
            return True
        except KeyboardInterrupt:
            self.terminal.console("User stop...", "info")
            return False

    def start(self):
        while True:
            try:
                self.terminal.clear()
                self.terminal.showLogo()
                domain = self.terminal.question(f"Input Domain [eg: {Fore.GREEN}https://google.com{Fore.RESET}]> ")
                wordPath = self.terminal.question("Wordlist Path [Select ENTER]> ", fixBlank=False)
                if wordPath == "":
                    wordPath = self.wordlist.selectWordlist()
                while True:
                    mode = self.terminal.question("Read mode [raw/byte] > ")
                    if mode.lower() == "raw" or mode.lower() == "r":
                        mode = "r"
                        break
                    elif mode.lower() == "byte" or mode.lower() == "rb" or mode.lower():
                        mode = "rb"
                        break
                    else:
                        self.terminal.console("Please choice raw or byte mode", "warning")
                domain = self.checkConnection(domain)
                wordList, isUnicode = self.wordlist.read(wordPath)
                if isUnicode:
                    wordList = self.wordlist.convertByte2raw(wordList)
                if len(wordList) == 0:
                    self.terminal.console("Wordlist null", "error")
                    if self.terminal.enter2continue(): continue
                else:
                    self.terminal.console(f"Total word {Fore.GREEN}{len(wordList)}")
                    bruteStatus = self.brute(domain, wordList)
                    if bruteStatus is True:
                        self.showAll()
            except KeyboardInterrupt: return False

def run():
    apps = AdminFinder()
    apps.start()