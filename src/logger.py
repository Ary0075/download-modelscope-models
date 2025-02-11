#!/usr/bin/env python3

import sys
import logging
from pathlib import Path
from typing import Optional

class DownloaderLogger:
    """下载器日志管理器
    
    负责管理日志的配置、格式化和输出。支持控制台输出和文件输出。
    
    Attributes:
        logger: logging.Logger实例
        log_file: 日志文件路径
    """
    
    def __init__(self, name: str = 'modelscope_downloader', log_file: Optional[Path] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.log_file = log_file
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 如果指定了日志文件，添加文件处理器
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """记录信息级别的日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告级别的日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误级别的日志"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """记录调试级别的日志"""
        self.logger.debug(message)
    
    def exception(self, message: str):
        """记录异常信息，包含堆栈跟踪"""
        self.logger.exception(message)

# 默认日志实例
default_logger = DownloaderLogger()