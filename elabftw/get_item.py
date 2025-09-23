#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get Item from elabFTW

This script retrieves a specific item from the elabFTW system and returns it as JSON.
"""

import os
import sys
import json
import logging
import argparse

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elabftw.elab_manager import ElabManager
from config import ConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_item(item_id):
    """Get a specific item from elabFTW
    
    Args:
        item_id (int): ID of the item to retrieve
        
    Returns:
        dict: Item details
    """
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize elabFTW manager
        elab_manager = ElabManager(
            api_url=config.get('elabftw', {}).get('api_url', ''),
            api_key=config.get('elabftw', {}).get('api_key', ''),
            verify_ssl=config.get('elabftw', {}).get('verify_ssl', False)
        )
        
        # Get item
        item = elab_manager.get_item(item_id)
        return item
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        return {"error": str(e)}

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Get item from elabFTW')
    parser.add_argument('--id', type=int, required=True, help='Item ID')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    item = get_item(args.id)
    print(json.dumps(item))