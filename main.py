from fuse import FUSE

from configurable_fs import ConfigurableFS

if __name__ == '__main__':
    mount_point = 'mnt_point'
    root_path = 'data'
    config_file = 'example-config.json'

    fs = ConfigurableFS(root_path, config_file)
    fuse = FUSE(fs, mount_point, foreground=True)
