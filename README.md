# ModelScope 模型下载工具
## 使用方法
### 基本用法

```bash
# 下载模型
python main.py download <model_id> <save_dir> [options]

# 查看下载状态
python main.py status <model_id>
```

### 使用示例

```bash
# 基本下载示例
python main.py download "deepseek-ai/DeepSeek-R1" ./models

# 使用8个线程并发下载
python main.py download "deepseek-ai/DeepSeek-R1" ./models --max-workers 8

# 设置下载块大小为16MB
python main.py download "deepseek-ai/DeepSeek-R1" ./models --chunk-size 16777216

# 查看下载状态
python main.py status "deepseek-ai/DeepSeek-R1"

# 在后台运行下载任务（使用nohup）
nohup python main.py download "deepseek-ai/DeepSeek-R1" ./models > download.log 2>&1 &

# 查看后台下载日志
tail -f download.log
```

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
4. 使用nohup在后台运行时，下载日志会保存到download.log文件中
5. 断点续传功能会自动保存下载进度，意外中断后重新运行即可继续下载