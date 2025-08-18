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

from backend.bot.config import LocalConfig, MultiConfig

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
st.sidebar.header("配置管理")

# Load all configurations
config_profiles = MultiConfig.load_configs(constants.PathConstants.ConfigFile)
config_names = [config.name for config in config_profiles]
active_config_name = MultiConfig.get_active_config(constants.PathConstants.ConfigFile).name

# Get current status and config
status = get_bot_status()
if status:
    api_config = status["config"]
    running = status["running"]
else:
    # Default values if API is not responding
    api_config = {
        "lowest_price": DefaultConfig.lowest_price,
        "volume": DefaultConfig.volume,
        "screenshot_delay": DefaultConfig.screenshot_delay,
        "debug_mode": DefaultConfig.debug_mode,
        "target_schema_index": DefaultConfig.target_schema_index
    }
    running = False

# Initialize session state if not already initialized
if 'config_profiles' not in st.session_state:
    st.session_state.config_profiles = config_profiles
    
if 'selected_config_name' not in st.session_state:
    st.session_state.selected_config_name = active_config_name
    
if 'editing_config_name' not in st.session_state:
    st.session_state.editing_config_name = ""

# Function to update session state config profiles
def update_session_config_profiles():
    st.session_state.config_profiles = MultiConfig.load_configs(constants.PathConstants.ConfigFile)

# Function to set active config
def set_active_config(config_name):
    MultiConfig.set_active_config(config_name, constants.PathConstants.ConfigFile)
    st.session_state.selected_config_name = config_name
    # Also refresh the config list
    update_session_config_profiles()

# Function to find config by name
def find_config_by_name(name):
    for config in st.session_state.config_profiles:
        if config.name == name:
            return config
    return None

# Function to add a new config
def add_new_config():
    new_name = st.session_state.new_config_name.strip()
    if not new_name:
        st.sidebar.error("配置名称不能为空")
        return
        
    # Check for duplicate name
    if new_name in [config.name for config in st.session_state.config_profiles]:
        st.sidebar.error(f"配置名称 '{new_name}' 已存在")
        return
        
    # Create new config based on the default values
    new_config = LocalConfig()
    new_config.name = new_name
    
    # Add to profiles
    st.session_state.config_profiles.append(new_config)
    MultiConfig.save_configs(st.session_state.config_profiles, constants.PathConstants.ConfigFile)
    
    # Set as selected
    st.session_state.selected_config_name = new_name
    set_active_config(new_name)
    
    # Clear input
    st.session_state.new_config_name = ""
    st.rerun()

# Function to delete a config
def delete_config():
    if len(st.session_state.config_profiles) <= 1:
        st.sidebar.error("无法删除唯一的配置")
        return
        
    config_to_delete = st.session_state.selected_config_name
    
    # Remove from profiles
    st.session_state.config_profiles = [
        config for config in st.session_state.config_profiles 
        if config.name != config_to_delete
    ]
    
    # Set another config as selected
    st.session_state.selected_config_name = st.session_state.config_profiles[0].name
    
    # Save to file
    MultiConfig.save_configs(st.session_state.config_profiles, constants.PathConstants.ConfigFile)
    set_active_config(st.session_state.selected_config_name)
    st.rerun()

# Configuration profile selection
st.sidebar.subheader("选择配置")
config_names = [config.name for config in st.session_state.config_profiles]
selected_index = config_names.index(st.session_state.selected_config_name) if st.session_state.selected_config_name in config_names else 0
selected_config_name = st.sidebar.selectbox(
    "配置方案",
    config_names,
    index=selected_index,
    key="config_selector",
    on_change=lambda: set_active_config(st.session_state.config_selector)
)
st.session_state.selected_config_name = selected_config_name

# Add new configuration input
st.sidebar.subheader("添加新配置")
st.sidebar.text_input("新配置名称", key="new_config_name")
add_col, del_col = st.sidebar.columns(2)
with add_col:
    st.button("添加", on_click=add_new_config)
with del_col:
    st.button("删除当前配置", on_click=delete_config)

# Separator
st.sidebar.markdown("---")

# Bot status indicator in the sidebar
st.sidebar.subheader("机器人状态")
if running:
    st.sidebar.success("运行中")
else:
    st.sidebar.info("已停止")

# Main configuration area
st.header(f"配置设置: {selected_config_name}")

# Get the selected config
selected_config = find_config_by_name(selected_config_name)

