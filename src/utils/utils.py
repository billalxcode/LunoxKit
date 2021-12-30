import os
import io

def isfile(path):
    return os.path.isfile(path)

def isdir(path):
    return os.path.isdir(path)
    
def basename(path):
    return os.path.basename(path)

def getcwd():
    return os.getcwd()

def mkdir(path):
    os.mkdir(path)

def rmdir(path):
    os.removedirs(path)
    
def openfile(path: str, mode: str = "r", encoding: str = "utf-8", buffer: int = 1024):
    with open(path, mode=mode, encoding=encoding, buffering=buffer) as File:
        try:
            content = File.read()
            return content
        except UnicodeDecodeError:
            content = openfile(path, "rb", encoding, buffer)
            return content
        except UnicodeError:
            content = openfile(path, "rb", encoding, buffer)
            return content

def path_join(*args, **kwargs):
    return os.path.join(*args, **kwargs)
    
def change_path_reg(path: str, modname: str = ""):
    output = path
    if "[cwd]" in path:
        output = output.replace("[cwd]", os.getcwd())
    if "[modules]" in path:
        output = output.replace("[modules]", "modules")
    if "[name]" in path:
        output = output.replace("[name]", modname)
    return output

def check_path_syntax(path: str, ascii_list: list = []):
    pathlst = list(path)
    for a in pathlst:
        if a in ascii_list:
            return True, a
    return False, None

def change_prompt_syntax(prompt: str, module: str = "~"):
    output = prompt
    if "[module]" in prompt:
        output = output.replace("[module]", module)
    return output

def convert_date( 
    second: int = 0, minute: int = 0, hour: int = 0, 
    day: int = 0, month: int = 0, year: int = 0 ):
    months_list = [
        "Jan", "Feb", "March", "Apr", "Mey", "Jun", "Jul", "Augs", "Sep", "Okt", "Nov", "Des"
    ]
    
