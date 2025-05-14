import logging.config
import os
import socket
import yaml
from utils.config_provider import PROJECT_ROOT_DIR


def record_factory(*args, **kwargs):
    username = os.environ.get("USER", os.environ.get("USERNAME"))
    hostname = socket.gethostname()
    record = old_factory(*args, **kwargs)
    record.userdata = f"{username}@{hostname}"
    return record


old_factory = logging.getLogRecordFactory()
logging.setLogRecordFactory(record_factory)
config_file_path = os.path.join(PROJECT_ROOT_DIR, "logging.yml")

with open(config_file_path, "rt") as file:
    try:
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)
    except Exception as e:
        print("Could not load logger configuration file!", e)

# create logger
logger = logging.getLogger("bragerNotifier")
