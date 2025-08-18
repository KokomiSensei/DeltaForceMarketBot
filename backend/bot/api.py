import json
import sys
import threading
import time
import argparse
from fastapi import FastAPI, HTTPException
import keyboard
from pydantic import BaseModel
import uvicorn
from typing import Dict, Optional, List
from backend.bot.buyBot2 import BuyBot
from backend.bot.config import DefaultConfig, LocalConfig, MultiConfig
from backend.bot import constants
from backend.bot.logger import logger

# FastAPI app
app = FastAPI(title="DeltaForce Market Bot API")

# Bot instance and state
bot_instance = None
bot_thread = None
bot_running = False

# Create or get bot instance
def get_bot_instance():
    global bot_instance
    if bot_instance is None:
        logger.info("Creating new BuyBot instance")
        bot_instance = BuyBot()
    return bot_instance

# Data models
class BotConfig(BaseModel):
    lowest_price: Optional[int] = DefaultConfig.lowest_price
    volume: Optional[int] = DefaultConfig.volume
    screenshot_delay: Optional[int] = DefaultConfig.screenshot_delay
    debug_mode: Optional[bool] = DefaultConfig.debug_mode
    target_schema_index: Optional[int] = DefaultConfig.target_schema_index
    config_name: Optional[str] = None

class BotStatus(BaseModel):
    running: bool
    config: Dict
    active_config_name: Optional[str] = None
    available_configs: Optional[list] = None

# API Routes
@app.get("/status")
def get_status():
    """Get current bot status and configuration"""
    bot = get_bot_instance()
    
    # Get all available configs
    configs = MultiConfig.load_configs(constants.PathConstants.ConfigFile)
    config_names = [config.name for config in configs]
    active_config = MultiConfig.get_active_config(constants.PathConstants.ConfigFile)
    
    return {
        "running": bot.controller.running,
        "config": {
            "lowest_price": bot.config.lowest_price,
            "volume": bot.config.volume,
            "screenshot_delay": bot.config.screenshot_delay,
            "debug_mode": bot.config.debug_mode,
            "target_schema_index": bot.config.target_schema_index
        },
        "active_config_name": active_config.name,
        "available_configs": config_names
    }

@app.post("/start")
def start_bot():
    """Start the bot with current configuration"""
    bot = get_bot_instance()
    if bot.controller.running:
        return {"message": "Bot is already running"}
    
    bot.controller.start_bot()
    return {"message": "Bot started successfully"}

@app.post("/stop")
def stop_bot():
    """Stop the bot"""
    bot = get_bot_instance()
    if not bot.controller.running:
        return {"message": "Bot is not running"}
    
    bot.controller.stop_bot()
    return {"message": "Bot stopped successfully"}

@app.post("/config")
def update_config(config: BotConfig):
    """Update bot configuration"""
    bot = get_bot_instance()
    
    # Update bot instance config
    if config.lowest_price is not None:
        bot.config.lowest_price = config.lowest_price
    if config.volume is not None:
        bot.config.volume = config.volume
    if config.screenshot_delay is not None:
        bot.config.screenshot_delay = config.screenshot_delay
    if config.debug_mode is not None:
        bot.config.debug_mode = config.debug_mode
    if config.target_schema_index is not None:
        bot.config.target_schema_index = config.target_schema_index
    
    # If a config name is provided, update the named config and set it as active
    if config.config_name is not None:
        # Get all configs
        configs = MultiConfig.load_configs(constants.PathConstants.ConfigFile)
        found = False
        
        # Look for the named config
        for i, cfg in enumerate(configs):
            if cfg.name == config.config_name:
                # Update the config with the new values
                if config.lowest_price is not None:
                    configs[i].lowest_price = config.lowest_price
                if config.volume is not None:
                    configs[i].volume = config.volume
                if config.screenshot_delay is not None:
                    configs[i].screenshot_delay = config.screenshot_delay
                if config.debug_mode is not None:
                    configs[i].debug_mode = config.debug_mode
                if config.target_schema_index is not None:
                    configs[i].target_schema_index = config.target_schema_index
                found = True
                break
        
        if found:
            # Save all configs back to file
            MultiConfig.save_configs(configs, constants.PathConstants.ConfigFile)
            # Set this config as active
            MultiConfig.set_active_config(config.config_name, constants.PathConstants.ConfigFile)
        else:
            logger.warning(f"Config '{config.config_name}' not found")
    
    logger.info(f"Configuration updated: {config.model_dump(exclude_unset=True)}")
    return {"message": "Configuration updated successfully"}

@app.get("/configs")
def get_configs():
    """Get all available configurations"""
    configs = MultiConfig.load_configs(constants.PathConstants.ConfigFile)
    active_config = MultiConfig.get_active_config(constants.PathConstants.ConfigFile)
    
    return {
        "configs": [config.model_dump() for config in configs],
        "active_config_name": active_config.name
    }

@app.post("/configs/activate/{config_name}")
def activate_config(config_name: str):
    """Set a configuration as active"""
    configs = MultiConfig.load_configs(constants.PathConstants.ConfigFile)
    
    # Check if config exists
    config_exists = any(config.name == config_name for config in configs)
    if not config_exists:
        return {"message": f"Configuration '{config_name}' not found", "success": False}
    
    # Set as active
    MultiConfig.set_active_config(config_name, constants.PathConstants.ConfigFile)
    
    # Find the config to update bot instance
    bot = get_bot_instance()
    for config in configs:
        if config.name == config_name:
            bot.config.lowest_price = config.lowest_price
            bot.config.volume = config.volume
            bot.config.screenshot_delay = config.screenshot_delay
            bot.config.debug_mode = config.debug_mode
            bot.config.target_schema_index = config.target_schema_index
            break
    
    logger.info(f"Activated configuration: {config_name}")
    return {"message": f"Configuration '{config_name}' activated", "success": True}

def run_api_server(host="127.0.0.1", port=8000, reload=False):
    """Run the FastAPI server"""
    uvicorn.run('api:app', host=host, port=port, reload=reload)

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="DeltaForce Market Bot API Server")
        parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
        args = parser.parse_args()

        from backend.bot.adminAuth import is_admin, run_as_admin
        if not is_admin():
            logger.info("Requesting administrator privileges...")
            run_as_admin()

        # Set up keyboard hotkeys
        keyboard.add_hotkey('f8', start_bot) # type: ignore
        keyboard.add_hotkey('f9', stop_bot) # type: ignore

        # 运行API服务器
        run_api_server(reload=args.reload)
    except Exception as e:
        logger.error(f"Error occurred while running API server: {e}")
    input("Press Enter to exit...")
