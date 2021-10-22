import requests
from terminal import Terminal

class Apps:
    def __init__(self) -> None:
        self.terminal = Terminal()

    def run(self):
        while True:
            try:
                self.terminal.clear()
                self.terminal.showLogo()
                self.terminal.showMenu()
                i = self.terminal.question("Select > ")
                if i == "0" or i == "00":
                    self.terminal.quit(newLine=False)
                elif i == "1" or i == "01":
                    try:
                        from plugin import bruteSubdo
                        bruteSubdo.run()
                    except (ImportError, ModuleNotFoundError, SyntaxError):
                        self.terminal.console("Module error", out="error")
                        self.terminal.quit(isUser=False)
                elif i == "2" or i == "02":
                    try:
                        from wordlist import Wordlist
                        self.terminal.clear()
                        self.terminal.showLogo()
                        wordlist = Wordlist()
                        wordlist.selectManifest()
                    except (ImportError, ModuleNotFoundError, SyntaxError):
                        self.terminal.console("Module error", out="error")
                        self.terminal.quit(isUser=False)
                elif i == "3" or i == "03":
                    try:
                        from plugin import adminFinder
                        adminFinder.run()
                    except (ImportError, ModuleNotFoundError, SyntaxError):
                        self.terminal.console("Module error", out="error")
                        self.terminal.quit(isUser=False)
                elif i == "4" or i == "04":
                    try:
                        from modules import exploitModules
                        exploitModules.run()
                    except (ImportError, ModuleNotFoundError, SyntaxError):
                        self.terminal.console("Module error", out="error")
                        self.terminal.quit(isUser=False)
            except KeyboardInterrupt:
                self.terminal.quit(newLine=True)

if __name__ == "__main__":
    apps = Apps()
    apps.run()