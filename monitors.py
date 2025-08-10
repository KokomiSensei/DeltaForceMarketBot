from PyQt5.QtWidgets import QApplication, QMainWindow
import ctypes
from ctypes import wintypes


def get_monitor_counts(app: QApplication) -> int:
    """
    获取连接的显示器数量
    """
    return len(app.screens())



def set_window_position(app: QApplication, window: QMainWindow, target_screen_number: int, x: int, y: int):
    """
    :param target_screen_number: 目标屏幕的编号 (从1开始)
    :param x: 目标位置的x坐标（最左为0）
    :param y: 目标位置的y坐标（最上为0）
    :raise ValueError: 如果目标屏幕编号超出范围
    """
    screens = { int(screen.name().split("DISPLAY")[-1]) : screen for screen in  app.screens()}
    print(f"QT func: { [ screen.geometry() for screen in screens.values() ]}")
    if target_screen_number > len(screens):
        raise ValueError("目标屏幕编号超出范围")

    target_screen = screens[target_screen_number]
    
    # 获取目标屏幕的几何信息
    screen_geometry = target_screen.geometry()
    
    # 在目标屏幕上的特定位置显示窗口
    window.move(screen_geometry.left() + x, screen_geometry.top() + y)
    
def set_console_window_position(target_monitor_number: int, x: int, y: int):
    """
    :param target_screen_number: 目标屏幕的编号 (从1开始)
    :param x: 目标位置的x坐标（最左为0）
    :param y: 目标位置的y坐标（最上为0）

    :raise ValueError: 如果目标屏幕编号超出范围；如果没找到控制台窗口
    """
    # 尝试设置控制台窗口位置


    
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    
    SW_RESTORE = 9
    
    # 获取控制台窗口句柄
    hwnd = kernel32.GetConsoleWindow()
    
    # 如果存在控制台窗口
    if not hwnd:
        raise ValueError("控制台窗口不存在")
    

    
    # 枚举显示器的回调函数
    def MonitorEnumProc(hMonitor, hdcMonitor, lprcMonitor, dwData):
        monitors.append((lprcMonitor.contents.left, lprcMonitor.contents.top, 
                        lprcMonitor.contents.right, lprcMonitor.contents.bottom))
        return True
    
    # 定义回调函数的原型
    MonitorEnumProcType = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.POINTER(wintypes.RECT),
        ctypes.c_ulong
    )
    
    # 枚举所有显示器
    monitors = []
    callback = MonitorEnumProcType(MonitorEnumProc)
    user32.EnumDisplayMonitors(None, None, callback, 0)
    print(f"console func: {monitors}")
    
    # 确保目标显示器索引有效
    if target_monitor_number > len(monitors):
        raise ValueError(f"目标显示器{target_monitor_number}不存在，只有{len(monitors )}块显示器")

    # 获取指定显示器的位置信息
    monitor_index = target_monitor_number-1 
    monitor_left, monitor_top, monitor_right, monitor_bottom = monitors[monitor_index]
    
    # 在目标显示器上定位窗口(左上角坐标为显示器起始点+相对位置)
    x = monitor_left + x
    y = monitor_top + y
    width = 800
    height = 600
    
    # 移动窗口到指定显示器上的指定位置
    user32.SetWindowPos(hwnd, 0, x, y, width, height, 0x0040)
    # 确保窗口可见
    user32.ShowWindow(hwnd, SW_RESTORE)

