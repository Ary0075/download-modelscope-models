#!/usr/bin/env python3

import json
import os
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
    import time
    import uuid
    
    status_file = default_config.get_status_file_path(model_id)
    # 使用时间戳和随机字符串生成唯一的临时文件名
    temp_suffix = f".{int(time.time())}_{uuid.uuid4().hex[:8]}.tmp"
    temp_file = status_file.with_suffix(temp_suffix)
    
    # 确保状态文件的父目录存在
    status_file.parent.mkdir(parents=True, exist_ok=True)
    
    status_data = {
        'model_id': model_id,
        'files': [{
            'filename': f.filename,
            'file_size': f.file_size,
            'downloaded_size': f.downloaded_size,
            'status': f.status
        } for f in model_files]
    }
    
    # 先写入临时文件，然后原子性地替换目标文件
    try:
        # 确保临时文件所在目录存在
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 由于使用了唯一的临时文件名，不需要检查和删除已存在的临时文件
        
        # 写入临时文件
        try:
            # 检查目录权限
            if not os.access(temp_file.parent, os.W_OK):
                default_logger.error(f"目录 {temp_file.parent} 没有写入权限")
                return
                
            with open(temp_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # 确保数据写入磁盘
            
            # 验证文件是否成功写入
            if not temp_file.exists() or temp_file.stat().st_size == 0:
                default_logger.error("临时文件写入失败或为空")
                return
        except Exception as e:
            default_logger.error(f"写入临时文件失败: {str(e)}")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    default_logger.error(f"清理失败的临时文件失败: {str(e)}")
            return
        
        # 原子性地替换目标文件
        try:
            os.replace(temp_file, status_file)
            
            # 清理其他可能存在的临时文件（只清理1小时前的文件）
            current_time = time.time()
            for old_temp in status_file.parent.glob(f"{status_file.stem}.*tmp"):
                try:
                    # 从文件名中提取时间戳
                    timestamp = float(old_temp.suffix.split('.')[1])
                    if current_time - timestamp > 3600:  # 1小时
                        old_temp.unlink()
                except (ValueError, IndexError, OSError):
                    continue
        except Exception as e:
            default_logger.error(f"替换状态文件失败: {str(e)}")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    default_logger.error(f"清理临时文件失败: {str(e)}")
            return
            
    except Exception as e:
        default_logger.error(f"保存下载状态失败: {str(e)}")
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception as e:
                default_logger.error(f"清理临时文件失败: {str(e)}")

def validate_status_data(data: Dict) -> bool:
    """验证状态数据格式
    
    Args:
        data: 状态数据
        
    Returns:
        bool: 数据格式是否有效
    """
    try:
        if not isinstance(data, dict):
            return False
        if 'model_id' not in data or 'files' not in data:
            return False
        if not isinstance(data['files'], list):
            return False
        for file_info in data['files']:
            if not isinstance(file_info, dict):
                return False
            required_fields = {'filename', 'file_size', 'downloaded_size', 'status'}
            if not all(field in file_info for field in required_fields):
                return False
        return True
    except Exception:
        return False

def load_download_status(model_id: str) -> Optional[Dict]:
    """从临时文件加载下载状态
    
    Args:
        model_id: 模型ID
        
    Returns:
        Optional[Dict]: 下载状态数据，如果文件不存在或无效则返回None
    """
    status_file = default_config.get_status_file_path(model_id)
    if not status_file.exists():
        return None

    try:
        with open(status_file) as f:
            data = json.load(f)
            if validate_status_data(data):
                return data
            else:
                default_logger.error("状态文件格式无效，将重新开始下载")
                try:
                    status_file.unlink()
                except Exception as e:
                    default_logger.error(f"删除无效状态文件失败: {str(e)}")
                return None
    except json.JSONDecodeError as e:
        default_logger.error(f"状态文件已损坏: {str(e)}，将重新开始下载")
        try:
            status_file.unlink()
        except Exception as e:
            default_logger.error(f"删除损坏状态文件失败: {str(e)}")
        return None
    except Exception as e:
        default_logger.error(f"读取状态文件失败: {str(e)}")
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
    failed_files = []

    for file_info in status_data['files']:
        total_size += file_info['file_size']
        downloaded_size += file_info['downloaded_size']
        if file_info['status'] == 'completed':
            completed_count += 1
        elif file_info['status'] == 'failed':
            failed_count += 1
            failed_files.append(os.path.join(default_config.status_dir.parent, file_info['filename']))

    if total_size > 0:
        progress = (downloaded_size / total_size) * 100
    else:
        progress = 0

    default_logger.info(f"总进度: {progress:.1f}%")
    default_logger.info(f"已完成: {completed_count} 个文件")
    default_logger.info(f"失败: {failed_count} 个文件")
    if failed_files:
        default_logger.info("\n失败文件列表:")
        for file_path in failed_files:
            default_logger.info(f"- {file_path}")
    default_logger.info(f"已下载: {downloaded_size / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB")