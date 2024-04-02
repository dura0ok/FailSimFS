import argparse
import os.path

from fuse import FUSE

from configurable_fs import ConfigurableFS


def main(mount_point, base_dir, config_file):
    fs = ConfigurableFS(os.path.abspath(base_dir), config_file)
    FUSE(fs, os.path.abspath(mount_point), foreground=True, debug=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mount a configurable file system.')
    parser.add_argument('mount_point', type=str, help='Path to the mount point')
    parser.add_argument('base_dir', type=str, help='Path to the base of file system')
    parser.add_argument('config_file', type=str, help='Path to the configuration file')

    args = parser.parse_args()
    print(args)
    main(args.mount_point, args.base_dir, args.config_file)
