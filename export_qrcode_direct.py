#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-line tool for directly exporting asset URLs from elabFTW
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
    parser = argparse.ArgumentParser(description='Export elabFTW asset URL')
    parser.add_argument('item_id', type=int, help='elabFTW asset ID')
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
        
        # Build asset URL
        api_url = config.get('elabftw', {}).get('api_url', '')
        base_url = api_url.split('/api/')[0] if '/api/' in api_url else 'https://elab.local'
        asset_url = f"{base_url}/database.php?mode=view&id={args.item_id}"
        
        # Output asset URL
        print(f"\nAsset ID: {args.item_id}")
        print(f"Asset Title: {item_info.get('title', 'Unknown')}")
        print(f"Asset URL: {asset_url}")
        print("\nYou can use this URL to generate a QR code, or directly access this URL to view asset information.")
        print("\nTip: You can use online QR code generators or mobile apps to create QR codes.")
        
        return 0
            
    except Exception as e:
        logger.error(f"Error exporting asset URL: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())