#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Project Paths Management

Centralized path management for the Lab Asset Manager project.
"""

import os
import sys
from pathlib import Path


class ProjectPaths:
    """Centralized project path management"""
    
    def __init__(self):
        # Get the project root directory (lab_asset_manager)
        self._project_root = Path(__file__).parent.parent.resolve()
        
        # Add project root to Python path if not already there
        project_root_str = str(self._project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
    
    @property
    def project_root(self) -> Path:
        """Get project root directory"""
        return self._project_root
    
    @property
    def config_dir(self) -> Path:
        """Get config directory"""
        return self._project_root / "config"
    
    @property
    def utils_dir(self) -> Path:
        """Get utils directory"""
        return self._project_root / "utils"
    
    @property
    def elabftw_dir(self) -> Path:
        """Get elabftw directory"""
        return self._project_root / "elabftw"
    
    @property
    def camera_dir(self) -> Path:
        """Get camera directory"""
        return self._project_root / "camera"
    
    @property
    def llm_dir(self) -> Path:
        """Get llm directory"""
        return self._project_root / "llm"
    
    @property
    def web_dir(self) -> Path:
        """Get web directory"""
        return self._project_root / "web"
    
    @property
    def images_dir(self) -> Path:
        """Get images directory"""
        return self._project_root / "images"
    
    @property
    def qrcodes_dir(self) -> Path:
        """Get qrcodes directory"""
        return self._project_root / "qrcodes"
    
    def get_config_file(self, filename: str = "config.json") -> Path:
        """Get path to configuration file"""
        return self._project_root / filename
    
    def ensure_directory(self, directory: Path) -> Path:
        """Ensure directory exists, create if it doesn't"""
        directory.mkdir(parents=True, exist_ok=True)
        return directory


# Global instance for easy access
paths = ProjectPaths()


def setup_project_paths():
    """Setup project paths - call this at the beginning of scripts"""
    return paths