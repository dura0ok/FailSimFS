import errno
import os
import random
import time
from errno import ENOENT

from fuse import FuseOSError
from print_color import print


def get_attr(path, fh=None):
    try:
        st = os.lstat(path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                        'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size',
                                                        'st_uid'))
    except FileNotFoundError:
        raise FuseOSError(2)


def read(path, size, offset, fh=None):
    """
    Read a file, but with 50% chance return no-op
    :param path: The path to the file being read.
    :param size:  The number of bytes to read.
    :param offset: The offset in the file from where to start reading.
    :param fh: The file handle, representing the open file. It is an identifier that your FUSE implementation can use
    to keep track of open files.
    :return: bytes | FuseOSError
    """
    random.seed(time.time())
    print(f"custom read method for {path}", color="green")
    try:
        with open(path, 'rb') as f:
            data = f.read()
            res = data[offset:offset + size]
            if random.random() <= 0.5:
                print(f"We not get this data to user :) -> {res[:10]}", color='red')
                return b''
            return res
    except FileNotFoundError:
        raise FuseOSError(2)


def write(self, path, data, offset, fh):
    random.seed(time.time())
    print(f"custom write method for {path}", color="green")
    if random.random() <= 0.5:
        raise FuseOSError(errno.ENOSPC)

    try:
        with open(path, 'r+b') as f:
            os.lseek(f.fileno(), offset, os.SEEK_SET)
            os.write(f.fileno(), data)
            return len(data)
    except FileNotFoundError:
        raise FuseOSError(ENOENT)
