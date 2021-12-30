import random
import time
import sys
from os.path import isfile
from string import ascii_letters
from string import punctuation
from threading import Thread
from colorama import init, ansi

init()

ALPHABET = ascii_letters
GENERATED = []
generator = lambda mn, mx: "".join([random.choice(ALPHABET) for s in range(random.randint(mn, mx))])
FILENAME = "filesystem/wordlist/test1.txt"
if isfile(FILENAME) is False:
    with open(FILENAME, "w") as File:
        File.close()

def process():
    global GENERATED, generator
    while True:
        s = generator(4, 8)
        GENERATED.append(s)
        with open(FILENAME, "a") as File:
            File.write(f"{s}\n")
            File.close()

def main():
    global GENERATED
    start_time = time.time()
    th = Thread(target=process)
    th.start()
    while th.is_alive():
        sys.stdout.write(f"\r{ansi.clear_line()}Generated {len(GENERATED)} on time {round(time.time() - start_time)}s")
        
if __name__ == "__main__":
    main()