from __future__ import annotations
import json

from pydantic import BaseModel



class DefaultConfig:
    lowest_price: int = 548
    volume: int = 3540
    screenshot_delay: int = 250
    debug_mode: bool = False
    target_schema_index: int = 4
    
    

class LocalConfig(DefaultConfig, BaseModel):
    @staticmethod
    def from_file(file_path: str) -> DefaultConfig:
        import os
        if not os.path.exists(file_path):
            # File doesn't exist, create a new config with default values
            default_config = LocalConfig()
            LocalConfig.to_file(default_config, file_path)
            return default_config
        
        # File exists, load it
        with open(file_path, "r") as f:
            data = json.load(f)
            # Create a default config and manually set the values
            config = LocalConfig.model_validate(data)
            return config


    def to_file(self, file_path: str) -> None:
        # Convert the config object to a dictionary
        config_dict = self.model_dump()
        with open(file_path, "w") as f:
            json.dump(config_dict, f, indent=4)
