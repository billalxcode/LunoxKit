# Build a tool to binary file
# Author: Billal Fauzan
#=== Lunox Kit generate binary file ===#
import os
import sys
import glob
import time
import pathlib
import shutil

CWD = os.getcwd()
BUILD_PATH = os.path.join(CWD, "build")
SOURCE_PATH = os.path.join(CWD, "src")
SUPPORT_FILES = ["LunoxKit.py", "release", "version", "env.lnx"]
start_time = time.time()

def calculate_time():
    global start_time
    return round(time.time() - start_time)

def question_yn(msg):
    user_input = input(msg)
    if user_input.lower() == "y":
        return True
    else:
        return False

def logging(message, clear_line = False, end = None):
    message += f" => '{calculate_time()}'s"
    print(message)
    if clear_line is True:
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")

def check_build_directory():
    global BUILD_PATH
    if os.path.isdir(BUILD_PATH) is False:
        print(f"Make a directory...")
        os.makedirs(BUILD_PATH)
    else:
        print(f"Directory already exists, remove all file from directory")
        join_patern = os.path.join(BUILD_PATH, "*")
        all_files = glob.glob(join_patern)
        print (f"Total files: {len(all_files)}")
        for files in all_files:
            if os.path.isfile(files):
                logging(f"Delete file '{os.path.basename(files)[:10]}'", end="\r")
                try:
                    os.remove(files)
                except: pass
            else:
                logging(f"Delete dir '{os.path.basename(files)}'", end="\r")
                try:
                    os.removedirs(files)
                except: pass
        print()
        os.removedirs(BUILD_PATH)

def find_path(path):
    result = []
    join_patern = os.path.join(path, "*")
    logging(f"Find all files from '{path}'", clear_line=True, end="\r")
    time.sleep(0.0)
    for files in glob.glob(join_patern):
        if os.path.isfile(files):
            result.append(files)
        elif os.path.isdir(files):
            res = find_path(files)
            result.extend(res)
    return result

def get_all_source():
    global SOURCE_PATH
    sources = find_path(SOURCE_PATH)
    # print()
    print (f"Total files: {len(sources)}")
    return sources

def copy_all_files():
    sources = get_all_source()
    print (f"Copy file from 'src/' to 'build/'")
    shutil.copytree(SOURCE_PATH, BUILD_PATH)
    print (f"Copy support file...")
    SUPPORT_FILE = [os.path.join(os.getcwd(), x) for x in SUPPORT_FILES]
    print (SUPPORT_FILE)

if __name__ == "__main__":
    print ("This script not implemented!")
