#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Camera Capture Bridge Script

This script captures an image from the camera and saves it to the specified path.
Used by the web API to capture images.
"""

import cv2
import json
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置项目路径
from config import ProjectPaths
paths = ProjectPaths()

import argparse
import logging
from datetime import datetime

from camera.camera_manager import CameraManager
from config import ConfigManager

def capture_image(output_path=None):
    """Capture an image from the camera"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize camera manager
        camera_manager = CameraManager(
            device_id=config.get("camera", {}).get("device_id", 0),
            resolution=tuple(config.get("camera", {}).get("resolution", [1280, 720]))
        )
        
        # Generate output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            images_dir = config.get("storage", {}).get("image_dir", "images")
            if not os.path.exists(images_dir):
                os.makedirs(images_dir, exist_ok=True)
            output_path = os.path.join(images_dir, f"asset_{timestamp}.jpg")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Initialize camera
        if not camera_manager.initialize():
            raise Exception("Failed to initialize camera")
        
        # Capture image
        success = camera_manager.capture_image(output_path)
        
        # Release camera
        camera_manager.release()
        
        if success and os.path.exists(output_path):
            result = {
                "success": True,
                "image_path": output_path,
                "message": "Image captured successfully"
            }
        else:
            result = {
                "success": False,
                "message": "Failed to capture image"
            }
            
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error capturing image: {str(e)}"
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Capture image from camera')
    parser.add_argument('--output', type=str, help='Output image path')
    
    args = parser.parse_args()
    
    try:
        result = capture_image(args.output)
        
        if result["success"]:
            print(f"Image captured: {result['image_path']}")
            return 0
        else:
            print(f"Error: {result['message']}", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"Script error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())