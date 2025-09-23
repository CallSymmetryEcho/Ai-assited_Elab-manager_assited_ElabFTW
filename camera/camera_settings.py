#!/usr/bin/env python3

"""
Bridge script to handle camera settings operations for the web frontend.
This script is called by the web server to get and update camera settings.
"""

import argparse
import json
import sys
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('camera_settings')

# Add parent directory to path to import local modules
sys.path.append(str(Path(__file__).parent.parent))

# Import after path setup to avoid import errors
try:
    from camera.camera_manager import CameraManager
    from config.config_manager import ConfigManager
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def get_camera_manager():
    """
    Initialize and return a CameraManager instance with current configuration.
    
    Returns:
        CameraManager: Initialized CameraManager instance
    """
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize CameraManager
        camera_manager = CameraManager(config)
        return camera_manager
    except Exception as e:
        logger.error(f"Error initializing CameraManager: {e}")
        raise

def get_camera_settings():
    """
    Get camera settings from configuration.
    
    Returns:
        dict: Camera settings
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Extract camera settings
        camera_settings = {
            "device_id": config.get("camera", {}).get("device_id", 0),
            "resolution": {
                "width": config.get("camera", {}).get("resolution", {}).get("width", 640),
                "height": config.get("camera", {}).get("resolution", {}).get("height", 480)
            },
            "fps": config.get("camera", {}).get("fps", 30),
            "auto_focus": config.get("camera", {}).get("auto_focus", True),
            "image_format": config.get("camera", {}).get("image_format", "jpg"),
            "image_quality": config.get("camera", {}).get("image_quality", 95),
            "save_directory": config.get("camera", {}).get("save_directory", "images")
        }
        
        return camera_settings
    except Exception as e:
        logger.error(f"Error getting camera settings: {e}")
        return {"error": str(e)}

def update_camera_settings(settings):
    """
    Update camera settings in configuration.
    
    Args:
        settings (dict): New camera settings
        
    Returns:
        dict: Updated settings
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Update camera settings
        if "camera" not in config:
            config["camera"] = {}
            
        config["camera"]["device_id"] = settings.get("device_id", 0)
        
        if "resolution" not in config["camera"]:
            config["camera"]["resolution"] = {}
            
        if "resolution" in settings:
            config["camera"]["resolution"]["width"] = settings["resolution"].get("width", 640)
            config["camera"]["resolution"]["height"] = settings["resolution"].get("height", 480)
            
        config["camera"]["fps"] = settings.get("fps", 30)
        config["camera"]["auto_focus"] = settings.get("auto_focus", True)
        config["camera"]["image_format"] = settings.get("image_format", "jpg")
        config["camera"]["image_quality"] = settings.get("image_quality", 95)
        config["camera"]["save_directory"] = settings.get("save_directory", "images")
        
        # Save updated configuration
        config_manager.save_config(config)
        
        return get_camera_settings()
    except Exception as e:
        logger.error(f"Error updating camera settings: {e}")
        return {"error": str(e)}

def get_camera_status():
    """
    Get the current status of the camera.
    
    Returns:
        dict: Camera status
    """
    try:
        camera_manager = get_camera_manager()
        status = camera_manager.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        return {"error": str(e)}

def capture_image(filename=None, save_directory=None):
    """
    Capture an image from the camera.
    
    Args:
        filename (str, optional): Filename to save the image
        save_directory (str, optional): Directory to save the image
        
    Returns:
        dict: Captured image information
    """
    try:
        camera_manager = get_camera_manager()
        
        # Capture image
        image_path = camera_manager.capture_image(filename, save_directory)
        
        return {
            "success": True,
            "path": image_path,
            "filename": os.path.basename(image_path)
        }
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        return {"success": False, "error": str(e)}

def list_available_cameras():
    """
    List all available camera devices.
    
    Returns:
        dict: List of available cameras
    """
    try:
        camera_manager = get_camera_manager()
        cameras = camera_manager.list_cameras()
        return {"success": True, "cameras": cameras}
    except Exception as e:
        logger.error(f"Error listing cameras: {e}")
        return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='Camera Settings Bridge Script')
    parser.add_argument('--action', required=True, 
                        choices=['get_settings', 'update_settings', 'get_status', 'capture', 'list_cameras'],
                        help='Action to perform')
    parser.add_argument('--settings', help='JSON string with camera settings')
    parser.add_argument('--filename', help='Filename for captured image')
    parser.add_argument('--save-directory', help='Directory to save captured image')
    parser.add_argument('--output', help='Path to save the results (JSON)')
    
    args = parser.parse_args()
    
    # Parse settings if provided
    settings = None
    if args.settings:
        try:
            settings = json.loads(args.settings)
        except json.JSONDecodeError:
            logger.error("Invalid JSON settings format")
            sys.exit(1)
    
    # Perform the requested action
    result = None
    
    if args.action == 'get_settings':
        result = get_camera_settings()
    elif args.action == 'update_settings':
        if not settings:
            logger.error("Settings data is required for update_settings action")
            sys.exit(1)
        result = update_camera_settings(settings)
    elif args.action == 'get_status':
        result = get_camera_status()
    elif args.action == 'capture':
        result = capture_image(args.filename, args.save_directory)
    elif args.action == 'list_cameras':
        result = list_available_cameras()
    
    # Output the result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()