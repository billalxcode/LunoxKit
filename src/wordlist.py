import requests
import os
import time
import glob
import sys
from colorama import Fore
from .manifest import loadManifest
from .terminal import Terminal

class Wordlist:
    def __init__(self) -> None:
        self.manifest = loadManifest()
        self.terminal = Terminal()


    def quit(self, newLine: bool = False):
        self.terminal.console("User quit...", "info", newLine=newLine)
        self.terminal.exit()

    def selectManifest(self):
        manifestdata = self.manifest["wordlists"]
        data = {}
        while True:
            print ("Wordlist:")
            for i, data in zip(range(len(manifestdata)), manifestdata):
                print (f"\t{i+1}). {data['name']}")
            print ("\t0). Back")
            i = self.terminal.question("Select > ")    
            if i == "0" or i == "00":
                return
            if i.isdigit() is True:
                minSelect = 1
                maxSelect = int(len(manifestdata))
                if int(i) > maxSelect:
                    self.terminal.console(f"Please select [{minSelect}-{maxSelect}]", "warning")
                    if self.terminal.enter2continue(): continue
                else:
                    data = manifestdata[int(i)-1]
                    break
            else:
                self.terminal.console("Please input digit", "warning")
                if self.terminal.enter2continue(): continue
        self.downloadWordlist(data)
        time.sleep(2)
    
    def read(self, path: str = "", mode: str = "r"):
        self.terminal.console("Reading wordlist....", "info")
        try:
            with open(path, mode=mode) as F:
                content = F.read().splitlines()
                return content, False
        except FileNotFoundError:
            self.terminal.console("File not found error", "error")
            self.terminal.quit()
        except UnicodeDecodeError:
            self.terminal.console("Unicode error, change to byte mode")
            newContent, _ = self.read(path, "rb")
            return newContent, True
            
    def convertByte2raw(self, wordlist: list = []):
        self.terminal.console("Start convert byte to raw files...")
        outputs = []
        for word in wordlist:
            try:
                outputs.append(word.decode())
            except UnicodeDecodeError: pass
            print (f"{Fore.WHITE}[{Fore.CYAN}DECODE{Fore.WHITE}] Converting {Fore.GREEN}{len(outputs)}{Fore.WHITE}/{Fore.YELLOW}{len(wordlist)}{Fore.RESET}")
            sys.stdout.write("\033[F")
        return outputs

    def downloadWordlist(self, data: dict = {}):
        self.terminal.console(f"Downloading from '{data['url']}'")
        output = os.path.join(os.getcwd(), data["path"])
        dirname = os.path.dirname(output)
        if os.path.isdir(dirname) is False:
            os.mkdir(dirname)

        with open(output, "wb") as F:
            r = requests.get(data["url"], stream=True)
            for content in r.iter_content(chunk_size=1024):
                F.write(content)
        self.terminal.console(f"Saved to '{output}'")

    def selectWordlist(self):
        while True:
            dirname = os.path.join(os.getcwd(), "wordlists/*")
            filesname = glob.glob(dirname)
            print ("Wordlist path:")
            for i, files in zip(range(len(filesname)), filesname):
                filename = os.path.basename(files)
                print (f"\t{i+1}). {filename}")
            print ("\t99). Download Wordlist")
            print ("\t0). Back")
            i = self.terminal.question("\nSelect > ")
            if i == "0" or i == "00":
                return

            if i == "99":
                self.selectManifest()
                continue

            if i.isdigit() is True:
                minSelect = 1
                maxSelect = int(len(filesname))
                if int(i) > maxSelect:
                    self.terminal.console(f"Please select [{minSelect}-{maxSelect}]", "warning")
                    if self.terminal.enter2continue(): continue
                else:
                    data = filesname[int(i)-1]
                    return data
            else:
                self.terminal.console("Please input digit", "warning")
                if self.terminal.enter2continue(): continue