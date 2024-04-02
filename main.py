import argparse

from fuse import FUSE

from configurable_fs import ConfigurableFS


def main(mount_point, root_path, config_file):
    fs = ConfigurableFS(root_path, config_file)
    FUSE(fs, mount_point, foreground=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mount a configurable file system.')
    parser.add_argument('mount_point', type=str, help='Path to the mount point')
    parser.add_argument('root_path', type=str, help='Root path of the file system')
    parser.add_argument('config_file', type=str, help='Path to the configuration file')

    args = parser.parse_args()
    print(args)
    main(args.mount_point, args.root_path, args.config_file)
