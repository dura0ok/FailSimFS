import json
import re

from typing import Optional, Dict, Any
from .config_loader import ConfigLoader


class JsonConfigLoader(ConfigLoader):
    def __init__(self, config_file_name: str) -> None:
        self.config_file_name: str = config_file_name

    def load_config(self) -> Dict[str, Any]:
        with open(self.config_file_name, 'r') as f:
            return json.load(f)

    def find_matching_key(self, path: str) -> Optional[str]:
        config_data: Dict[str, Any] = self.load_config()
        print(config_data.keys(), path)
        for key in config_data.keys():
            if re.match(key, path):
                return key
        return None

    def get_replacement(self, path: str, syscall_name: str) -> Optional[Dict[str, str]]:
        matching_key: Optional[str] = self.find_matching_key(path)

        if matching_key is not None:
            return self.load_config()[matching_key].get(syscall_name)

        return None
