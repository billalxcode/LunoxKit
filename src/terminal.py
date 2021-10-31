import os
import sys
import readline
import requests
import socket
from .__init__ import __version__, __created__, __author__, __updated__
from colorama import Fore
from datetime import datetime

class Timer:
    def getTime(self, format=""):
        timeNow = datetime.now()
        return timeNow.strftime("%H:%M:%S")
        

class Terminal:
    def __init__(self) -> None:
        self.timer = Timer()
        self.myaddr = socket.gethostbyname(socket.gethostname())
    def exit(self):
        sys.exit()

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def quit(self, newLine: bool = False, isUser: bool =True):
        if isUser:
            self.console("User quit...", "info", newLine=newLine)
        else:
            self.console("Program quit...", "info", newLine=newLine)
        self.exit()

    def console(self, message: str, out: str ="info", newLine: bool =False, fixLine: bool = False):
        timeNow = self.timer.getTime()
        formatOut = ""
        if newLine:
            formatOut += "\n"
        if fixLine:
            formatOut += "\r"
        if out == "" or out == "info":
            formatOut += f"[{Fore.GREEN}INFO{Fore.WHITE}] "
        elif out == "error":
            formatOut += f"[{Fore.RED}ERROR{Fore.WHITE}] "
        elif out == "warning":
            formatOut += f"[{Fore.YELLOW}WARNING{Fore.WHITE}] "
        print (f"{formatOut}[{Fore.CYAN}{timeNow}{Fore.WHITE}] {Fore.RESET}{message}{Fore.RESET}")

    def question(self, text: str, fixBlank=True):
        while True:
            i = input(text)
            if i.strip():
                return i
            else:
                if fixBlank:
                    self.console("Blank Word", "warning")
                    continue
                else:
                    return i
    
    def checkNetwork(self):
        try:
            requests.get("https://google.com", timeout=3)
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            return False

    
    def showNoImplement(self):
        self.console("Sorry, this feature is not implemented yet. Please choose another", "warning")
        i = self.question("Back? (Y/n) > ")
        if i.lower() == "y":
            return True
        else:
            return False
            
    def enter2continue(self):
        i = self.question("Continue? (Y/n) > ")
        if i.lower() == "y":
            return True
        else:
            self.quit()

    def showLogo(self):
        networkstatus = self.checkNetwork()
        network = (Fore.GREEN + "Connected" if networkstatus else Fore.RED + "Disconnected")
        self.logos = f"""
{Fore.CYAN}         _ 
{Fore.CYAN}        | | {Fore.GREEN}Penetration Testing Tool KIT v{__version__}
{Fore.CYAN}        | |    _   _ _ __   _____  __
{Fore.CYAN}        | |   | | | | '_ \ / _ \ \/ /
{Fore.YELLOW}        | |___| |_| | | | | (_) >  < 
{Fore.YELLOW}        \_____/\__,_|_| |_|\___/_/\_\\   {Fore.RESET}\n
Author: {Fore.GREEN}{__author__}{Fore.RESET}\tVersion: {Fore.YELLOW}{__version__}{Fore.RESET}
Created: {Fore.GREEN}{__created__}{Fore.RESET}\tUpdated: {Fore.YELLOW}{__updated__}{Fore.RESET}
Network: {network}{Fore.RESET}\tADDRESS: {Fore.YELLOW}{self.myaddr}\n\n{Fore.RESET}"""
        print (self.logos)

    def showMenu(self):
        menuLists = [
            "Subdomain Finder (Brute Force)",
            "Download Wordlist",
            "Admin Login Finder",
            "Exploit"
        ]

        print ("Menu: ")
        for i, name in zip(range(len(menuLists)), menuLists):
            print (f"\t{i+1}). {name}")
        print ("\t0). Exit\n")