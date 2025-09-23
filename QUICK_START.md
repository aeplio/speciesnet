# SpeciesNet 一键部署使用说明

## 🚀 快速开始

### 方法一：完整自动化安装（推荐新环境）

适用于全新的 Ubuntu/Debian 系统：

```bash
# 1. 下载项目
git clone https://github.com/aeplio/speciesnet.git
cd speciesnet

# 2. 运行完整安装脚本（需要 root 权限）
sudo bash install.sh

# 3. 安装完成后启动服务
./start_all.sh
```

### 方法二：快速安装（已有环境）

适用于已安装 Python 和 Node.js 的系统：

```bash
# 1. 进入项目目录
cd speciesnet

# 2. 运行快速安装脚本
bash quick_install.sh

# 3. 启动服务
./quick_start.sh
```

### 方法三：Docker 部署（推荐生产环境）

```bash
# 1. 使用 Docker Compose
docker-compose up -d

# 2. 查看服务状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f
```

## 📋 安装后验证

### 检查服务状态

```bash
# 检查后端服务
curl http://localhost:8000/docs

# 检查前端服务
curl http://localhost:3000
```

### 测试识别功能

```bash
# 创建测试图片
python3 -c "
from PIL import Image
img = Image.new('RGB', (224, 224), color=(128, 64, 192))
img.save('test.jpg')
"

# 测试 API
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@test.jpg" \
  -F "model=v4.0.1a"
```

## 🌐 访问地址

安装完成后，可以通过以下地址访问：

- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:8000  
- **API 文档**: http://localhost:8000/docs

## 🛠️ 管理命令

### 启动服务

```bash
# 完整安装版本
./start_all.sh      # 启动所有服务
./start_backend.sh  # 仅启动后端
./start_frontend.sh # 仅启动前端

# 快速安装版本  
./quick_start.sh    # 启动所有服务
```

### 停止服务

```bash
# 完整安装版本
./stop_all.sh       # 停止所有服务

# 快速安装版本
./quick_stop.sh     # 停止所有服务

# Docker 版本
docker-compose down # 停止 Docker 服务
```

### 查看日志

```bash
# 查看后端日志
tail -f backend.log

# 查看 Docker 日志
docker-compose logs -f

# 查看系统服务日志（完整安装）
sudo journalctl -u speciesnet-backend -f
```

## 🔧 故障排除

### 常见问题及解决方案

1. **端口被占用**
   ```bash
   # 查看端口占用
   sudo netstat -tlnp | grep :8000
   sudo netstat -tlnp | grep :3000
   
   # 杀死占用进程
   sudo pkill -f "uvicorn app.main:app"
   sudo pkill -f "npm run dev"
   ```

2. **权限问题**
   ```bash
   # 给脚本执行权限
   chmod +x *.sh
   ```

3. **Python 环境问题**
   ```bash
   # 检查环境
   conda env list
   conda activate speciesnet
   python -c "import speciesnet; print('OK')"
   ```

4. **模型下载失败**
   ```bash
   # 手动重新下载
   conda activate speciesnet
   python -c "
   import kagglehub
   kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1a', force_download=True)
   kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1b', force_download=True)
   "
   ```

5. **前端依赖安装失败**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

## 📊 系统要求

### 最低要求
- **操作系统**: Ubuntu 18.04+ 或 Debian 9+
- **内存**: 4GB RAM
- **存储**: 10GB 可用空间
- **网络**: 稳定的互联网连接（用于下载模型）

### 推荐配置
- **内存**: 8GB+ RAM
- **存储**: 20GB+ 可用空间
- **CPU**: 4核以上处理器

## 🔄 更新和维护

### 更新项目代码

```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖
bash quick_install.sh
```

### 清理和重装

```bash
# 清理 Conda 环境
conda env remove -n speciesnet

# 清理 Docker
docker-compose down --rmi all --volumes

# 重新安装
bash install.sh  # 或 bash quick_install.sh
```

## 📞 获取支持

如果遇到问题：

1. 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 详细部署文档
2. 查看 [FIX_REPORT.md](FIX_REPORT.md) 修复报告
3. 检查项目 Issues: https://github.com/aeplio/speciesnet/issues
4. 提交新的 Issue 描述遇到的问题

## 📝 开发模式

如需进行开发：

```bash
# 激活环境
conda activate speciesnet

# 启动后端开发服务器
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端开发服务器
cd frontend
npm run dev
```

---

**提示**: 首次安装可能需要较长时间下载模型文件（约500MB），请保持网络连接稳定。