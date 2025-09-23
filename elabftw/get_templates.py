#!/usr/bin/env python3

"""
Get templates from elabFTW for the web API.
This script provides template information for the LLM analysis workflow.
"""

import json
import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置项目路径
from config import ProjectPaths
paths = ProjectPaths()

from elabftw.elab_manager import ElabManager
from config import ConfigManager

def get_templates():
    """Get templates from elabFTW"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Get elabFTW configuration
        elab_config = config.get("elabftw", {})
        api_url = elab_config.get("api_url", "")
        api_key = elab_config.get("api_key", "")
        
        if not api_url or not api_key:
            return {
                "success": False,
                "message": "elabFTW configuration not found"
            }
        
        # Initialize elabFTW manager
        elab_manager = ElabManager(api_url, api_key)
        
        # Get templates
        templates = elab_manager.get_item_templates()
        
        return {
            "success": True,
            "templates": templates
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting templates: {str(e)}"
        }

def get_template_structure(template_id):
    """Get template structure for LLM prompt"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Get elabFTW configuration
        elab_config = config.get("elabftw", {})
        api_url = elab_config.get("api_url", "")
        api_key = elab_config.get("api_key", "")
        
        if not api_url or not api_key:
            return {
                "success": False,
                "message": "elabFTW configuration not found"
            }
        
        # Initialize elabFTW manager
        elab_manager = ElabManager(api_url, api_key)
        
        # Get template structure
        structure = elab_manager.get_template_structure(int(template_id))
        
        return {
            "success": True,
            "structure": structure
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting template structure: {str(e)}"
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Get elabFTW templates')
    parser.add_argument('--template-id', type=int, help='Get specific template structure')
    
    args = parser.parse_args()
    
    if args.template_id:
        result = get_template_structure(args.template_id)
    else:
        result = get_templates()
    
    print(json.dumps(result, indent=2))
    
    return 0 if result["success"] else 1

if __name__ == "__main__":
    sys.exit(main())