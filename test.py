import time
import sys
import random
import zipfile
from prettytable import PrettyTable

def test(total: int = 10, sec: float = 0.2):
    idx = 0
    index = 0
    pointer_list = list("|/-\|")
    while index < total:
        if idx == len(pointer_list):
            idx = 0
        pointer = pointer_list[idx]
        texts = f"\r[{pointer}] Loading ..."
        sys.stdout.write(texts)
        time.sleep(sec)
        index += 1
        idx += 1

tables = PrettyTable(["#", "X", "Y"])
for _ in range(100):
    x = random.randint(10, 100)
    y = random.randint(10, 300)
    tables.add_row([str(_), str(x), str(y)])
print (tables)
# start_time = time.time()
# with open("data/wordlist/test1.txt", "r") as File:
#     passwords = File.read().splitlines()
# i = 0
# zipext = zipfile.ZipFile("data/brutezip/test.zip")
# files = zipext.filelist[0]
# filename = files.filename

# for passw in passwords:
#     i += 1
#     try:
#         zipext.read(files, pwd=passw.encode())
#         x = zipext.filelist[0]
#         print()
#         print (x.file_size)
#         print (f"Test ok -> {passw} on time {time.time() - start_time}s")
#         break
#     except:
#         print (f"Test {i}/{len(passwords)}", end="\r")