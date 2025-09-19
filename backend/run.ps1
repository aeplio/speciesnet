Param()
# 确保在 speciesnet 环境（从仓库根目录或backend目录运行都可）
$root = Split-Path -Path $PSScriptRoot -Parent
& "$root/scripts/ensure_env.ps1"

# 安装依赖（如已安装会跳过）
python -m pip install --upgrade pip
pip install -r "$PSScriptRoot/requirements.txt"

# 启动 Uvicorn (0.0.0.0 便于局域网访问)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
