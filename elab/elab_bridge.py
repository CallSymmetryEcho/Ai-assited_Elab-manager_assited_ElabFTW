#!/usr/bin/env python3

"""
Bridge script to handle elabFTW operations for the web frontend.
This script is called by the web server to interact with the elabFTW API.
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
logger = logging.getLogger('elab_bridge')

# Add parent directory to path to import local modules
sys.path.append(str(Path(__file__).parent.parent))

# Import after path setup to avoid import errors
try:
    from elab.elab_manager import ElabManager
    from config.config_manager import ConfigManager
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def get_elab_manager():
    """
    Initialize and return an ElabManager instance with current configuration.
    
    Returns:
        ElabManager: Initialized ElabManager instance
    """
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize ElabManager
        elab_manager = ElabManager(config)
        return elab_manager
    except Exception as e:
        logger.error(f"Error initializing ElabManager: {e}")
        raise

def get_items():
    """
    Get all items from elabFTW.
    
    Returns:
        list: List of items
    """
    try:
        elab_manager = get_elab_manager()
        items = elab_manager.get_items()
        return items
    except Exception as e:
        logger.error(f"Error getting items: {e}")
        return {"error": str(e)}

def get_item(item_id):
    """
    Get a specific item from elabFTW.
    
    Args:
        item_id (int): ID of the item to retrieve
        
    Returns:
        dict: Item details
    """
    try:
        elab_manager = get_elab_manager()
        item = elab_manager.get_item(item_id)
        return item
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        return {"error": str(e)}

def create_item(item_data):
    """
    Create a new item in elabFTW.
    
    Args:
        item_data (dict): Item data to create
        
    Returns:
        dict: Created item details
    """
    try:
        elab_manager = get_elab_manager()
        result = elab_manager.create_item(item_data)
        return result
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return {"error": str(e)}

def update_item(item_id, item_data):
    """
    Update an existing item in elabFTW.
    
    Args:
        item_id (int): ID of the item to update
        item_data (dict): Updated item data
        
    Returns:
        dict: Updated item details
    """
    try:
        elab_manager = get_elab_manager()
        result = elab_manager.update_item(item_id, item_data)
        return result
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        return {"error": str(e)}

def delete_item(item_id):
    """
    Delete an item from elabFTW.
    
    Args:
        item_id (int): ID of the item to delete
        
    Returns:
        dict: Result of the deletion operation
    """
    try:
        elab_manager = get_elab_manager()
        result = elab_manager.delete_item(item_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        return {"error": str(e)}

def get_settings():
    """
    Get elabFTW settings from configuration.
    
    Returns:
        dict: elabFTW settings
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Extract elabFTW settings
        elab_settings = {
            "url": config.get("elab", {}).get("url", ""),
            "token": config.get("elab", {}).get("token", ""),
            "teamId": config.get("elab", {}).get("team_id", 1),
            "defaultCategory": config.get("elab", {}).get("default_category", "1")
        }
        
        return elab_settings
    except Exception as e:
        logger.error(f"Error getting elabFTW settings: {e}")
        return {"error": str(e)}

def update_settings(settings):
    """
    Update elabFTW settings in configuration.
    
    Args:
        settings (dict): New elabFTW settings
        
    Returns:
        dict: Updated settings
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Update elabFTW settings
        if "elab" not in config:
            config["elab"] = {}
            
        config["elab"]["url"] = settings.get("url", "")
        config["elab"]["token"] = settings.get("token", "")
        config["elab"]["team_id"] = settings.get("teamId", 1)
        config["elab"]["default_category"] = settings.get("defaultCategory", "1")
        
        # Save updated configuration
        config_manager.save_config(config)
        
        return get_settings()
    except Exception as e:
        logger.error(f"Error updating elabFTW settings: {e}")
        return {"error": str(e)}

def test_connection(settings=None):
    """
    Test connection to elabFTW API.
    
    Args:
        settings (dict, optional): elabFTW settings to test
        
    Returns:
        dict: Connection test result
    """
    try:
        if settings:
            # Create temporary config with provided settings
            temp_config = {
                "elab": {
                    "url": settings.get("url", ""),
                    "token": settings.get("token", ""),
                    "team_id": settings.get("teamId", 1)
                }
            }
            elab_manager = ElabManager(temp_config)
        else:
            elab_manager = get_elab_manager()
        
        # Test connection by trying to get user info
        result = elab_manager.test_connection()
        return {"success": True, "message": "Connection successful", "data": result}
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {"success": False, "message": f"Connection failed: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description='elabFTW Bridge Script')
    parser.add_argument('--action', required=True, 
                        choices=['get_items', 'get_item', 'create_item', 'update_item', 'delete_item', 
                                 'get_settings', 'update_settings', 'test_connection'],
                        help='Action to perform')
    parser.add_argument('--id', type=int, help='Item ID for get_item, update_item, or delete_item')
    parser.add_argument('--data', help='JSON string with item data or settings')
    parser.add_argument('--output', help='Path to save the results (JSON)')
    
    args = parser.parse_args()
    
    # Parse data if provided
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON data format")
            sys.exit(1)
    
    # Perform the requested action
    result = None
    
    if args.action == 'get_items':
        result = get_items()
    elif args.action == 'get_item':
        if not args.id:
            logger.error("Item ID is required for get_item action")
            sys.exit(1)
        result = get_item(args.id)
    elif args.action == 'create_item':
        if not data:
            logger.error("Item data is required for create_item action")
            sys.exit(1)
        result = create_item(data)
    elif args.action == 'update_item':
        if not args.id or not data:
            logger.error("Item ID and data are required for update_item action")
            sys.exit(1)
        result = update_item(args.id, data)
    elif args.action == 'delete_item':
        if not args.id:
            logger.error("Item ID is required for delete_item action")
            sys.exit(1)
        result = delete_item(args.id)
    elif args.action == 'get_settings':
        result = get_settings()
    elif args.action == 'update_settings':
        if not data:
            logger.error("Settings data is required for update_settings action")
            sys.exit(1)
        result = update_settings(data)
    elif args.action == 'test_connection':
        result = test_connection(data)
    
    # Output the result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()