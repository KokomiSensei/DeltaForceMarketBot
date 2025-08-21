from typing import Optional

from pydantic import BaseModel

# from backend.app import app
from backend.bot.config import BotConfig
from backend.extension.controller_decorators import (
    DeleteMapping,
    GetMapping,
    PatchMapping,
    PostMapping,
    PutMapping,
    RequestBody,
    ResponseBody,
)
from backend.service.bot_service import bot_service
from backend.service.config_service import config_service


class BotConfigOpt(BaseModel):
    lowest_price: Optional[int] = None
    volume: Optional[int] = None
    screenshot_delay: Optional[int] = None
    debug_mode: Optional[bool] = None
    target_schema_index: Optional[int] = None
    name: Optional[str] = None


# Bot Controller APIs


@GetMapping("/api/bot/config")
@ResponseBody
def get_bot_config():
    return bot_service.get_config()


@PostMapping("/api/bot/config")
@RequestBody
@ResponseBody
def set_bot_config(config: BotConfig):
    # 完整替换配置
    bot_service.load_config(config)
    return bot_service.get_config()


@PatchMapping("/api/bot/config")
@RequestBody
@ResponseBody
def update_bot_config(config: BotConfigOpt):
    # 部分更新配置
    current_config = bot_service.get_config()
    updated_config = current_config.model_copy(update=config.model_dump(exclude_unset=True))
    bot_service.load_config(updated_config)
    return bot_service.get_config()


@PostMapping("/api/bot/start")
@ResponseBody
def start_bot() -> dict[str, str]:
    bot_service.start_bot()
    return {"status": "started"}


@PostMapping("/api/bot/stop")
@ResponseBody
def stop_bot() -> dict[str, str]:
    bot_service.stop_bot()
    return {"status": "stopped"}


# Config Controller APIs


@GetMapping("/api/configs")
@ResponseBody
def get_all_configs():
    return config_service.get_configs()


@PostMapping("/api/configs")
@RequestBody
@ResponseBody
def create_config(config: BotConfig):
    # 创建新配置
    config_service.add_config(config.name, config)
    return config


@PutMapping("/api/configs/<name>")
@RequestBody
@ResponseBody
def update_full_config(config: BotConfig, name: str):
    config_service.update_config(name, config)
    return config


@DeleteMapping("/api/configs/<name>")
@ResponseBody
def delete_config(name: str):
    config_service.remove_config(name)
    return {}


@PostMapping("/api/configs/<old_name>/rename/<new_name>")
@ResponseBody
def rename_config(old_name: str, new_name: str):
    config_service.rename_config(old_name, new_name)
    return {}
