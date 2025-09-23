#!/usr/bin/env python3

"""
Bridge script to handle LLM settings operations for the web frontend.
This script is called by the web server to get and update LLM settings.
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
logger = logging.getLogger('llm_settings')

# Add parent directory to path to import local modules
sys.path.append(str(Path(__file__).parent.parent))

# Import after path setup to avoid import errors
try:
    from llm.llm_manager import LLMManager
    from config.config_manager import ConfigManager
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def get_llm_manager():
    """
    Initialize and return an LLMManager instance with current configuration.
    
    Returns:
        LLMManager: Initialized LLMManager instance
    """
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize LLMManager
        llm_manager = LLMManager(config)
        return llm_manager
    except Exception as e:
        logger.error(f"Error initializing LLMManager: {e}")
        raise

def get_llm_settings():
    """
    Get LLM settings from configuration.
    
    Returns:
        dict: LLM settings
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Extract LLM settings
        llm_settings = {
            "provider": config.get("llm", {}).get("provider", "openai"),
            "model": config.get("llm", {}).get("model", "gpt-4-vision-preview"),
            "api_key": config.get("llm", {}).get("api_key", ""),
            "temperature": config.get("llm", {}).get("temperature", 0.7),
            "max_tokens": config.get("llm", {}).get("max_tokens", 1000),
            "prompt_template": config.get("llm", {}).get("prompt_template", "Analyze this image and describe what you see.")
        }
        
        return llm_settings
    except Exception as e:
        logger.error(f"Error getting LLM settings: {e}")
        return {"error": str(e)}

def update_llm_settings(settings):
    """
    Update LLM settings in configuration.
    
    Args:
        settings (dict): New LLM settings
        
    Returns:
        dict: Updated settings
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Update LLM settings
        if "llm" not in config:
            config["llm"] = {}
            
        config["llm"]["provider"] = settings.get("provider", "openai")
        config["llm"]["model"] = settings.get("model", "gpt-4-vision-preview")
        config["llm"]["api_key"] = settings.get("api_key", "")
        config["llm"]["temperature"] = settings.get("temperature", 0.7)
        config["llm"]["max_tokens"] = settings.get("max_tokens", 1000)
        config["llm"]["prompt_template"] = settings.get("prompt_template", "Analyze this image and describe what you see.")
        
        # Save updated configuration
        config_manager.save_config(config)
        
        return get_llm_settings()
    except Exception as e:
        logger.error(f"Error updating LLM settings: {e}")
        return {"error": str(e)}

def test_llm_connection(settings=None):
    """
    Test connection to LLM API.
    
    Args:
        settings (dict, optional): LLM settings to test
        
    Returns:
        dict: Connection test result
    """
    try:
        if settings:
            # Create temporary config with provided settings
            temp_config = {
                "llm": {
                    "provider": settings.get("provider", "openai"),
                    "model": settings.get("model", "gpt-4-vision-preview"),
                    "api_key": settings.get("api_key", ""),
                    "temperature": settings.get("temperature", 0.7),
                    "max_tokens": settings.get("max_tokens", 1000)
                }
            }
            llm_manager = LLMManager(temp_config)
        else:
            llm_manager = get_llm_manager()
        
        # Test connection by sending a simple query
        result = llm_manager.test_connection()
        return {"success": True, "message": "Connection successful", "data": result}
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {"success": False, "message": f"Connection failed: {str(e)}"}

def get_available_models():
    """
    Get a list of available LLM models.
    
    Returns:
        dict: List of available models
    """
    try:
        llm_manager = get_llm_manager()
        models = llm_manager.get_available_models()
        return {"success": True, "models": models}
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='LLM Settings Bridge Script')
    parser.add_argument('--action', required=True, 
                        choices=['get_settings', 'update_settings', 'test_connection', 'get_models'],
                        help='Action to perform')
    parser.add_argument('--settings', help='JSON string with LLM settings')
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
        result = get_llm_settings()
    elif args.action == 'update_settings':
        if not settings:
            logger.error("Settings data is required for update_settings action")
            sys.exit(1)
        result = update_llm_settings(settings)
    elif args.action == 'test_connection':
        result = test_llm_connection(settings)
    elif args.action == 'get_models':
        result = get_available_models()
    
    # Output the result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()