from abc import ABC, abstractmethod


class ConfigLoader(ABC):
    @abstractmethod
    def load_config(self):
        pass

    @abstractmethod
    def get_replacement(self, path, syscall_name):
        pass
