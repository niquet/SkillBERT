import sys
sys.path.append('./')
from utils.config import ConfigParser

cp = ConfigParser()
print(cp.conf_dir)
print(cp.get_file_name("conf/linkedin.config.json"))
print(cp.get_file_path("conf/linkedin.config.json"))
print(cp.read_json("conf/linkedin.config.json"))