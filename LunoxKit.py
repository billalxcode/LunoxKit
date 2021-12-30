try:
    from src.core.shell import Shell
    from src.utils.terminal import Terminal
    from src.utils.terminal import MESSAGE_INFO, MESSAGE_ERROR, MESSAGE_NORMAL, MESSAGE_WARNING
except ImportError:
    from core.shell import Shell
    from utils.terminal import Terminal
    from utils.terminal import MESSAGE_WARNING, MESSAGE_NORMAL, MESSAGE_ERROR, MESSAGE_INFO

terminal = Terminal()

def main():
    terminal.show_banner()
    shell = Shell()
    shell.initialize()
    shell.run()

if __name__ == "__main__":
    try:
        main()
    except SyntaxError as err:
        terminal.console(f"Syntax error => {err}", MESSAGE_ERROR)