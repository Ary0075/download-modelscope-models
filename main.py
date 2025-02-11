#!/usr/bin/env python3

import sys
import argparse
from src.downloader import ModelDownloader
from src.status_manager import show_download_status
from src.logger import default_logger
from src.config import default_config

def download_model(args):
    """下载模型文件"""
    downloader = ModelDownloader(
        model_id=args.model_id,
        local_dir=args.save_dir,
        max_workers=args.max_workers
    )
    if args.chunk_size:
        downloader.config.chunk_size = args.chunk_size
    downloader.download_all(background=args.background)

def show_status(args):
    """显示下载状态"""
    status = show_download_status(args.model_id)

def main():
    parser = argparse.ArgumentParser(description='ModelScope模型下载工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载模型')
    download_parser.add_argument('model_id', help='ModelScope模型ID')
    download_parser.add_argument('save_dir', help='保存目录')
    download_parser.add_argument('--max-workers', type=int, default=4, help='最大并发下载线程数')
    download_parser.add_argument('--chunk-size', type=int, help='下载块大小（字节）')
    download_parser.add_argument('--background', action='store_true', help='后台下载模式')

    # 状态命令
    status_parser = subparsers.add_parser('status', help='查看下载状态')
    status_parser.add_argument('model_id', help='ModelScope模型ID')

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