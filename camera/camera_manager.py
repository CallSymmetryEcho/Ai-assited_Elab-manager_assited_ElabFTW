#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
摄像头管理模块

负责初始化和控制USB摄像头，提供图像捕捉功能。
"""

import time
import logging
import numpy as np
from pathlib import Path

# Try to import cv2 with proper error handling
try:
    import cv2
except ImportError:
    cv2 = None
    logging.error("OpenCV (cv2) module not found or not properly installed.")
except AttributeError:
    # This handles the case where cv2 is imported but missing attributes
    logging.error("OpenCV (cv2) module is installed but may be missing required components.")

logger = logging.getLogger(__name__)


class CameraManager:
    """摄像头管理器类"""
    
    def __init__(self, device_id=0, resolution=(1280, 720)):
        """初始化摄像头管理器
        
        Args:
            device_id (int): 摄像头设备ID
            resolution (tuple): 分辨率 (宽, 高)
        """
        self.device_id = device_id
        self.resolution = resolution
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.last_error = None
    
    def initialize(self):
        """初始化摄像头
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # # Check if cv2 is available
            # if cv2 is None:
            #     self.last_error = "OpenCV (cv2) module not found or not properly installed."
            #     logger.error(self.last_error)
            #     return False
                
            # # Check if VideoCapture attribute exists
            # if not hasattr(cv2, 'VideoCapture'):
            #     self.last_error = "cv2 module does not have VideoCapture attribute."
            #     logger.error(self.last_error)
            #     return False
                
            # 打开摄像头
            self.camera = cv2.VideoCapture(self.device_id)
            
            # 检查摄像头是否成功打开
            if not self.camera.isOpened():
                self.last_error = f"无法打开摄像头 (ID: {self.device_id})"
                logger.error(self.last_error)
                return False
            
            # 设置分辨率
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            # 设置自动对焦（如果支持）
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            
            # 读取一帧以确认设置生效
            ret, frame = self.camera.read()
            if not ret:
                self.last_error = "无法从摄像头读取图像"
                logger.error(self.last_error)
                self.release()
                return False
            
            self.is_running = True
            logger.info(f"摄像头初始化成功 (ID: {self.device_id}, 分辨率: {self.resolution})")
            return True
            
        except Exception as e:
            self.last_error = f"摄像头初始化失败: {e}"
            logger.error(self.last_error)
            return False
    
    def release(self):
        """释放摄像头资源"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            self.is_running = False
            logger.info("摄像头资源已释放")
            
    def start(self):
        """启动摄像头
        
        Returns:
            bool: 启动是否成功
        """
        if self.is_running:
            return True
            
        return self.initialize()
    
    def read_frame(self):
        """读取一帧图像
        
        Returns:
            numpy.ndarray or None: 图像数据，如果读取失败则返回None
        """
        if not self.is_running or self.camera is None:
            if not self.initialize():
                return None
        
        try:
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame
                return frame
            else:
                self.last_error = "读取图像帧失败"
                logger.error(self.last_error)
                return None
        except Exception as e:
            self.last_error = f"读取图像帧异常: {e}"
            logger.error(self.last_error)
            return None
    
    def capture_image(self, save_path=None, delay=2):
        """捕捉图像并可选保存
        
        Args:
            save_path (str, optional): 保存路径，如果为None则不保存
            delay (int): 延迟秒数，用于给用户准备时间
            
        Returns:
            tuple: (成功标志, 图像数据或错误信息)
        """
        if not self.is_running:
            if not self.initialize():
                return False, self.last_error
        
        try:
            # 延迟捕捉，给用户准备时间
            for i in range(delay, 0, -1):
                # 读取帧用于预览
                ret, frame = self.camera.read()
                if not ret:
                    self.last_error = "预览图像帧失败"
                    logger.error(self.last_error)
                    return False, self.last_error
                
                # 在图像上显示倒计时
                countdown_frame = frame.copy()
                cv2.putText(
                    countdown_frame, 
                    f"捕捉倒计时: {i}", 
                    (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0, 0, 255), 
                    2
                )
                
                # 更新当前帧用于UI显示
                self.current_frame = countdown_frame
                
                # 等待1秒
                time.sleep(1)
            
            # 捕捉最终图像
            ret, image = self.camera.read()
            if not ret:
                self.last_error = "捕捉图像失败"
                logger.error(self.last_error)
                return False, self.last_error
            
            # 保存图像（如果提供了保存路径）
            if save_path is not None:
                # 确保目录存在
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                
                # 保存图像
                cv2.imwrite(save_path, image)
                logger.info(f"图像已保存至: {save_path}")
            
            # 更新当前帧
            self.current_frame = image
            
            return True, image
            
        except Exception as e:
            self.last_error = f"捕捉图像异常: {e}"
            logger.error(self.last_error)
            return False, self.last_error
    
    def get_camera_properties(self):
        """获取摄像头属性
        
        Returns:
            dict: 摄像头属性字典
        """
        if not self.is_running or self.camera is None:
            return {}
        
        try:
            properties = {
                "width": int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": self.camera.get(cv2.CAP_PROP_FPS),
                "brightness": self.camera.get(cv2.CAP_PROP_BRIGHTNESS),
                "contrast": self.camera.get(cv2.CAP_PROP_CONTRAST),
                "saturation": self.camera.get(cv2.CAP_PROP_SATURATION),
                "hue": self.camera.get(cv2.CAP_PROP_HUE),
                "gain": self.camera.get(cv2.CAP_PROP_GAIN),
                "exposure": self.camera.get(cv2.CAP_PROP_EXPOSURE),
                "autofocus": self.camera.get(cv2.CAP_PROP_AUTOFOCUS)
            }
            return properties
        except Exception as e:
            logger.error(f"获取摄像头属性失败: {e}")
            return {}
    
    def set_camera_property(self, property_id, value):
        """设置摄像头属性
        
        Args:
            property_id: OpenCV属性ID（如cv2.CAP_PROP_*）
            value: 要设置的值
            
        Returns:
            bool: 设置是否成功
        """
        if not self.is_running or self.camera is None:
            return False
        
        try:
            return self.camera.set(property_id, value)
        except Exception as e:
            logger.error(f"设置摄像头属性失败: {e}")
            return False
    
    def is_camera_available(self):
        """检查摄像头是否可用
        
        Returns:
            bool: 摄像头是否可用
        """
        try:
            # Check if cv2 is available
            if cv2 is None:
                self.last_error = "OpenCV (cv2) module not found or not properly installed."
                logger.error(self.last_error)
                return False
                
            # Check if VideoCapture attribute exists
            if not hasattr(cv2, 'VideoCapture'):
                self.last_error = "cv2 module does not have VideoCapture attribute."
                logger.error(self.last_error)
                return False
            
            # Try to open camera temporarily to check availability
            test_camera = cv2.VideoCapture(self.device_id)
            if test_camera.isOpened():
                test_camera.release()
                return True
            else:
                self.last_error = f"Camera device {self.device_id} is not available"
                return False
                
        except Exception as e:
            self.last_error = f"Error checking camera availability: {e}"
            logger.error(self.last_error)
            return False
    
    def get_last_error(self):
        """获取最后一次错误信息
        
        Returns:
            str: 错误信息
        """
        return self.last_error
    
    def get_status(self):
        """获取相机状态信息
        
        Returns:
            dict: 相机状态信息
        """
        try:
            is_available = self.is_camera_available()
            
            status = {
                "available": is_available,
                "device_id": self.device_id,
                "resolution": list(self.resolution),
                "is_running": self.is_running,
                "current_frame_available": self.current_frame is not None
            }
            
            if is_available:
                status["status"] = "ready"
                status["message"] = "Camera is available and ready"
            else:
                status["status"] = "error"
                status["message"] = "Camera is not available"
                if self.last_error:
                    status["error"] = self.last_error
                    
            return status
            
        except Exception as e:
            error_msg = f"Error getting camera status: {e}"
            logger.error(error_msg)
            return {
                "available": False,
                "status": "error",
                "message": error_msg,
                "device_id": self.device_id,
                "resolution": list(self.resolution),
                "is_running": False,
                "current_frame_available": False
            }