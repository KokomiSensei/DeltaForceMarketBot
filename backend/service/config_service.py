from abc import ABC, abstractmethod
from typing import List

from backend.bot.config import BotConfig
from backend.exception.general_exception import ConflictError, NotFoundError
from backend.util.monitor import Monitor
from config import Config


class ConfigDao(ABC):
    @abstractmethod
    def get_configs(self) -> List[BotConfig]: ...

    @abstractmethod
    def set_configs(self, configs: List[BotConfig]): ...

    @abstractmethod
    def update_config(self, config_name: str, config: BotConfig): ...

    @abstractmethod
    def rename_config(self, old_name: str, new_name: str): ...

    @abstractmethod
    def remove_config(self, config_name: str): ...

    @abstractmethod
    def add_config(self, config_name: str, config: BotConfig): ...

    @abstractmethod
    def contains(self, config_name: str) -> bool: ...


class ConfigService(Monitor):
    def __init__(self, config_dao: ConfigDao):
        super().__init__()
        self.dao = config_dao

    @Monitor.synchronized
    def get_configs(self) -> List[BotConfig]:
        return self.dao.get_configs()

    @Monitor.synchronized
    def set_configs(self, configs: List[BotConfig]):
        self.dao.set_configs(configs)

    @Monitor.synchronized
    def update_config(self, config_name: str, config: BotConfig):
        if not self.dao.contains(config_name):
            raise NotFoundError(f"Config '{config_name}' not found")
        self.dao.update_config(config_name, config)

    @Monitor.synchronized
    def rename_config(self, old_name: str, new_name: str):
        if not self.dao.contains(old_name):
            raise NotFoundError(f"Config '{old_name}' not found")
        if self.dao.contains(new_name):
            raise ConflictError(f"Config '{new_name}' already exists")
        self.dao.rename_config(old_name, new_name)

    @Monitor.synchronized
    def remove_config(self, config_name: str):
        if not self.dao.contains(config_name):
            raise NotFoundError(f"Config '{config_name}' not found")
        self.dao.remove_config(config_name)

    @Monitor.synchronized
    def add_config(self, config_name: str, config: BotConfig):
        if self.dao.contains(config_name):
            raise ConflictError(f"Config '{config_name}' already exists")
        self.dao.add_config(config_name, config)


class ConfigMemoryDao(ConfigDao):
    def __init__(self):
        self.configs: dict[str, BotConfig] = {}

    def get_configs(self) -> List[BotConfig]:
        return list(self.configs.values())

    def set_configs(self, configs: List[BotConfig]):
        self.configs = {config.name: config for config in configs}

    def update_config(self, config_name: str, config: BotConfig):
        self.configs[config_name] = config

    def rename_config(self, old_name: str, new_name: str):
        self.configs[new_name] = self.configs.pop(old_name)

    def remove_config(self, config_name: str):
        self.configs.pop(config_name, None)

    def add_config(self, config_name: str, config: BotConfig):
        self.configs[config_name] = config

    def contains(self, config_name: str) -> bool:
        return config_name in self.configs


# TODO GPT generated
class ConfigJsonFileDao(ConfigDao):
    def __init__(self, file_path: str = "config.json"):
        self.file_path = file_path

    def get_configs(self) -> List[BotConfig]:
        from backend.bot.config import MultiConfig

        local_configs = MultiConfig.load_configs(self.file_path)
        # Convert LocalConfig to BotConfig
        return [
            BotConfig(
                lowest_price=config.lowest_price,
                volume=config.volume,
                screenshot_delay=config.screenshot_delay,
                debug_mode=config.debug_mode,
                target_schema_index=config.target_schema_index,
                name=config.name,
            )
            for config in local_configs
        ]

    def set_configs(self, configs: List[BotConfig]):
        from backend.bot.config import LocalConfig, MultiConfig

        # Convert BotConfig to LocalConfig if needed
        local_configs = []
        for config in configs:
            if isinstance(config, LocalConfig):
                local_configs.append(config)
            else:
                # Create new LocalConfig with values from BotConfig
                local_configs.append(
                    LocalConfig(
                        lowest_price=config.lowest_price,
                        volume=config.volume,
                        screenshot_delay=config.screenshot_delay,
                        debug_mode=config.debug_mode,
                        target_schema_index=config.target_schema_index,
                        name=config.name,
                    ),
                )
        MultiConfig.save_configs(local_configs, self.file_path)

    def update_config(self, config_name: str, config: BotConfig):
        configs = self.get_configs()
        found = False

        for i, existing_config in enumerate(configs):
            if existing_config.name == config_name:
                configs[i] = config
                found = True
                break

        if not found:
            raise NotFoundError(f"Config '{config_name}' not found")

        self.set_configs(configs)

    def rename_config(self, old_name: str, new_name: str):
        configs = self.get_configs()
        found = False

        for i, config in enumerate(configs):
            if config.name == old_name:
                config.name = new_name
                found = True
                break

        if not found:
            raise NotFoundError(f"Config '{old_name}' not found")

        self.set_configs(configs)

    def remove_config(self, config_name: str):
        configs = self.get_configs()
        initial_length = len(configs)

        configs = [config for config in configs if config.name != config_name]

        if len(configs) == initial_length:
            raise NotFoundError(f"Config '{config_name}' not found")

        self.set_configs(configs)

    def add_config(self, config_name: str, config: BotConfig):
        configs = self.get_configs()

        for existing_config in configs:
            if existing_config.name == config_name:
                raise ConflictError(f"Config '{config_name}' already exists")

        config.name = config_name
        configs.append(config)
        self.set_configs(configs)

    def contains(self, config_name: str) -> bool:
        configs = self.get_configs()
        return any(config.name == config_name for config in configs)


