#!/usr/bin/env python3

import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class DownloaderConfig:
    """下载器配置
    
    Attributes:
        chunk_size: 下载块大小（字节）
        status_dir: 下载状态文件保存目录
        max_retry: 下载失败最大重试次数
        status_save_interval: 状态保存间隔（字节）
    """
    chunk_size: int = 1024 * 1024  # 1MB
    status_dir: Path = Path.home() / '.modelscope_downloads'
    max_retry: int = 3
    status_save_interval: int = 10 * 1024 * 1024  # 10MB

    def __post_init__(self):
        """初始化后处理
        
        确保状态目录存在
        """
        self.status_dir.mkdir(exist_ok=True)

    def get_status_file_path(self, model_id: str) -> Path:
        """获取状态文件路径
        
        Args:
            model_id: 模型ID
            
        Returns:
            Path: 状态文件路径
        """
        return self.status_dir / f"{model_id.replace('/', '_')}_status.json"

# 默认配置实例
default_config = DownloaderConfig()