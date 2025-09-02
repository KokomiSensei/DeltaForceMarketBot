class Config:
    # 服务器设置
    port = 9876
    host = "0.0.0.0"  # 表示 Flask 服务会监听所有网卡（本机和局域网都能访问）。
    secret_key = "your_secret_key"

    # 开发设置
    use_reloader = [False, True][0]
    skip_bot_model = [False, True][0]
    run_in_debug_mode = [False, True][0]
    dao_type = ["memory", "json", "sqlite"][2]


class DefaultConfig:
    IDEAL_PRICE = 518
    UNACCEPTABLE_PRICE = 567  # TODO 更直观的设置
    LOOP_GAP = 100
    IS_CONVERTIBLE = True
    IS_KEY_MODE = False
    IS_HALF_COIN_MODE = False
    SCREENSHOT_DELAY_MS = 0
