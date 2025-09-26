# 基于Speciesnt开源模型的陆生脊椎动物识别分类系统

本项目所有开发、测试、运行操作 **必须** 在 Python虚拟环境中执行（虚拟环境建议名称为`speciesnet` ，建议采用Conda方式建立虚拟环境），无虚拟环境下的报错请自行摸索。

一. 项目简介
本项目提供基于Speciesnet模型的Web前端，提供了a.始终剪裁合适区域与b.全图像检测两个Speciesnet模型的变体，提供对上传图片中的陆生脊椎动物进行识别的功能；以下为Speciesnet模型的简介：
https://github.com/google/cameratrapai

二、部署方法
以下部署方法基于您已正确安装Anaconda的情况：
1. 建立虚拟环境：
conda create -n speciesnet python=3.12 -y
conda activate speciesnet

2. 克隆本项目
git clone https://github.com/aeplio/speciesnet

3. 安装并启动项目
3.1 安装并启动后端服务：

# 进入项目后端文件夹
cd speciesnet/backend
# 安装依赖
pip install -r requirements.txt
# 验证依赖
pip install speciesnet
# 预下载模型（可选，建议。首次使用时会自动下载）
python -c "
import kagglehub
kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1a')
kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1b')
"
**注意**: 模型文件约500MB，请确保网络连接稳定。

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

3.2 安装并启动前端服务（需另开一个终端窗口）：
# 进入项目前端文件夹
cd speciesnet/frontend
# 安装npm
npm install    ##如果不行就apt install npm
# 启动前端服务
npm run dev
# 如果前端启动报错，可以尝试：
npm install -g n
n stable    //安装node稳定发行版
//或
n latest    //安装node最新发行版

4. 环境守卫脚本（PowerShell环境，Linux可忽略）
- Python 脚本: `scripts/env_guard.py`
- PowerShell 脚本: `scripts/ensure_env.ps1`

手动运行：
```powershell
conda activate speciesnet
python scripts/env_guard.py
```

或（PowerShell）：
```powershell
./scripts/ensure_env.ps1
```

5. VS Code 保障（Windows环境，Linux可忽略）
- `.vscode/settings.json` 已固定解释器路径。
- 任务执行使用 `conda run -n speciesnet`，参考 `.vscode/tasks.json`。

运行任务：
1. Ctrl+Shift+P 输入 `Tasks: Run Task`
2. 选择 `Run Script (speciesnet)`
3. 也可使用 VS Code 任务：
1. Tasks: Run Task -> `Dev: All`（同时启动后端与前端）

前后端均正常启动后，前端会通过 Vite 代理将以 `/api` 开头的请求转发至 `http://127.0.0.1:8000`，浏览器访问：`http://<你的IP>:3000` 或 `http://localhost:3000` 即可访问项目。
