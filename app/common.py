# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE, STDOUT
from os import path, remove, walk, chmod
from fnmatch import filter as nfilter
from urllib import urlopen as connect
from shlex import split as arg_split
from urllib2 import urlopen, Request
from contextlib import closing
from os import name as os_name
from zipfile import ZipFile
from sys import stdout, version_info
from glob import glob

MAX_PATH_WIN = 248
CHUNK_SIZE = 4 * 1024

if os_name != "nt":
    from os import symlink


def debug(text):
    stdout.write("[DEBUG]: {0}\n".format(text))


def console(command, stream=False):
    ret = None
    out = None
    debug(command)
    try:
        process = Popen(arg_split(command), stdout=PIPE, stderr=STDOUT)
        if stream:
            for line in iter(process.stdout.readline, b""):
                print line.rstrip()
        process.wait()
    except Exception as e:
        ret = e.args[0]
        out = e
    else:
        ret = process.returncode
        out = process.stdout.read()
    finally:
        return {"code": ret, "message": out}


def is_symlink(info):
    """
    :param info: file info
    :return: True if the object ZipInfo passed in represents a symlink
    """
    return (info.external_attr >> 16) & 0770000 == 0120000


def set_attributes(file_info, path_to_file):
    permissions = (file_info.external_attr >> 16) & 0777
    if permissions:
        chmod(path_to_file, permissions)


def create_symlink(path_to_file):
    with open(path_to_file, "r") as symlink_file:
        symlink_name = symlink_file.read()
    remove(path_to_file)
    symlink(path_to_file.replace(path.basename(path_to_file), symlink_name), path_to_file)


def unzip(path_to_package, path_to_extract):
    with closing(ZipFile(path_to_package, "r")) as archive:
        for file_info in archive.infolist():
            path_to_file = path.join(path_to_extract, file_info.filename)

            if os_name == "nt" and len(path_to_file) >= MAX_PATH_WIN:
                continue

            archive.extract(file_info.filename, path_to_extract)

            if os_name != "nt":
                set_attributes(file_info, path_to_file)
                if is_symlink(file_info):
                    create_symlink(path_to_file)


def zip_files(path_to_package, files_list):
    with closing(ZipFile(path_to_package, "w")) as archive:
        for f in files_list:
            archive.write(f)


def get_http_code(url):
    return connect(url).code


def download_file(url, path_to_save):
    connect_code = get_http_code(url)
    if connect_code != 200:
        raise Exception("Connection to {0} failed. Return code: {1}".format(url, connect_code))
    request = Request(url)
    response = urlopen(request)
    with open(path_to_save, "wb") as archive:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            archive.write(chunk)


def get_files_by_glob(glob_path, root_dir):
    files = []
    for root, dirnames, filenames in walk(root_dir):
        for g in glob_path:
            for filename in nfilter(filenames, g):
                files.append(path.join(root, filename))
    if not files:
        raise Exception("Can not match files by glob: {0} in {1} dir".format(glob_path, root_dir))
    return files


def glob_wrapper(glob_path):
    files = glob(glob_path)
    if not files:
        raise Exception("Can not match files by glob: {0}".format(glob_path))
    return files
