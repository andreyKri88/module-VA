import configparser
import os
from pathlib import Path


class IniClass:
    def __init__(self, config_file: str = None):
        if config_file is None:
            # Get the project root directory (controller-va)
            project_root = Path(__file__).parent.parent.parent.parent
            # Try Russian version first, then fallback to English
            config_file_ru = project_root / "settings_ru.ini"
            config_file_en = project_root / "settings.ini"

            if config_file_ru.exists():
                config_file = config_file_ru
            elif config_file_en.exists():
                config_file = config_file_en
            else:
                raise FileNotFoundError(
                    f"Neither settings_ru.ini nor settings.ini found in {project_root}"
                )

        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        self.config.read(self.config_file, encoding="utf-8")

    def get_setting(self, section: str, key: str, default=None, type_cast=str):
        try:
            value = self.config.get(section, key)
            if type_cast == int:
                return int(value)
            elif type_cast == float:
                return float(value)
            elif type_cast == bool:
                return value.lower() in ("true", "yes", "1", "on")
            else:
                return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            if default is not None:
                return default
            raise
        except ValueError:
            if default is not None:
                return default
            raise
