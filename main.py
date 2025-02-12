#!/usr/bin/env python3

import os
import signal
import argparse
from src.downloader import ModelDownloader
from src.status_manager import show_download_status
from src.logger import default_logger
from src.config import default_config

def signal_handler(signum, frame):
    """处理Ctrl+C信号"""
    if signum == signal.SIGINT:
        os._exit(0)  # 使用os._exit()直接退出，避免线程清理

def download_model(args):
    """下载模型文件"""
    downloader = ModelDownloader(
        model_id=args.model_id,
        local_dir=args.save_dir,
        max_workers=args.max_workers
    )
    if args.chunk_size:
        downloader.config.chunk_size = args.chunk_size
    if args.no_verify:
        downloader.config.verify_hash = False
    if args.retry is not None:
        downloader.config.max_retry = args.retry
    downloader.download_all()

def show_status(args):
    """显示下载状态"""
    status = show_download_status(args.model_id)

def main():
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description='ModelScope模型下载工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载模型', description='从ModelScope下载模型文件到本地目录')
    download_parser.add_argument('model_id', help='ModelScope模型ID，例如："deepseek-ai/DeepSeek-R1"')
    download_parser.add_argument('save_dir', help='模型文件保存目录的本地路径')
    download_parser.add_argument('--max-workers', type=int, default=4, help='最大并发下载线程数（默认：4）')
    download_parser.add_argument('--chunk-size', type=int, help='下载块大小，单位为字节（默认：1MB）')
    download_parser.add_argument('--no-verify', action='store_true', help='跳过文件完整性验证')
    download_parser.add_argument('--retry', type=int, default=3, help='下载失败时的重试次数（默认：3）')

    # 状态命令
    status_parser = subparsers.add_parser('status', help='查看下载状态', description='查看指定模型的下载进度和状态信息')
    status_parser.add_argument('model_id', help='要查询状态的ModelScope模型ID')

    args = parser.parse_args()

    if args.command == 'download':
        download_model(args)
    elif args.command == 'status':
        show_status(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()