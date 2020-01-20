import os
from configparser import ConfigParser, NoSectionError, NoOptionError
import logging
from typing import Dict, List


class Config:
    config = ConfigParser()

    @classmethod
    def init(cls, config_files: List[str]) -> None:

        for config_file in config_files:
            if not os.path.exists(config_file):
                raise Exception('Configuration-file "{}" does not exist'.format(config_file))

        cls.config.read(config_files)

    @classmethod
    def get_option(cls, section: str, option: str) -> str:
        try:
            return cls.config.get(section, option)
        except NoSectionError:
            logging.error('Tried to load non existing config section "%s"', section)

        except NoOptionError:
            logging.error('Tried to load non existing config option "%s" from section "%s"', option, section)

        return ''

    @classmethod
    def get_section(cls, section_name: str) -> Dict[str, str]:
        try:
            items = cls.config.items(section_name)
        except NoSectionError:
            logging.error('Tried to load non existing config section "%s"', section_name)
            return {}

        section = {}
        for item in items:
            section[item[0]] = item[1]

        return section
