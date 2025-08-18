import json
import sys
import threading
import time
import argparse
from fastapi import FastAPI, HTTPException
import keyboard
from pydantic import BaseModel
import uvicorn
from typing import Dict, Optional
from backend.bot.buyBot2 import BuyBot, DefaultConfig
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
    lowest_price: Optional[int] = DefaultConfig.MinPrice
    volume: Optional[int] = DefaultConfig.Volume
    screenshot_delay: Optional[int] = DefaultConfig.ScreenshotDelayMs
    debug_mode: Optional[bool] = True

class BotStatus(BaseModel):
    running: bool
    config: Dict

# API Routes
@app.get("/status")
def get_status():
    """Get current bot status and configuration"""
    bot = get_bot_instance()
    return {
        "running": bot.controller.running,
        "config": {
            "lowest_price": bot.lowest_price,
            "volume": bot.volume,
            "screenshot_delay": bot.screenshot_delay,
            "debug_mode": bot.debug_mode
        }
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
    
    if config.lowest_price is not None:
        bot.lowest_price = config.lowest_price
    if config.volume is not None:
        bot.volume = config.volume
    if config.screenshot_delay is not None:
        bot.screenshot_delay = config.screenshot_delay
    if config.debug_mode is not None:
        bot.debug_mode = config.debug_mode
    
    logger.info(f"Configuration updated: {config.dict(exclude_unset=True)}")
    return {"message": "Configuration updated successfully"}

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
