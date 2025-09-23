#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration Package

Centralized configuration management for the Lab Asset Manager.
"""

from .paths import ProjectPaths
from .settings import ConfigManager

__all__ = ['ProjectPaths', 'ConfigManager']