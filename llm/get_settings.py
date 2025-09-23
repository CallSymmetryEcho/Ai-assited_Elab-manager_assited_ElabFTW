#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
获取LLM设置的脚本

从配置文件中读取LLM的相关设置，包括API密钥、模型名称等。
"""

import json
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置项目路径
from config import ConfigManager, ProjectPaths
paths = ProjectPaths()

def get_llm_settings():
    """Get LLM settings from configuration"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Extract LLM settings
        llm_config = config.get("llm", {})
        
        settings = {
            "provider": llm_config.get("provider", "openai"),
            "model": llm_config.get("model", "gpt-4-vision-preview"),
            "api_key_set": bool(llm_config.get("api_key", "")),
            "base_url": llm_config.get("base_url", ""),
            "max_tokens": llm_config.get("max_tokens", 1000),
            "temperature": llm_config.get("temperature", 0.7),
            "system_prompt": llm_config.get("system_prompt", ""),
            "analysis_prompt": llm_config.get("analysis_prompt", "")
        }
        
        return {
            "success": True,
            "settings": settings
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting LLM settings: {str(e)}"
        }

def main():
    """Main function"""
    try:
        result = get_llm_settings()
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