#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Camera Status Bridge Script

This script provides camera status information for the web API.
It returns JSON-formatted status data about the camera system.
"""

import json
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置项目路径
from config import ProjectPaths
paths = ProjectPaths()

from camera.camera_manager import CameraManager
from config import ConfigManager

def get_camera_status():
    """Get camera status information"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize camera manager
        camera_manager = CameraManager(
            device_id=config.get("camera", {}).get("device_id", 0),
            resolution=tuple(config.get("camera", {}).get("resolution", [1280, 720]))
        )
        
        # Check if camera is available
        is_available = camera_manager.is_camera_available()
        
        status = {
            "available": is_available,
            "device_id": config.get("camera", {}).get("device_id", 0),
            "resolution": config.get("camera", {}).get("resolution", [1280, 720]),
            "auto_focus": config.get("camera", {}).get("auto_focus", True),
            "capture_delay": config.get("camera", {}).get("capture_delay", 2)
        }
        
        if is_available:
            status["status"] = "ready"
            status["message"] = "Camera is available and ready"
        else:
            status["status"] = "error"
            status["message"] = "Camera is not available"
            
        return status
        
    except Exception as e:
        return {
            "available": False,
            "status": "error",
            "message": f"Error checking camera status: {str(e)}"
        }

def main():
    """Main function"""
    try:
        status = get_camera_status()
        print(json.dumps(status, indent=2))
        return 0
    except Exception as e:
        error_status = {
            "available": False,
            "status": "error",
            "message": f"Script error: {str(e)}"
        }
        print(json.dumps(error_status, indent=2))
        return 1

if __name__ == "__main__":
    sys.exit(main())