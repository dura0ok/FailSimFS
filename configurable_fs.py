import errno
import importlib
import inspect
import os

from fuse import FuseOSError
from print_color import print

from config.json_config_loader import JsonConfigLoader
from default_impl import DefaultFS


class ConfigurableFS(DefaultFS):
    def __init__(self, base_dir, config_file_name):
        super().__init__(base_dir)
        self.config = JsonConfigLoader(config_file_name)

    def default_implementation(self, func_name, *args, **kwargs):
        default_func = getattr(DefaultFS, func_name, None)
        # print(f"REPLACEMENT, default_implementation {default_func}", color="blue")
        if default_func:
            return default_func(self, *args, **kwargs)
        else:
            raise FuseOSError(errno.ENOSYS)

    def apply_replacement(self, path, *args, **kwargs):
        syscall_name = inspect.stack()[1][3]

        replacement = self.config.get_replacement(path, syscall_name)
        f_path = self.full_path(path)
        #print(f"REPLACEMENT, {syscall_name}, {replacement} {path} {f_path}, {kwargs}", color="red")
        if replacement:
            module_name, function_name = replacement['module'], replacement['function']
            module = importlib.import_module(module_name)
            func = getattr(module, function_name)
            return func(f_path, *args, **kwargs)
        else:
            return self.default_implementation(syscall_name, f_path, *args, **kwargs)

    def getattr(self, path, fh=None):
        return self.apply_replacement(path, fh)

    def readdir(self, path, fh):
        return self.apply_replacement(path, fh)

    def read(self, path, size, offset, fh):
        return self.apply_replacement(path, size, offset, fh)

    def write(self, path, data, offset, fh):
        return self.apply_replacement(path, data, offset, fh)

    def open(self, path, flags):
        return self.apply_replacement(path, flags)

    def create(self, path, mode, fi=None):
        return self.apply_replacement(path, mode, fi)

    def unlink(self, path):
        return self.apply_replacement(path)

    def mkdir(self, path, mode):
        return self.apply_replacement(path, mode)

    def rmdir(self, path):
        return self.apply_replacement(path)

    def chmod(self, path, mode):
        return self.apply_replacement(path, mode)

    def chown(self, path, uid, gid):
        return self.apply_replacement(path, uid, gid)

    def truncate(self, path, length, fh=None):
        return self.apply_replacement(path, length, fh)

    def utimens(self, path, times=None):
        return self.apply_replacement(path, times)

    def rename(self, old, new):
        return self.apply_replacement(old, new)

    def statfs(self, path):
        return self.apply_replacement(path)

    def fsync(self, path, datasync, fh):
        return self.apply_replacement(path, datasync, fh)

    def symlink(self, target, source):
        return self.apply_replacement(source, self.full_path(target))

    def link(self, target, source):
        return self.apply_replacement(source, self.full_path(target))

    def readlink(self, path):
        return self.apply_replacement(path)

    def mknod(self, path, mode, dev):
        return self.apply_replacement(path, mode, dev)

    def flush(self, path, fh):
        return self.apply_replacement(path, fh)

    def release(self, path, fh):
        return self.apply_replacement(path, fh)

    def access(self, path, mode):
        return self.apply_replacement(path, mode)

    def lseek(self, path, off, whence):
        return self.apply_replacement(path, path, off, whence)

    def ioctl(self, path, cmd, arg, fip, flags, data):
        return self.apply_replacement(path, cmd, arg, fip, flags, data)
