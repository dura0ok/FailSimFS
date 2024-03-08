import os
import colorful as cf
from print_color import print


def get_attr(path, fh=None):
    print(f"DEBUG: Custom getattr for {path} {fh} with logging :)", color='purple')
    try:
        st = os.lstat(path)
        return dict((key, getattr(st, key)) for key in
                    ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
    except OSError as e:
        print(f"ERROR: {e}")
        return None
