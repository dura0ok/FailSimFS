import errno
import fcntl
import os

import fuse
from fuse import FuseOSError, Operations
from print_color import print


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
            raise FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        try:
            dirs = ['.', '..'] + [f.name for f in os.scandir(path)]
            return dirs
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def read(self, path, size, offset, fh):
        try:
            with open(path, 'rb') as f:
                f.seek(offset)
                return f.read(size)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def mkdir(self, path, mode):
        try:
            os.mkdir(path, mode)
        except FileExistsError:
            raise FuseOSError(errno.EEXIST)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def rmdir(self, path):
        try:
            os.rmdir(path)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def unlink(self, path):
        try:
            os.unlink(path)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def open(self, path, flags):
        try:
            return os.open(path, flags)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def create(self, path, mode, fi=None):
        try:
            return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def chmod(self, path, mode):
        try:
            os.chmod(path, mode)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def chown(self, path, uid, gid):
        try:
            os.chown(path, uid, gid)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def truncate(self, path, length, fh=None):
        try:
            with open(path, 'r+') as f:
                f.truncate(length)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def utimens(self, path, times=None):
        try:
            os.utime(path, times)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def rename(self, old, new):
        try:
            os.rename(old, self.full_path(new))
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def statfs(self, path):
        statvfs = os.statvfs(path)
        return {
            'f_bsize': statvfs.f_bsize,
            'f_blocks': statvfs.f_blocks,
            'f_bavail': statvfs.f_bavail,
            'f_files': statvfs.f_files,
            'f_ffree': statvfs.f_ffree,
            'f_frsize': statvfs.f_frsize,
            'f_favail': statvfs.f_favail
        }

    def fsync(self, path, datasync, fh):
        return self.flush(path, fh)

    def symlink(self, source, target):
        os.symlink(source, target)

    def link(self, source, target):
        os.link(source, target)

    def readlink(self, path):
        try:
            return os.readlink(path)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def mknod(self, path, mode, dev):
        try:
            os.mknod(path, mode, dev)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def chmod(self, path, mode):
        try:
            os.chmod(path, mode)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def chown(self, path, uid, gid):
        try:
            os.chown(path, uid, gid)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def access(self, path, mode):
        if not os.access(path, mode):
            raise FuseOSError(errno.EACCES)

    def lseek(self, path, off, whence):
        try:
            return os.lseek(path, off, whence)
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def ioctl(self, path, cmd, arg, fip, flags, data):
        try:
            fd = os.open(path, os.O_RDWR)
            result = fcntl.ioctl(fd, cmd, arg, True)
            os.close(fd)
            return result
        except FileNotFoundError:
            raise FuseOSError(errno.ENOENT)

    def full_path(self, partial) -> str:
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.basedir, partial)
        return str(path)
