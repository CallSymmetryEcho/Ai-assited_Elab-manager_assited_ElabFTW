#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Camera Settings Bridge Script

This script provides camera settings information for the web API.
It returns JSON-formatted camera configuration data.
"""

import json
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use centralized configuration management
from config import ConfigManager, ProjectPaths

# Setup project paths
paths = ProjectPaths()

def get_camera_settings():
    """Get camera settings from configuration"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Extract camera settings
        camera_config = config.get("camera", {})
        
        settings = {
            "device_id": camera_config.get("device_id", 0),
            "resolution": camera_config.get("resolution", [1280, 720]),
            "auto_focus": camera_config.get("auto_focus", True),
            "capture_delay": camera_config.get("capture_delay", 2),
            "brightness": camera_config.get("brightness", 0),
            "contrast": camera_config.get("contrast", 0),
            "saturation": camera_config.get("saturation", 0),
            "exposure": camera_config.get("exposure", 0)
        }
        
        return {
            "success": True,
            "settings": settings
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting camera settings: {str(e)}"
        }

def main():
    """Main function"""
    try:
        result = get_camera_settings()
        print(json.dumps(result, indent=2))
        return 0 if result["success"] else 1
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"Script error: {str(e)}"
        }
        print(json.dumps(error_result, indent=2))
        return 1

if __name__ == "__main__":
    sys.exit(main())