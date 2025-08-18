from __future__ import annotations
import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field



class DefaultConfig:
    lowest_price: int = 548
    volume: int = 3540
    screenshot_delay: int = 250
    debug_mode: bool = False
    target_schema_index: int = 4
    
    

class LocalConfig(DefaultConfig, BaseModel):
    name: str = "Default"
    
    @staticmethod
    def from_file(file_path: str) -> DefaultConfig:
        import os
        if not os.path.exists(file_path):
            # File doesn't exist, create a new config with default values
            default_config = LocalConfig()
            MultiConfig.save_configs([default_config], file_path)
            return default_config
        
        # File exists, load it
        try:
            configs = MultiConfig.load_configs(file_path)
            if configs and len(configs) > 0:
                return configs[0]  # Return the first config as default
            else:
                # No configs found, create a default one
                default_config = LocalConfig()
                MultiConfig.save_configs([default_config], file_path)
                return default_config
        except Exception as e:
            # If there's an error with the new format, try loading the old format
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                    # Create a default config from the old format
                    config = LocalConfig.model_validate(data)
                    # Save in the new format for future use
                    MultiConfig.save_configs([config], file_path)
                    return config
                except Exception as inner_e:
                    # If that also fails, create a new default config
                    default_config = LocalConfig()
                    MultiConfig.save_configs([default_config], file_path)
                    return default_config


    def to_file(self, file_path: str) -> None:
        # Load existing configs
        configs = MultiConfig.load_configs(file_path)
        
        # Find if this config already exists by name
        found = False
        for i, config in enumerate(configs):
            if config.name == self.name:
                # Replace the existing config
                configs[i] = self
                found = True
                break
        
        if not found:
            # Add as a new config
            configs.append(self)
        
        # Save all configs back to file
        MultiConfig.save_configs(configs, file_path)


class MultiConfig(BaseModel):
    configs: List[LocalConfig] = Field(default_factory=list)
    active_config_name: Optional[str] = None
    
    @staticmethod
    def load_configs(file_path: str) -> List[LocalConfig]:
        if not os.path.exists(file_path):
            return [LocalConfig()]
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
                if isinstance(data, dict) and "configs" in data:
                    # New format with multiple configs
                    multi_config = MultiConfig.model_validate(data)
                    return multi_config.configs
                elif isinstance(data, list):
                    # List of configs
                    return [LocalConfig.model_validate(item) for item in data]
                else:
                    # Old single config format
                    config = LocalConfig.model_validate(data)
                    return [config]
        except Exception as e:
            # If error, return default config
            return [LocalConfig()]
    
    @staticmethod
    def save_configs(configs: List[LocalConfig], file_path: str) -> None:
        # Find active config
        active_name = None
        if configs:
            active_name = configs[0].name
        
        multi_config = MultiConfig(configs=configs, active_config_name=active_name)
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(multi_config.model_dump(), f, indent=4)
    
    @staticmethod
    def get_active_config(file_path: str) -> LocalConfig:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
                if isinstance(data, dict) and "configs" in data:
                    multi_config = MultiConfig.model_validate(data)
                    
                    if multi_config.active_config_name:
                        for config in multi_config.configs:
                            if config.name == multi_config.active_config_name:
                                return config
                    
                    if multi_config.configs:
                        return multi_config.configs[0]
                
            # If no active config found, return default
            return LocalConfig()
        except Exception as e:
            return LocalConfig()
    
    @staticmethod
    def set_active_config(config_name: str, file_path: str) -> None:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            if isinstance(data, dict) and "configs" in data:
                multi_config = MultiConfig.model_validate(data)
                multi_config.active_config_name = config_name
                
                with open(file_path, "w") as f:
                    json.dump(multi_config.model_dump(), f, indent=4)
        except Exception as e:
            pass  # Silently fail if file doesn't exist yet
