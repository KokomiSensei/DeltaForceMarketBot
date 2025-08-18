import streamlit as st
import requests
import json
import time
import os
import sys
import subprocess
from threading import Thread
from backend.bot import constants
from backend.bot.buyBot2 import DefaultConfig
import socket

from backend.bot.config import LocalConfig

# Add API server URL
API_URL = "http://127.0.0.1:8000"

# Check if the port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Start API server if not running
def start_api_server():
    if not is_port_in_use(8000):
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # Set the command to run the API server
        api_script_path = os.path.join(current_dir, "api.py")
        
        try:
            # Run the API server in a separate process
            subprocess.Popen([sys.executable, api_script_path], 
                            cwd=parent_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
            
            # Wait for the server to start
            for _ in range(5):  # Wait up to 5 seconds
                if is_port_in_use(8000):
                    return True
                time.sleep(1)
        except Exception as e:
            st.error(f"Failed to start API server: {str(e)}")
            return False
    else:
        # Port is already in use, which likely means the API server is running
        return True
    
    return False

# Check if API server is available
api_server_running = is_port_in_use(8000)

# Display warning if API server is not running
if not api_server_running:
    st.warning("""
    API服务器未运行! 无法与后端通信。
    
    请在终端运行以下命令启动API服务器:
    ```
    python run_app.py --api-only
    ```
    
    或者重新启动完整应用:
    ```
    python run_app.py
    ```
    """)
    
    if st.button("尝试自动启动API服务器"):
        with st.spinner("正在启动API服务器..."):
            if start_api_server():
                st.success("API服务器成功启动!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("API服务器启动失败。请手动启动。")
                st.code("python run_app.py --api-only", language="bash")

# Function to get bot status
def get_bot_status():
    try:
        response = requests.get(f"{API_URL}/status")
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error connecting to API server: {e}")
        return None

# Function to start the bot
def start_bot():
    try:
        response = requests.post(f"{API_URL}/start")
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error starting bot: {e}")
        return None

# Function to stop the bot
def stop_bot():
    try:
        response = requests.post(f"{API_URL}/stop")
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error stopping bot: {e}")
        return None

# Function to update configuration
def update_config(config):
    try:
        response = requests.post(f"{API_URL}/config", json=config)
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error updating configuration: {e}")
        return None

# App title
st.title("Delta Force Market Bot")

# Sidebar for configuration
st.sidebar.header("Bot Configuration")

# Get current status and config
status = get_bot_status()
if status:
    config = status["config"]
    running = status["running"]
else:
    # Default values if API is not responding
    config = {
        "lowest_price": DefaultConfig.lowest_price,
        "volume": DefaultConfig.volume,
        "screenshot_delay": DefaultConfig.screenshot_delay,
        "debug_mode": DefaultConfig.debug_mode,
        "target_schema_index": DefaultConfig.target_schema_index
    }
    running = False

# Configuration inputs
lowest_price = st.sidebar.number_input(
    "Lowest Price (per item)",
    min_value=1,
    value=config["lowest_price"],
    help="The minimum price per item below which the bot will make a purchase",
    on_change=lambda: update_config({"lowest_price": lowest_price})
)

volume = st.sidebar.number_input(
    "Volume",
    min_value=1,
    value=config["volume"],
    help="The number of items to purchase",
    on_change=lambda: update_config({"volume": volume})
)

screenshot_delay = st.sidebar.number_input(
    "Screenshot Delay (ms)",
    min_value=0,
    value=config["screenshot_delay"],
    help="Delay in milliseconds between taking screenshots",
    on_change=lambda: update_config({"screenshot_delay": screenshot_delay})
)

debug_mode = st.sidebar.checkbox(
    "Debug Mode",
    value=config["debug_mode"],
    help="In debug mode, the bot will move to the purchase button but not click it",
    on_change=lambda: update_config({"debug_mode": debug_mode})
)

target_schema = st.sidebar.slider(
    "Target Schema Index",
    min_value=0,
    max_value=constants.PositionalConstants.Schema.Counts - 1,
    value=config["target_schema_index"],
    help="The schema index to use for item identification",
    on_change=lambda: update_config({"target_schema_index": target_schema})
)

# Save configuration button
if st.sidebar.button("Save Configuration"):
    new_config = {
        "lowest_price": lowest_price,
        "volume": volume,
        "screenshot_delay": screenshot_delay,
        "debug_mode": debug_mode,
        "target_schema_index": target_schema
    }
    response = update_config(new_config)
    if response:
        st.sidebar.success("Configuration updated successfully!")
        config = LocalConfig.model_validate(new_config)
        config.to_file(constants.PathConstants.ConfigFile)

# Main content area
st.header("Bot Control")

# Status indicator
st.subheader("Status")
status_indicator = st.empty()

if running:
    status_indicator.success("Bot is running")
else:
    status_indicator.info("Bot is stopped")

# Start/Stop buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Start Bot", disabled=running):
        response = start_bot()
        if response:
            st.success("Bot started!")
            time.sleep(1)  # Brief pause to let the status update
            st.rerun()  # Rerun the app to update status

with col2:
    if st.button("Stop Bot", disabled=not running):
        response = stop_bot()
        if response:
            st.success("Bot stopped!")
            time.sleep(1)  # Brief pause to let the status update
            st.rerun()  # Rerun the app to update status

# Bot info
st.header("Bot Information")
st.markdown("""
This bot automatically purchases items when the price falls below your specified threshold.

**Current Configuration:**
- Target price: {:.2f} (per item)
- Purchase volume: {} items
- Screenshot delay: {} ms
- Debug mode: {}
- Target schema index: {}
""".format(lowest_price, volume, screenshot_delay, "Enabled" if debug_mode else "Disabled", target_schema))

# How to use
st.header("How to Use")
st.markdown("""
1. Configure your desired price and volume in the sidebar
2. Click "Apply Configuration" to save settings
3. Click "Start Bot" to begin monitoring
4. The bot will automatically purchase when prices drop below your threshold
5. Click "Stop Bot" to halt operation

**Debug Mode:** When enabled, the bot will move to the purchase button but not click it
""")

# Auto-refresh status every 5 seconds
if running:
    st.markdown("Status auto-refreshes every 5 seconds while bot is running")
    time.sleep(5)
    st.rerun()
