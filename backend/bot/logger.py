import logging
import logging.handlers
from datetime import datetime
import os


def setup_logging():
    """设置应用程序日志系统"""
    # 创建logs目录（如果不存在）
    # logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    logs_dir = os.path.join("./", 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # 创建并配置logger
    logger = logging.getLogger('BuyBot')
    logger.setLevel(logging.DEBUG)
    
    # 文件处理器 - 日志轮转，每天一个文件，保留30天
    log_file = os.path.join(logs_dir, f'buybot_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=30, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化日志
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()