import os
from pathlib import Path
from typing import Any
import yaml

PROJECT_ROOT_DIR = os.path.abspath(Path(__file__).parent.parent)


class ConfigProvider:
    config: dict

    with open(os.path.join(PROJECT_ROOT_DIR, "config.yml"), "r", encoding="utf-8") as file:
        try:
            config = yaml.safe_load(file)
        except Exception as e:
            print("Could not load main configuration file!", e)

    @staticmethod
    def get_brager_config_option(option_name: str) -> Any:
        return ConfigProvider.get_config_option("Brager", option_name)

    @staticmethod
    def get_router_config_option(option_name: str) -> Any:
        return ConfigProvider.get_config_option("Router", option_name)

    @staticmethod
    def get_config_option(section: str, option_name: str) -> Any:
        return ConfigProvider.config[section][option_name]
