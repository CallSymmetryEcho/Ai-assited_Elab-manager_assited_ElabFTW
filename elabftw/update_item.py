#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Update Item in elabFTW

This script updates an existing item in the elabFTW system and returns the result as JSON.
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

def update_item(item_id, item_data):
    """Update an existing item in elabFTW
    
    Args:
        item_id (int): ID of the item to update
        item_data (dict): Updated item data
        
    Returns:
        dict: Updated item details or error message
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
        
        # Update item
        success = elab_manager.update_item(item_id, item_data)
        
        if success:
            # Get the updated item
            item = elab_manager.get_item(item_id)
            return item
        else:
            return {"error": f"Failed to update item {item_id}"}
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        return {"error": str(e)}

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Update item in elabFTW')
    parser.add_argument('--id', type=int, required=True, help='Item ID')
    parser.add_argument('--data', type=str, required=True, help='Updated item data as JSON string')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        item_data = json.loads(args.data)
        result = update_item(args.id, item_data)
        print(json.dumps(result))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON data: {e}")
        print(json.dumps({"error": f"Invalid JSON data: {e}"}))