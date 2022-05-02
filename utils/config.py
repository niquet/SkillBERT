import json
import os

CONF_DIR_NAME = "conf"

class ConfigParser:

    def __init__(self) -> None:
        self.conf_dir = self.get_dir_path(CONF_DIR_NAME)

    def get_dir_path(self, dir_name: str) -> str:
        dir_path = os.path.abspath(dir_name)
        return dir_path

    def get_file_name(self, path: str) -> str:
        file_name = os.path.basename(path)
        return file_name

    def get_file_path(self, path: str) -> str:
        file_name = self.get_file_name(path)
        path = os.path.join(self.conf_dir, file_name)
        return path

    def read_json(self, path: str) -> dict:
        path = self.get_file_path(path)
        with open(path, "r") as file:
            data = json.load(file)         
        return data
