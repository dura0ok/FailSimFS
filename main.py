import errno
import importlib
import inspect
import os
import json
import colorful as cf
from fuse import FUSE

from print_color import print

from configurable_fs import ConfigurableFS

if __name__ == '__main__':
    mount_point = 'mnt_point'
    root_path = 'data'
    config_file = 'example.json'

    fs = ConfigurableFS(root_path, config_file)
    fuse = FUSE(fs, mount_point, foreground=True, debug=False)
