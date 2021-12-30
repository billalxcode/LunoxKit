import random
from colorama import Fore

banner1 = f"""
{Fore.CYAN}         _ 
{Fore.CYAN}        | | {Fore.GREEN}Penetration Testing Tool KIT
{Fore.CYAN}        | |    _   _ _ __   _____  __
{Fore.CYAN}        | |   | | | | '_ \ / _ \ \/ /
{Fore.YELLOW}        | |___| |_| | | | | (_) >  < 
{Fore.YELLOW}        \_____/\__,_|_| |_|\___/_/\_\\   {Fore.RESET}\n"""

def random_banner():
    banner_list = [banner1]
    return random.choice(banner_list)