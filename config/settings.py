#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration Management Module

Responsible for loading, saving, and managing system configuration.
"""

import os
import json
import logging
from pathlib import Path
from .paths import setup_project_paths

logger = logging.getLogger(__name__)

# Setup project paths
paths = setup_project_paths()


class ConfigManager:
    """Configuration Manager Class"""
    
    def __init__(self, config_path=None):
        """Initialize configuration manager
        
        Args:
            config_path (str, optional): Configuration file path. 
                                       If None, uses default project config.
        """
        if config_path is None:
            self.config_path = paths.get_config_file()
        else:
            self.config_path = Path(config_path)
        self.config = {}
        self.default_config = {
            "llm": {
                "provider": "openai",  # openai, anthropic, local
                "api_key": "",
                "model": "gpt-4-vision-preview",  # For OpenAI
                "local_model_path": "",  # For local models
                "temperature": 0.7,
                "max_tokens": 4000
            },
            "elabftw": {
                "api_url": "https://10.159.64.205:3148/api/v2",
                "api_key": "1-1c5237f614dfe42da3d16c6f82f7c0157950ca4e37f1cfb3d248227928b6c51a97c293f03ac78f4ea2401",
                "verify_ssl": False
            },
            "camera": {
                "resolution": [1280, 720],
                "auto_focus": True,
                "capture_delay": 2  # Delay in seconds after pressing the confirm button
            },
            "ui": {
                "theme": "light",  # light, dark
                "language": "en_US"
            },
            "storage": {
                "image_dir": "images",
                "qrcode_dir": "qrcodes"
            }
        }
    
    def load_config(self):
        """Load configuration file
        
        If the configuration file does not exist, create a default configuration file
        
        Returns:
            dict: Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Configuration file loaded: {self.config_path}")
            else:
                # If configuration file does not exist, create default configuration
                self.config = self.default_config
                self.save_config()
                logger.info(f"Default configuration file created: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}")
            # Use default configuration
            self.config = self.default_config
        
        return self.config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuration file saved: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration file: {e}")
            return False
    
    def update_config(self, new_config):
        """Update configuration
        
        Args:
            new_config (dict): New configuration dictionary
            
        Returns:
            bool: Whether the update was successful
        """
        try:
            # Recursively update configuration
            self._update_dict(self.config, new_config)
            return self.save_config()
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def _update_dict(self, d, u):
        """Recursively update dictionary
        
        Args:
            d (dict): Target dictionary
            u (dict): Update dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_dict(d[k], v)
            else:
                d[k] = v
    
    def get_value(self, key_path, default=None):
        """获取配置值
        
        Args:
            key_path (str): 键路径，如 "llm.api_key"
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        try:
            value = self.config
            for key in key_path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_value(self, key_path, value):
        """设置配置值
        
        Args:
            key_path (str): 键路径，如 "llm.api_key"
            value: 要设置的值
            
        Returns:
            bool: 设置是否成功
        """
        try:
            keys = key_path.split('.')
            d = self.config
            for key in keys[:-1]:
                if key not in d or not isinstance(d[key], dict):
                    d[key] = {}
                d = d[key]
            d[keys[-1]] = value
            return self.save_config()
        except Exception as e:
            logger.error(f"设置配置值失败: {e}")
            return False