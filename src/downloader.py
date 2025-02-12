#!/usr/bin/env python3

import os
import sys
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests
from tqdm import tqdm
from modelscope import snapshot_download
from modelscope.hub.api import HubApi
from .config import default_config
from .logger import default_logger

@dataclass
class ModelFile:
    """表示要下载的模型文件
    
    Attributes:
        filename: 文件名
        file_size: 文件大小（字节）
        file_hash: 文件的SHA256哈希值
        download_url: 文件下载URL
        downloaded_size: 已下载的字节数
        status: 下载状态（pending/downloading/completed/failed/stopped）
    """
    filename: str
    file_size: int
    file_hash: str
    download_url: str
    downloaded_size: int = 0
    status: str = 'pending'

class ModelDownloader:
    """ModelScope模型下载器
    
    负责从ModelScope下载模型文件，支持断点续传和并发下载。
    
    Attributes:
        model_id: ModelScope模型ID
        local_dir: 本地保存目录
        max_workers: 最大并发下载线程数
        chunk_size: 下载块大小（字节）
    """
    
    def __init__(self, model_id: str, local_dir: str, max_workers: int = 4):
        self.model_id = model_id
        self.local_dir = os.path.abspath(local_dir)
        self.max_workers = max_workers
        self.hub_api = HubApi()
        self.config = default_config
        self.logger = default_logger
        self.current_model_files = []
        self._executor = None

    def get_model_files(self) -> List[ModelFile]:
        """获取模型文件列表
        
        Returns:
            List[ModelFile]: 模型文件列表
        
        Raises:
            SystemExit: 当获取文件列表失败时退出程序
        """
        try:
            model_files = []
            files_info = self.hub_api.get_model_files(self.model_id)
            
            if not files_info:
                self.logger.warning(f"模型 {self.model_id} 没有返回任何文件信息")
                return model_files
            
            for file_info in files_info:
                if not isinstance(file_info, dict):
                    self.logger.warning(f"跳过无效的文件信息格式: {file_info}")
                    continue

                filename = file_info.get('Name')
                if not filename:
                    self.logger.warning(f"文件信息中没有找到文件名: {file_info}")
                    continue

                if not file_info.get('Downloadable', True):
                    self.logger.info(f"跳过不可下载的文件: {filename}")
                    continue

                download_url = f"https://modelscope.cn/models/{self.model_id}/resolve/master/{filename}"
                model_files.append(ModelFile(
                    filename=filename,
                    file_size=file_info.get('Size', 0),
                    file_hash=file_info.get('Sha256', ''),
                    download_url=download_url
                ))
            
            if not model_files:
                self.logger.warning("没有找到任何有效的文件信息")
            else:
                self.logger.info(f"成功获取到 {len(model_files)} 个文件的信息")
                
            return model_files

        except Exception as e:
            self.logger.exception(f"获取模型文件列表失败: {str(e)}")
            sys.exit(1)

    def verify_file(self, file_path: str, expected_hash: str) -> bool:
        """验证文件完整性
        
        Args:
            file_path: 文件路径
            expected_hash: 预期的SHA256哈希值
            
        Returns:
            bool: 文件验证是否通过
        """
        if not expected_hash:
            return True

        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest() == expected_hash

    def download_file(self, model_file: ModelFile) -> bool:
        """下载单个文件
        
        Args:
            model_file: 要下载的模型文件信息
            
        Returns:
            bool: 下载是否成功
        """
        from .status_manager import save_download_status
        import time
        
        local_path = os.path.join(self.local_dir, model_file.filename)
        temp_path = f"{local_path}.tmp"
        model_file.status = 'downloading'

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        initial_pos = 0
        if os.path.exists(temp_path):
            initial_pos = os.path.getsize(temp_path)

        headers = {}
        if initial_pos > 0:
            headers['Range'] = f'bytes={initial_pos}-'

        try:
            response = requests.get(model_file.download_url, headers=headers, stream=True)
            total_size = int(response.headers.get('content-length', 0)) + initial_pos
            mode = 'ab' if initial_pos > 0 else 'wb'
            last_save_time = time.time()

            with open(temp_path, mode) as f, tqdm(
                desc=model_file.filename,
                initial=initial_pos,
                total=total_size,
                unit='iB',
                unit_scale=True
            ) as pbar:
                for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
                        model_file.downloaded_size = os.path.getsize(temp_path)  # 获取实际文件大小
                        current_time = time.time()
                        if current_time - last_save_time >= 10:  # 每10秒保存一次
                            save_download_status(self.model_id, self.current_model_files)
                            last_save_time = current_time

            if self.verify_file(temp_path, model_file.file_hash):
                os.replace(temp_path, local_path)
                model_file.status = 'completed'
                return True
            else:
                os.remove(temp_path)
                self.logger.error(f"文件验证失败: {model_file.filename}")
                model_file.status = 'failed'
                return False

        except Exception as e:
            self.logger.error(f"下载文件失败 {model_file.filename}: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            model_file.status = 'failed'
            return False

    def download_all(self):
        """使用线程池下载所有文件"""
        from .status_manager import load_download_status, save_download_status
        
        model_files = self.get_model_files()
        if not model_files:
            self.logger.warning("没有找到可下载的文件")
            return
            
        self.current_model_files = model_files
        previous_status = load_download_status(self.model_id)
        if previous_status:
            for file_info in previous_status['files']:
                for model_file in model_files:
                    if model_file.filename == file_info['filename']:
                        model_file.downloaded_size = file_info['downloaded_size']
                        model_file.status = file_info['status']
                        break

        # 在开始下载前保存所有文件的初始状态
        save_download_status(self.model_id, self.current_model_files)
        self.logger.info(f"开始下载模型 {self.model_id} 的文件到 {self.local_dir}")
        self._download_files()
            
    def _download_files(self):
        """实际执行下载的内部方法"""
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        try:
            results = list(self._executor.map(self.download_file, self.current_model_files))
            success_count = sum(1 for r in results if r)

            self.logger.info(f"下载完成: {success_count}/{len(self.current_model_files)} 个文件成功")
        finally:
            self._executor.shutdown(wait=True)
            self._executor = None