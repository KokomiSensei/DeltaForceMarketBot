# 设置执行策略为绕过，允许脚本执行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 获取脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 切换到脚本所在目录
Set-Location "$scriptPath"

# 激活 conda 环境
conda activate playground

# 设置 PYTHONPATH 环境变量
$env:PYTHONPATH = $scriptPath

# 运行 Python 脚本
python "$scriptPath\backend\run.py"
