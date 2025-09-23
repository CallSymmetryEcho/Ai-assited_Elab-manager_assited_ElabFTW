#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
实验室资产录入自动化系统

一个基于eLabFTW的实验室资产录入自动化系统，支持摄像头捕捉、LLM分析和二维码生成。
"""

__version__ = '1.0.0'
__author__ = 'AI Assisted Group Management System'
__description__ = "Laboratory Asset Management System with eLab FTW Integration"

# Setup project paths when package is imported
from .config import ProjectPaths
_paths = ProjectPaths()

__all__ = ['__version__', '__author__', '__description__']