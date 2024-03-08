import os

from fuse import FuseOSError


def get_attr(path, fh=None):
    # print(f"DEBUG: Custom getattr for {path} {fh}")

    # Mimic real getattr behavior (you can customize this part)
    try:
        st = os.lstat(path)
        return dict((key, getattr(st, key)) for key in
                    ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
    except OSError as e:
        print(f"ERROR: {e}")
        return None