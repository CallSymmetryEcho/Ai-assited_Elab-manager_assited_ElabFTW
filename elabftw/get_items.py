#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get Items from elabFTW

This script retrieves items from the elabFTW system and returns them as JSON.
"""

import os
import sys
import json
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elabftw.elab_manager import ElabManager
from config import ConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_items():
    """Get all items from elabFTW
    
    Returns:
        list: List of items
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
        
        # Get items
        items = elab_manager.get_items()
        return items
    except Exception as e:
        logger.error(f"Error getting items: {e}")
        return []

if __name__ == "__main__":
    items = get_items()
    print(json.dumps(items))