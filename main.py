#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Laboratory Asset Management System

This system uses a camera to capture item images, analyzes them with LLM,
automatically enters asset information into the elabFTW system, and generates QR code labels.
"""

import os
import sys

# Remove current directory from sys.path to avoid import conflicts with local packages
# This ensures that third-party libraries are imported from site-packages
if '' in sys.path:
    sys.path.remove('')

import argparse
import logging
from pathlib import Path

# 导入PyQt5
from PyQt5.QtWidgets import QApplication

# 导入自定义模块
from camera.camera_manager import CameraManager
from llm.llm_manager import LLMManager
from elabftw.elab_manager import ElabManager
from qrcode_module.qrcode_generator import QRCodeGenerator
from ui.main_window import MainWindow
from config import ConfigManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("lab_asset_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Laboratory Asset Management System')
    parser.add_argument('--config', type=str, default='config.json', help='Configuration file path')
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()


def main():
    """Main program entry"""
    # Parse command line arguments
    args = parse_args()
    
    # If debug mode is enabled, set log level to DEBUG
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    config = config_manager.load_config()
    
    # Initialize modules
    try:
        # Initialize camera manager
        camera_manager = CameraManager(device_id=args.camera)
        
        # Initialize LLM manager
        llm_manager = LLMManager(config['llm'])
        
        # Initialize elabFTW manager
        elab_manager = ElabManager(
            api_url=config['elabftw']['api_url'],
            api_key=config['elabftw']['api_key'],
            verify_ssl=config['elabftw']['verify_ssl']
        )
        
        # Initialize QR code generator
        qrcode_generator = QRCodeGenerator()
        
        # 初始化QApplication
        qt_app = QApplication(sys.argv)
        
        # 初始化并启动UI
        main_window = MainWindow(
            camera_manager=camera_manager,
            llm_manager=llm_manager,
            elab_manager=elab_manager,
            qrcode_generator=qrcode_generator,
            config=config
        )
        main_window.show()
        
        # 运行应用程序事件循环
        return qt_app.exec_()
        
    except Exception as e:
        logger.error(f"Program initialization failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())