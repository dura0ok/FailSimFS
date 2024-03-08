import os

from fuse import FuseOSError, Operations


class DefaultFS(Operations):
    def __init__(self, basedir):
        self.basedir = basedir

    def getattr(self, path, fh=None):
        try:
            st = os.lstat(path)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size',
                                                            'st_uid'))
        except FileNotFoundError:
            raise FuseOSError(2)

    def readdir(self, path, fh):
        try:
            dirs = ['.', '..'] + [f.name for f in os.scandir(path)]
            return dirs
        except FileNotFoundError:
            raise FuseOSError(2)

    def read(self, path, size, offset, fh):
        try:
            with open(path, 'rb') as f:
                data = f.read()
                return data[offset:offset + size]
        except FileNotFoundError:
            raise FuseOSError(2)

    def write(self, path, data, offset, fh):
        try:
            with open(path, 'r+b') as f:
                f.seek(offset)
                f.write(data)
                return len(data)
        except FileNotFoundError:
            raise FuseOSError(2)

    def mkdir(self, path, mode):
        try:
            os.mkdir(path, mode)
        except FileExistsError:
            raise FuseOSError(17)
        except FileNotFoundError:
            raise FuseOSError(2)

    def rmdir(self, path):
        try:
            os.rmdir(path)
        except FileNotFoundError:
            raise FuseOSError(2)

    def unlink(self, path):
        try:
            os.unlink(path)
        except FileNotFoundError:
            raise FuseOSError(2)

    def full_path(self, partial) -> str:
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.basedir, partial)
        return str(path)
