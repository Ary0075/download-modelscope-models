#!/usr/bin/env python3

import sys
import argparse
from src.downloader import ModelDownloader
from src.status_manager import get_download_status
from src.logger import default_logger

def download_model(args):
    """下载模型文件"""
    downloader = ModelDownloader(args.model_id, args.save_dir)
    downloader.download_all()

def show_status(args):
    """显示下载状态"""
    status = get_download_status(args.model_id)
    if not status:
        default_logger.info(f"未找到模型 {args.model_id} 的下载记录")
        return
    
    default_logger.info(f"模型 {args.model_id} 的下载状态:")
    for file_info in status['files']:
        default_logger.info(f"- {file_info['filename']}: {file_info['status']}")

def main():
    parser = argparse.ArgumentParser(description='ModelScope模型下载工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载模型')
    download_parser.add_argument('model_id', help='ModelScope模型ID')
    download_parser.add_argument('save_dir', help='保存目录')

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