if selected_config:
    # Create form for configuration
    with st.form("config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            lowest_price = st.number_input(
                "最低价格 (每个物品)",
                min_value=1,
                value=selected_config.lowest_price,
                help="机器人将在每个物品低于此价格时进行购买"
            )
            
            volume = st.number_input(
                "物品数量",
                min_value=1,
                value=selected_config.volume,
                help="要购买的物品数量"
            )
            
            screenshot_delay = st.number_input(
                "截图延迟 (毫秒)",
                min_value=0,
                value=selected_config.screenshot_delay,
                help="截图之间的延迟（毫秒）"
            )
        
        with col2:
            debug_mode = st.checkbox(
                "调试模式",
                value=selected_config.debug_mode,
                help="在调试模式下，机器人会移动到购买按钮，但不会点击"
            )
            
            target_schema = st.slider(
                "目标方案索引",
                min_value=0,
                max_value=constants.PositionalConstants.Schema.Counts - 1,
                value=selected_config.target_schema_index,
                help="用于物品识别的方案索引"
            )
        
        save_submitted = st.form_submit_button("保存配置")
        
        if save_submitted:
            # Update the config
            selected_config.lowest_price = lowest_price
            selected_config.volume = volume
            selected_config.screenshot_delay = screenshot_delay
            selected_config.debug_mode = debug_mode
            selected_config.target_schema_index = target_schema
            
            # Save to file
            selected_config.to_file(constants.PathConstants.ConfigFile)
            
            # If this is the active config, also update the API
            if selected_config.name == active_config_name:
                new_config = {
                    "lowest_price": lowest_price,
                    "volume": volume,
                    "screenshot_delay": screenshot_delay,
                    "debug_mode": debug_mode,
                    "target_schema_index": target_schema
                }
                response = update_config(new_config)
                if response:
                    st.success("配置已成功更新并应用!")
                else:
                    st.error("配置已保存，但无法更新API")
            else:
                st.success("配置已保存!")
                
            # Refresh the config list
            update_session_config_profiles()
    
    # Apply button (separate from save)
    if selected_config.name != active_config_name:
        if st.button(f"应用此配置 '{selected_config.name}'"):
            # Set as active config
            set_active_config(selected_config.name)
            
            # Update API with this config
            new_config = {
                "lowest_price": selected_config.lowest_price,
                "volume": selected_config.volume,
                "screenshot_delay": selected_config.screenshot_delay,
                "debug_mode": selected_config.debug_mode,
                "target_schema_index": selected_config.target_schema_index
            }
            response = update_config(new_config)
            if response:
                st.success(f"已应用配置 '{selected_config.name}'")
            else:
                st.error("无法更新API配置")
else:
    st.error("找不到选定的配置")

# Main content area
st.header("机器人控制")

# Status indicator
st.subheader("状态")
status_indicator = st.empty()

if running:
    status_indicator.success("机器人正在运行")
else:
    status_indicator.info("机器人已停止")

# Start/Stop buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("启动机器人", disabled=running):
        response = start_bot()
        if response:
            st.success("机器人已启动!")
            time.sleep(1)  # Brief pause to let the status update
            st.rerun()  # Rerun the app to update status

with col2:
    if st.button("停止机器人", disabled=not running):
        response = stop_bot()
        if response:
            st.success("机器人已停止!")
            time.sleep(1)  # Brief pause to let the status update
            st.rerun()  # Rerun the app to update status

# Bot info
st.header("机器人信息")

# Get the active configuration for display
active_config = MultiConfig.get_active_config(constants.PathConstants.ConfigFile)

st.markdown("""
此机器人会在价格低于您指定的阈值时自动购买物品。

**当前应用的配置方案: {}**
- 目标价格: {:.2f} (每个物品)
- 购买数量: {} 个物品
- 截图延迟: {} 毫秒
- 调试模式: {}
- 目标方案索引: {}
""".format(
    active_config.name,
    active_config.lowest_price, 
    active_config.volume, 
    active_config.screenshot_delay, 
    "启用" if active_config.debug_mode else "禁用", 
    active_config.target_schema_index
))

# How to use
st.header("使用方法")
st.markdown("""
1. 在侧边栏中选择一个现有配置或创建新配置
2. 在主界面中调整配置参数
3. 点击"保存配置"按钮保存设置
4. 如果要使用不同的配置，选择该配置并点击"应用此配置"按钮
5. 点击"启动机器人"开始监控
6. 机器人会在价格低于您设定的阈值时自动购买
7. 点击"停止机器人"停止操作

**调试模式:** 启用后，机器人会移动到购买按钮，但不会点击
""")

# Auto-refresh status every 5 seconds
if running:
    st.markdown("状态每5秒自动刷新一次（当机器人运行时）")
    time.sleep(5)
    st.rerun()
