#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Dict, List, Optional
from .downloader import ModelFile
from .config import default_config
from .logger import default_logger

def save_download_status(model_id: str, model_files: List[ModelFile]):
    """保存下载状态到临时文件
    
    Args:
        model_id: 模型ID
        model_files: 模型文件列表
    """
    status_file = default_config.get_status_file_path(model_id)
    
    status_data = {
        'model_id': model_id,
        'files': [{
            'filename': f.filename,
            'file_size': f.file_size,
            'downloaded_size': f.downloaded_size,
            'status': f.status
        } for f in model_files]
    }
    
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)

def load_download_status(model_id: str) -> Optional[Dict]:
    """从临时文件加载下载状态
    
    Args:
        model_id: 模型ID
        
    Returns:
        Optional[Dict]: 下载状态数据，如果文件不存在则返回None
    """
    status_file = default_config.get_status_file_path(model_id)
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    return None

def show_download_status(model_id: str):
    """显示下载状态
    
    Args:
        model_id: 模型ID
    """
    status_data = load_download_status(model_id)
    if not status_data:
        default_logger.info(f"未找到模型 {model_id} 的下载记录")
        return

    default_logger.info(f"\n模型 {model_id} 的下载状态:")
    total_size = 0
    downloaded_size = 0
    completed_count = 0
    failed_count = 0

    for file_info in status_data['files']:
        total_size += file_info['file_size']
        downloaded_size += file_info['downloaded_size']
        if file_info['status'] == 'completed':
            completed_count += 1
        elif file_info['status'] == 'failed':
            failed_count += 1

    if total_size > 0:
        progress = (downloaded_size / total_size) * 100
    else:
        progress = 0

    default_logger.info(f"总进度: {progress:.1f}%")
    default_logger.info(f"已完成: {completed_count} 个文件")
    default_logger.info(f"失败: {failed_count} 个文件")
    default_logger.info(f"已下载: {downloaded_size / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB")