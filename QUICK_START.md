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

## 🤖 模型安装

### 自动安装模型（推荐）

在首次运行识别功能时，系统会自动下载所需的 SpeciesNet 模型：

```bash
# 激活环境
conda activate speciesnet

# 自动下载模型（首次运行时）
python -c "
import speciesnet
print('模型将在首次使用时自动下载...')
"
```

### 手动预安装模型

为避免首次使用时等待下载，可以预先安装模型：

```bash
# 激活环境
conda activate speciesnet

# 下载 v4.0.1a 和 v4.0.1b 模型
python -c "
import kagglehub
print('正在下载 SpeciesNet v4.0.1a 模型...')
kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1a')
print('正在下载 SpeciesNet v4.0.1b 模型...')
kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1b')
print('模型下载完成！')
"
```

### 验证模型安装

```bash
# 验证模型文件存在
conda activate speciesnet
python -c "
import os
import kagglehub

# 检查模型缓存目录
cache_dir = os.path.expanduser('~/.cache/kagglehub/models/google/speciesnet')
if os.path.exists(cache_dir):
    print('✓ 模型缓存目录存在')
    
    # 检查 v4.0.1a
    v4_0_1a = os.path.join(cache_dir, 'pyTorch/v4.0.1a')
    if os.path.exists(v4_0_1a):
        print('✓ v4.0.1a 模型已安装')
    else:
        print('✗ v4.0.1a 模型未找到')
    
    # 检查 v4.0.1b  
    v4_0_1b = os.path.join(cache_dir, 'pyTorch/v4.0.1b')
    if os.path.exists(v4_0_1b):
        print('✓ v4.0.1b 模型已安装')
    else:
        print('✗ v4.0.1b 模型未找到')
else:
    print('✗ 模型缓存目录不存在，请先下载模型')
"
```

### 模型兼容性修复

如果遇到 PyTorch 加载模型时的兼容性问题：

```bash
# 检查 PyTorch 版本
conda activate speciesnet
python -c "import torch; print(f'PyTorch 版本: {torch.__version__}')"

# 如果是 PyTorch 2.6+ 版本，系统已自动修复 weights_only 参数问题
# 如遇到问题，可以手动验证修复是否生效：
python -c "
import speciesnet
print('测试分类器加载...')
classifier = speciesnet.SpeciesNetClassifier('kaggle:google/speciesnet/pyTorch/v4.0.1a')
print('✓ 分类器加载成功')
"
```

### 模型存储位置

```bash
# 模型默认存储位置
echo '模型存储目录:'
echo "~/.cache/kagglehub/models/google/speciesnet/"
echo "具体路径: $(echo ~/.cache/kagglehub/models/google/speciesnet/)"

# 查看模型文件大小
du -sh ~/.cache/kagglehub/models/google/speciesnet/ 2>/dev/null || echo "模型目录不存在"
```

**注意事项：**
- 模型文件总大小约 500MB，请确保有足够的存储空间
- 首次下载需要稳定的网络连接，建议在网络良好的环境下进行
- 如果下载中断，可以重新运行下载命令，系统会自动续传
- 模型文件下载后会缓存在本地，后续使用无需重新下载

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
   # 手动重新下载（强制重新下载）
   conda activate speciesnet
   python -c "
   import kagglehub
   print('强制重新下载 v4.0.1a 模型...')
   kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1a', force_download=True)
   print('强制重新下载 v4.0.1b 模型...')
   kagglehub.model_download('google/speciesnet/pyTorch/v4.0.1b', force_download=True)
   print('模型重新下载完成！')
   "
   ```

5. **模型加载错误**
   ```bash
   # 检查模型文件完整性
   conda activate speciesnet
   python -c "
   import torch
   import os
   
   model_paths = [
       '~/.cache/kagglehub/models/google/speciesnet/pyTorch/v4.0.1a/1/always_crop_99710272_22x8_v12_epoch_00148.pt',
       '~/.cache/kagglehub/models/google/speciesnet/pyTorch/v4.0.1b/1/full_image_88545560_22x8_v12_epoch_00153.pt'
   ]
   
   for path in model_paths:
       full_path = os.path.expanduser(path)
       if os.path.exists(full_path):
           try:
               checkpoint = torch.load(full_path, map_location='cpu', weights_only=False)
               print(f'✓ {path} 加载成功')
           except Exception as e:
               print(f'✗ {path} 加载失败: {e}')
       else:
           print(f'✗ {path} 文件不存在')
   "
   
   # 如果文件损坏，删除并重新下载
   rm -rf ~/.cache/kagglehub/models/google/speciesnet/
   # 然后重新运行模型下载命令
   ```

6. **PyTorch 兼容性问题**
   ```bash
   # 检查并修复 PyTorch 2.6+ 兼容性问题
   conda activate speciesnet
   python -c "
   import torch
   print(f'PyTorch 版本: {torch.__version__}')
   
   # 测试 SpeciesNet 导入和基本功能
   try:
       import speciesnet
       print('✓ SpeciesNet 导入成功')
       
       # 测试分类器创建
       classifier = speciesnet.SpeciesNetClassifier('kaggle:google/speciesnet/pyTorch/v4.0.1a')
       print('✓ 分类器创建成功')
   except Exception as e:
       print(f'✗ SpeciesNet 测试失败: {e}')
       print('请检查模型安装或 PyTorch 版本兼容性')
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