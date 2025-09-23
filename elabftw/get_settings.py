#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
eLabFTW Settings Bridge Script

This script provides eLabFTW settings information for the web API.
It returns JSON-formatted eLabFTW configuration data.
"""

import json
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use centralized configuration management
from config import ConfigManager, ProjectPaths

# Setup project paths
paths = ProjectPaths()

def get_elabftw_settings():
    """Get eLabFTW settings from configuration"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Extract eLabFTW settings
        elab_config = config.get("elabftw", {})
        
        settings = {
            "server_url": elab_config.get("server_url", ""),
            "api_key_set": bool(elab_config.get("api_key", "")),
            "team_id": elab_config.get("team_id", ""),
            "category_id": elab_config.get("category_id", ""),
            "auto_upload": elab_config.get("auto_upload", False),
            "include_metadata": elab_config.get("include_metadata", True),
            "default_tags": elab_config.get("default_tags", [])
        }
        
        return {
            "success": True,
            "settings": settings
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting eLabFTW settings: {str(e)}"
        }

def main():
    """Main function"""
    try:
        result = get_elabftw_settings()
        print(json.dumps(result, indent=2))
        return 0 if result["success"] else 1
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"Script error: {str(e)}"
        }
        print(json.dumps(error_result, indent=2))
        return 1

if __name__ == "__main__":
    sys.exit(main())