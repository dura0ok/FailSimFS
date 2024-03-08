import os
from random import randint

from fuse import FuseOSError
from print_color import print


def get_attr(path, fh=None):
    # print(f"DEBUG: Custom getattr for {path} {fh} with logging :)", color='purple')
    try:
        st = os.lstat(path)
        return dict((key, getattr(st, key)) for key in
                    ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
    except OSError as e:
        print(f"ERROR: {e}")
        return None


def read(path, size, offset, fh=None):
    print("DEBUG", color='green')
    try:
        with open(path, 'rb') as f:
            data = f.read()
            if randint(0, 1):
                print(data)
                return b''  # Return empty data as a no-op
            return data[offset:offset + size]
    except FileNotFoundError:
        raise FuseOSError(2)
