import os
import hashlib

try:
    from src.utils.utils import isfile, getcwd, path_join
except ImportError:
    from utils.utils import isfile, getcwd, path_join

def get_system_version():
    version = "unknown"
    try:
        version_file = path_join(getcwd(), "version")
        if isfile(version_file):
            with open(version_file, "r") as File:
                version = File.read().splitlines()[0]
                File.close()
    except (FileNotFoundError, IOError):
        version = "unknown"

    return version

def get_system_codename():
    release = "unknown"
    try:
        release_file = path_join(getcwd(), "data", "release")
        if isfile(release_file):
            with open(release_file, "r") as File:
                release = File.read().splitlines()[0]
                File.close()
    except (FileNotFoundError, IOError):
        release = "unknown"
    return release

def get_system_release():
    codename = get_system_codename()
    version = get_system_version()
    result = f"LunoxKit {codename} v{version}"
    return result

def get_system_sha256():
    codename = get_system_codename()
    version = get_system_version()

    join_string = f"{codename}-beta-v{version}".encode("utf-8")
    new_hash = hashlib.new("sha256")
    new_hash.update(join_string)
    return new_hash.hexdigest()