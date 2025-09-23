#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导出elabFTW资产QR码的简单命令行工具
"""

import os
import sys
import argparse
import logging
import qrcode
from PIL import Image

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from elabftw.elab_manager import ElabManager
from config import ConfigManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_qrcode(data, output_path):
    """
    Generate QR code and save to specified path
    
    Args:
        data: QR code data
        output_path: Output file path
        
    Returns:
        bool: Whether successful
    """
    try:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image
        img.save(output_path)
        logger.info(f"QR code saved to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Export elabFTW asset QR code')
    parser.add_argument('item_id', type=int, help='elabFTW asset ID')
    parser.add_argument('-o', '--output-dir', help='Output directory')
    parser.add_argument('-f', '--filename', help='Output filename')
    args = parser.parse_args()
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        if not config:
            logger.error("Unable to load configuration")
            return 1
        
        # Create ElabManager instance
        elab_manager = ElabManager(
            api_url=config.get('elabftw', {}).get('api_url'),
            api_key=config.get('elabftw', {}).get('api_key'),
            verify_ssl=config.get('elabftw', {}).get('verify_ssl', True)
        )
        
        # Get asset information
        item_info = elab_manager.get_item(args.item_id)
        if not item_info:
            logger.error(f"Unable to get asset information (ID: {args.item_id})")
            return 1
        
        # Set output directory
        output_dir = args.output_dir
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qrcodes')
        os.makedirs(output_dir, exist_ok=True)
        
        # Set filename
        if args.filename:
            filename = args.filename
            if not filename.lower().endswith('.png'):
                filename += '.png'
        else:
            asset_name = item_info.get("title", f"asset_{args.item_id}")
            # Remove characters not suitable for filenames
            asset_name = "".join(c for c in asset_name if c.isalnum() or c in "_ -")
            filename = f"{asset_name}_{args.item_id}.png"
        
        # Complete file path
        file_path = os.path.join(output_dir, filename)
        
        # Build QR code data
        qr_data = f"https://elab.local/database.php?mode=view&id={args.item_id}"
        
        # Generate QR code
        if generate_qrcode(qr_data, file_path):
            logger.info(f"Asset QR code successfully exported: {file_path}")
            return 0
        else:
            logger.error("Failed to export QR code")
            return 1
            
    except Exception as e:
        logger.error(f"Error exporting QR code: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())