# TODO GPT generated
class ConfigSqliteDao(ConfigDao):
    def __init__(self, db_path: str = "config.db"):
        import os
        import sqlite3

        self.db_path = db_path
        # Create the database and table if they don't exist
        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS bot_configs (
                name TEXT PRIMARY KEY,
                lowest_price INTEGER,
                volume INTEGER,
                screenshot_delay INTEGER,
                debug_mode INTEGER,
                target_schema_index INTEGER
            )
            """,
            )
            conn.commit()
            conn.close()

    def get_configs(self) -> List[BotConfig]:
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, lowest_price, volume, screenshot_delay, debug_mode, target_schema_index FROM bot_configs")
        rows = cursor.fetchall()
        conn.close()

        configs = []
        for row in rows:
            config = BotConfig(
                name=row[0],
                lowest_price=row[1],
                volume=row[2],
                screenshot_delay=row[3],
                debug_mode=bool(row[4]),
                target_schema_index=row[5],
            )
            configs.append(config)

        return configs

    def set_configs(self, configs: List[BotConfig]):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing configs
        cursor.execute("DELETE FROM bot_configs")

        # Insert all configs
        for config in configs:
            cursor.execute(
                "INSERT INTO bot_configs (name, lowest_price, volume, screenshot_delay, debug_mode, target_schema_index) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    config.name,
                    config.lowest_price,
                    config.volume,
                    config.screenshot_delay,
                    int(config.debug_mode),
                    config.target_schema_index,
                ),
            )

        conn.commit()
        conn.close()

    def update_config(self, config_name: str, config: BotConfig):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if config exists
        cursor.execute("SELECT 1 FROM bot_configs WHERE name = ?", (config_name,))
        if not cursor.fetchone():
            conn.close()
            raise NotFoundError(f"Config '{config_name}' not found")

        # Update the config
        cursor.execute(
            "UPDATE bot_configs SET lowest_price = ?, volume = ?, screenshot_delay = ?, debug_mode = ?, target_schema_index = ? WHERE name = ?",
            (config.lowest_price, config.volume, config.screenshot_delay, int(config.debug_mode), config.target_schema_index, config_name),
        )

        conn.commit()
        conn.close()

    def rename_config(self, old_name: str, new_name: str):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if old config exists
        cursor.execute("SELECT 1 FROM bot_configs WHERE name = ?", (old_name,))
        if not cursor.fetchone():
            conn.close()
            raise NotFoundError(f"Config '{old_name}' not found")

        # Check if new name already exists
        cursor.execute("SELECT 1 FROM bot_configs WHERE name = ?", (new_name,))
        if cursor.fetchone():
            conn.close()
            raise ConflictError(f"Config '{new_name}' already exists")

        # Rename the config
        cursor.execute("UPDATE bot_configs SET name = ? WHERE name = ?", (new_name, old_name))

        conn.commit()
        conn.close()

    def remove_config(self, config_name: str):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if config exists
        cursor.execute("SELECT 1 FROM bot_configs WHERE name = ?", (config_name,))
        if not cursor.fetchone():
            conn.close()
            raise NotFoundError(f"Config '{config_name}' not found")

        # Delete the config
        cursor.execute("DELETE FROM bot_configs WHERE name = ?", (config_name,))

        conn.commit()
        conn.close()

    def add_config(self, config_name: str, config: BotConfig):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if config already exists
        cursor.execute("SELECT 1 FROM bot_configs WHERE name = ?", (config_name,))
        if cursor.fetchone():
            conn.close()
            raise ConflictError(f"Config '{config_name}' already exists")

        # Insert the new config
        cursor.execute(
            "INSERT INTO bot_configs (name, lowest_price, volume, screenshot_delay, debug_mode, target_schema_index) VALUES (?, ?, ?, ?, ?, ?)",
            (config_name, config.lowest_price, config.volume, config.screenshot_delay, int(config.debug_mode), config.target_schema_index),
        )

        conn.commit()
        conn.close()

    def contains(self, config_name: str) -> bool:
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM bot_configs WHERE name = ?", (config_name,))
        exists = cursor.fetchone() is not None

        conn.close()
        return exists


# TODO switch dao
match Config.dao_type:
    case "json":
        dao: ConfigDao = ConfigJsonFileDao()
    case "sqlite":
        dao: ConfigDao = ConfigSqliteDao()
    case _:
        dao: ConfigDao = ConfigMemoryDao()
config_service = ConfigService(dao)
