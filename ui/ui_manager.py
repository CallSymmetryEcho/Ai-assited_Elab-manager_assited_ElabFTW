#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户界面管理模块

负责初始化和管理用户界面组件。
"""

import sys
import logging
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import QApplication

from .main_window import MainWindow
from camera.camera_manager import CameraManager
from llm.llm_manager import LLMManager
from elabftw.elab_manager import ElabManager
from qrcode_module.qrcode_generator import QRCodeGenerator

logger = logging.getLogger(__name__)


class UIManager:
    """用户界面管理器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化UI管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.app = None
        self.main_window = None
        
        # 初始化组件
        self.camera_manager = None
        self.llm_manager = None
        self.elab_manager = None
        self.qrcode_generator = None
    
    def initialize(self) -> bool:
        """初始化UI组件
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 创建QApplication实例
            self.app = QApplication(sys.argv)
            
            # 初始化摄像头管理器
            self.camera_manager = CameraManager(
                device_id=0,
                resolution=tuple(self.config["camera"]["resolution"])
            )
            
            # 初始化LLM管理器
            self.llm_manager = LLMManager(
                provider=self.config["llm"]["provider"],
                config=self.config["llm"]
            )
            
            # 初始化elabFTW管理器
            self.elab_manager = ElabManager(
                api_url=self.config["elabftw"]["api_url"],
                api_key=self.config["elabftw"]["api_key"],
                verify_ssl=self.config["elabftw"]["verify_ssl"]
            )
            
            # 初始化二维码生成器
            self.qrcode_generator = QRCodeGenerator(
                output_dir=self.config["storage"]["qrcode_dir"],
                box_size=self.config["qrcode"]["box_size"],
                border=self.config["qrcode"]["border"]
            )
            
            # 创建主窗口
            self.main_window = MainWindow(
                self.camera_manager,
                self.llm_manager,
                self.elab_manager,
                self.qrcode_generator,
                self.config
            )
            
            return True
            
        except Exception as e:
            logger.error(f"初始化UI组件失败: {e}")
            return False
    
    def run(self) -> int:
        """运行UI应用程序
        
        Returns:
            int: 应用程序退出代码
        """
        if not self.app or not self.main_window:
            logger.error("UI组件未初始化")
            return 1
        
        # 显示主窗口
        self.main_window.show()
        
        # 运行应用程序事件循环
        return self.app.exec_()
    
    def shutdown(self) -> None:
        """关闭UI组件"""
        # 关闭摄像头
        if self.camera_manager:
            self.camera_manager.release()
        
        # 关闭应用程序
        if self.app:
            self.app.quit()