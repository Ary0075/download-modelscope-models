# ModelScope 模型下载工具

这是一个用于从 ModelScope 下载模型的命令行工具，支持断点续传和后台下载功能。

## 功能特点

- 支持断点续传，意外中断后可继续下载
- 多线程并行下载，提高下载速度
- 文件完整性校验，确保下载文件的正确性
- 后台下载模式，可在下载过程中执行其他任务
- 下载进度实时显示
- 支持查看下载状态和历史记录

## 安装方法

```bash
# 克隆项目
git clone https://github.com/yourusername/download-modelscope-models.git
cd download-modelscope-models

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 下载模型
python main.py download <model_id> <save_dir> [options]

# 查看下载状态
python main.py status <model_id>
```

### 参数说明

#### 必选参数

- `model_id`: ModelScope模型ID，例如 "deepseek-ai/DeepSeek-R1"
- `save_dir`: 模型文件保存目录，支持相对路径或绝对路径

#### 可选参数

- `--max-workers <num>`: 最大并发下载线程数，默认为4
- `--background`: 启用后台下载模式，下载过程中可执行其他任务
- `--no-verify`: 跳过文件完整性校验
- `--retry <num>`: 下载失败时的重试次数，默认为3次
- `--chunk-size <size>`: 下载块大小（字节），默认为8MB

### 使用示例

```bash
# 基本下载示例
python main.py download "deepseek-ai/DeepSeek-R1" ./models

# 使用8个线程并发下载
python main.py download "deepseek-ai/DeepSeek-R1" ./models --max-workers 8

# 后台下载模式
python main.py download "deepseek-ai/DeepSeek-R1" ./models --background

# 设置下载块大小为16MB
python main.py download "deepseek-ai/DeepSeek-R1" ./models --chunk-size 16777216

# 查看下载状态
python main.py status "deepseek-ai/DeepSeek-R1"
```

## 项目结构

```
.
├── README.md           # 项目说明文档
├── main.py            # 命令行入口程序
├── requirements.txt   # 项目依赖
└── src/               # 源代码目录
    ├── __init__.py    # 包初始化文件
    ├── config.py      # 配置管理
    ├── downloader.py  # 下载器核心实现
    ├── logger.py      # 日志管理
    └── status_manager.py # 下载状态管理
```

## 注意事项

1. 确保有足够的磁盘空间存储模型文件
2. 下载大型模型时建议使用稳定的网络连接
3. 可以通过status命令随时查看下载进度
4. 后台下载模式下，可以使用status命令查看实时进度
5. 断点续传功能会自动保存下载进度，意外中断后重新运行即可继续下载