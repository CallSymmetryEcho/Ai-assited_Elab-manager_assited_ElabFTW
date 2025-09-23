#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-line tool for exporting elabFTW asset QR codes
"""

import os
import sys
import argparse
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from elabftw.elab_manager import ElabManager
from config import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        
        # Export QR code
        success, result = elab_manager.export_qrcode(
            item_id=args.item_id,
            output_dir=args.output_dir,
            filename=args.filename
        )
        
        if success:
            logger.info(f"QR code successfully exported: {result}")
            return 0
        else:
            logger.error(f"Failed to export QR code: {result}")
            return 1
            
    except Exception as e:
        logger.error(f"Error occurred while exporting QR code: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())