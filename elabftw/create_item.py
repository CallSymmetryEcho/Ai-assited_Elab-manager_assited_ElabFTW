#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create Item in elabFTW

This script creates a new item in the elabFTW system and returns the result as JSON.
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

def create_item(item_data):
    """Create a new item in elabFTW
    
    Args:
        item_data (dict): Item data to create
        
    Returns:
        dict: Created item details or error message
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
        
        # Get category ID from item data or use default
        category_id = item_data.get('category_id', 1)  # Default to category ID 1 if not specified
        
        # Create item
        item_id = elab_manager.create_item(category_id, item_data)
        
        if item_id:
            # Get the created item
            item = elab_manager.get_item(item_id)
            return item
        else:
            return {"error": "Failed to create item"}
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return {"error": str(e)}

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Create item in elabFTW')
    parser.add_argument('--data', type=str, required=True, help='Item data as JSON string')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        item_data = json.loads(args.data)
        result = create_item(item_data)
        print(json.dumps(result))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON data: {e}")
        print(json.dumps({"error": f"Invalid JSON data: {e}"}))