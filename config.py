class Config:
    # 服务器设置
    port = 9876
    host = "0.0.0.0"  # 表示 Flask 服务会监听所有网卡（本机和局域网都能访问）。
    use_reloader = True
    secret_key = "your_secret_key"
    skip_bot_model = True
    # run_in_debug_mode = False
    run_in_debug_mode = True
    dao_type = "memory"
    dao_type = "json"
    dao_type = "sqlite"


class DefaultConfig:
    IDEAL_PRICE = 518
    UNACCEPTABLE_PRICE = 567  # TODO 更直观的设置
    LOOP_GAP = 100
    IS_CONVERTIBLE = True
    IS_KEY_MODE = False
    IS_HALF_COIN_MODE = False
    SCREENSHOT_DELAY_MS = 0
