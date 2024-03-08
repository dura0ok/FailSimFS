import json

from .config_loader import ConfigLoader


class JsonConfigLoader(ConfigLoader):
    def __init__(self, config_file_name):
        self.config_file_name = config_file_name

    def load_config(self):
        with open(self.config_file_name, 'r') as f:
            return json.load(f)

    def get_replacement(self, path, syscall_name):
        return self.load_config().get(path, {}).get(syscall_name)
