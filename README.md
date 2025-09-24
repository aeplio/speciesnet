# SpeciesNet 项目环境约束

本项目所有开发、测试、运行操作 **必须** 在 Conda 环境 `speciesnet` 中执行，禁止跳过或绕过。

## 1. 创建与激活
```powershell
conda create -n speciesnet python=3.12 -y
conda activate speciesnet
```

## 2. 快速验证当前环境
```powershell
python -c "import sys;print(sys.executable)"
# 路径中应包含: speciesnet
```

## 3. 环境守卫脚本
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

## 4. VS Code 保障
- `.vscode/settings.json` 已固定解释器路径。
- 任务执行使用 `conda run -n speciesnet`，参考 `.vscode/tasks.json`。

运行任务：
1. Ctrl+Shift+P 输入 `Tasks: Run Task`
2. 选择 `Run Script (speciesnet)`

## 5. Git Hook 约束
示例 hook 位于 `.githooks/pre-commit`。
启用：
```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

每次提交将自动校验环境；未在正确环境下将拒绝提交。

## 6. 复现/共享环境
导出（仅记录显式安装包）：
```powershell
conda env export --from-history > environment.yml
```
使用：
```powershell
conda env create -f environment.yml
conda activate speciesnet
```

## 7. 常见问题
| 问题 | 说明 | 解决 |
|------|------|------|
| 激活后还是提示未在环境 | 可能开了新终端未激活 | 重新执行 `conda activate speciesnet` |
| VS Code 使用错误解释器 | 未重新选择或缓存旧环境 | Ctrl+Shift+P 选择解释器 |
| Git 提交被拒 | 未激活环境 | 先激活再提交 |

## 8. 后续可扩展
- 集成 `pre-commit` 工具链
- 增加格式化 (black, ruff)
- 添加测试框架 (pytest)

---
严格遵守以上规则以保证环境一致性。

## 模型安装

在首次使用前，需要安装 SpeciesNet 模型：

```powershell
conda activate speciesnet
# 安装 SpeciesNet 包
pip install speciesnet

# 预下载模型（可选，首次使用时会自动下载）
python -c "
import kagglehub
kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1a')
kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1b')
"
```

**注意**: 模型文件约500MB，请确保网络连接稳定。详细安装说明请参考 [QUICK_START.md](QUICK_START.md)。

## 前后端开发启动

1) 后端（FastAPI）：
```powershell
conda activate speciesnet
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2) 前端（Vue+Vite，端口3000）：
```powershell
cd frontend
npm install
npm run dev
```

前端会通过 Vite 代理将以 `/api` 开头的请求转发至 `http://127.0.0.1:8000`。

也可使用 VS Code 任务：
1. Tasks: Run Task -> `Dev: All`（同时启动后端与前端）
2. 浏览器访问：`http://<你的IP>:3000` 或 `http://localhost:3000`
