import errno
import importlib
import inspect
import json

from fuse import FuseOSError

from config.json_config_loader import JsonConfigLoader
from default_impl import DefaultFS
from print_color import print


class ConfigurableFS(DefaultFS):
    def __init__(self, root, config_file_name):
        super().__init__(root)
        self.config = JsonConfigLoader(config_file_name)

    def default_implementation(self, func_name, *args, **kwargs):
        default_func = getattr(DefaultFS, func_name, None)
        if default_func:
            return default_func(self, *args, **kwargs)
        else:
            raise FuseOSError(errno.ENOSYS)

    def apply_replacement(self, path, *args, **kwargs):
        syscall_name = inspect.stack()[1][3]
        replacement = self.config.get_replacement(path, syscall_name)
        full_path = super().full_path(path)
        if replacement:
            module_name, function_name = replacement['module'], replacement['function']
            module = importlib.import_module(module_name)
            func = getattr(module, function_name)
            return func(full_path, *args, **kwargs)
        else:
            return self.default_implementation(syscall_name, full_path, *args, **kwargs)

    def getattr(self, path, fh=None):
        return self.apply_replacement(path, fh)

    def readdir(self, path, fh):
        print(path)
        return self.apply_replacement(path, fh)

    def read(self, path, size, offset, fh):
        print(path, size)
        return self.apply_replacement(path, size, offset, fh)

    def write(self, path, data, offset, fh):
        return self.apply_replacement(path, data, offset, fh)
