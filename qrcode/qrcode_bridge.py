#!/usr/bin/env python3

"""
Bridge script to handle QR code operations for the web frontend.
This script is called by the web server to generate, retrieve, and manage QR codes.
"""

import argparse
import json
import sys
import os
from pathlib import Path
import logging
import base64

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('qrcode_bridge')

# Add parent directory to path to import local modules
sys.path.append(str(Path(__file__).parent.parent))

# Import after path setup to avoid import errors
try:
    from qrcode.qrcode_generator import QRCodeGenerator
    from config.config_manager import ConfigManager
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def get_qrcode_generator():
    """
    Initialize and return a QRCodeGenerator instance with current configuration.
    
    Returns:
        QRCodeGenerator: Initialized QRCodeGenerator instance
    """
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize QRCodeGenerator
        qrcode_generator = QRCodeGenerator(config)
        return qrcode_generator
    except Exception as e:
        logger.error(f"Error initializing QRCodeGenerator: {e}")
        raise

def generate_qrcode(data, filename=None, include_image=False):
    """
    Generate a QR code with the given data.
    
    Args:
        data (str): Data to encode in the QR code
        filename (str, optional): Filename to save the QR code
        include_image (bool, optional): Whether to include the image in the response
        
    Returns:
        dict: Generated QR code information
    """
    try:
        qrcode_generator = get_qrcode_generator()
        
        # Generate QR code
        qr_path = qrcode_generator.generate_qrcode(data, filename)
        
        result = {
            "success": True,
            "path": qr_path,
            "data": data,
            "filename": os.path.basename(qr_path)
        }
        
        # Include base64 encoded image if requested
        if include_image and os.path.exists(qr_path):
            with open(qr_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                result["image"] = encoded_string
        
        return result
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return {"success": False, "error": str(e)}

def get_qrcode(filename, include_image=False):
    """
    Get information about a specific QR code.
    
    Args:
        filename (str): Filename of the QR code
        include_image (bool, optional): Whether to include the image in the response
        
    Returns:
        dict: QR code information
    """
    try:
        qrcode_generator = get_qrcode_generator()
        qr_dir = qrcode_generator.get_qrcode_dir()
        qr_path = os.path.join(qr_dir, filename)
        
        if not os.path.exists(qr_path):
            return {"success": False, "error": f"QR code {filename} not found"}
        
        # Read QR code data
        data = qrcode_generator.read_qrcode(qr_path)
        
        result = {
            "success": True,
            "path": qr_path,
            "data": data,
            "filename": filename
        }
        
        # Include base64 encoded image if requested
        if include_image:
            with open(qr_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                result["image"] = encoded_string
        
        return result
    except Exception as e:
        logger.error(f"Error getting QR code {filename}: {e}")
        return {"success": False, "error": str(e)}

def list_qrcodes():
    """
    List all generated QR codes.
    
    Returns:
        dict: List of QR codes
    """
    try:
        qrcode_generator = get_qrcode_generator()
        qr_dir = qrcode_generator.get_qrcode_dir()
        
        # Ensure QR code directory exists
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir, exist_ok=True)
            return {"success": True, "qrcodes": []}
        
        # List QR code files
        qrcodes = []
        for filename in os.listdir(qr_dir):
            if filename.endswith(".png"):
                qr_path = os.path.join(qr_dir, filename)
                try:
                    data = qrcode_generator.read_qrcode(qr_path)
                    qrcodes.append({
                        "filename": filename,
                        "path": qr_path,
                        "data": data,
                        "created": os.path.getctime(qr_path)
                    })
                except Exception as e:
                    logger.warning(f"Error reading QR code {filename}: {e}")
        
        return {"success": True, "qrcodes": qrcodes}
    except Exception as e:
        logger.error(f"Error listing QR codes: {e}")
        return {"success": False, "error": str(e)}

def delete_qrcode(filename):
    """
    Delete a QR code.
    
    Args:
        filename (str): Filename of the QR code to delete
        
    Returns:
        dict: Result of the deletion operation
    """
    try:
        qrcode_generator = get_qrcode_generator()
        qr_dir = qrcode_generator.get_qrcode_dir()
        qr_path = os.path.join(qr_dir, filename)
        
        if not os.path.exists(qr_path):
            return {"success": False, "error": f"QR code {filename} not found"}
        
        # Delete the QR code file
        os.remove(qr_path)
        
        return {"success": True, "message": f"QR code {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting QR code {filename}: {e}")
        return {"success": False, "error": str(e)}

def get_settings():
    """
    Get QR code settings from configuration.
    
    Returns:
        dict: QR code settings
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Extract QR code settings
        qrcode_settings = {
            "directory": config.get("qrcode", {}).get("directory", "qrcodes"),
            "size": config.get("qrcode", {}).get("size", 10),
            "border": config.get("qrcode", {}).get("border", 4),
            "format": config.get("qrcode", {}).get("format", "png")
        }
        
        return qrcode_settings
    except Exception as e:
        logger.error(f"Error getting QR code settings: {e}")
        return {"error": str(e)}

def update_settings(settings):
    """
    Update QR code settings in configuration.
    
    Args:
        settings (dict): New QR code settings
        
    Returns:
        dict: Updated settings
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Update QR code settings
        if "qrcode" not in config:
            config["qrcode"] = {}
            
        config["qrcode"]["directory"] = settings.get("directory", "qrcodes")
        config["qrcode"]["size"] = settings.get("size", 10)
        config["qrcode"]["border"] = settings.get("border", 4)
        config["qrcode"]["format"] = settings.get("format", "png")
        
        # Save updated configuration
        config_manager.save_config(config)
        
        return get_settings()
    except Exception as e:
        logger.error(f"Error updating QR code settings: {e}")
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='QR Code Bridge Script')
    parser.add_argument('--action', required=True, 
                        choices=['generate', 'get', 'list', 'delete', 'get_settings', 'update_settings'],
                        help='Action to perform')
    parser.add_argument('--data', help='Data to encode in the QR code')
    parser.add_argument('--filename', help='Filename for the QR code')
    parser.add_argument('--include-image', action='store_true', help='Include base64 encoded image in response')
    parser.add_argument('--settings', help='JSON string with QR code settings')
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
    
    if args.action == 'generate':
        if not args.data:
            logger.error("Data is required for generate action")
            sys.exit(1)
        result = generate_qrcode(args.data, args.filename, args.include_image)
    elif args.action == 'get':
        if not args.filename:
            logger.error("Filename is required for get action")
            sys.exit(1)
        result = get_qrcode(args.filename, args.include_image)
    elif args.action == 'list':
        result = list_qrcodes()
    elif args.action == 'delete':
        if not args.filename:
            logger.error("Filename is required for delete action")
            sys.exit(1)
        result = delete_qrcode(args.filename)
    elif args.action == 'get_settings':
        result = get_settings()
    elif args.action == 'update_settings':
        if not settings:
            logger.error("Settings data is required for update_settings action")
            sys.exit(1)
        result = update_settings(settings)
    
    # Output the result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()