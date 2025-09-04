# 设置执行策略为绕过，允许脚本执行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 获取脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 切换到前端目录
Set-Location "$scriptPath\frontend"

# 输出当前目录信息
Write-Host "正在启动前端服务器，目录: $(Get-Location)"

# 启动服务器 npm run start / npm run dev
npm run start
