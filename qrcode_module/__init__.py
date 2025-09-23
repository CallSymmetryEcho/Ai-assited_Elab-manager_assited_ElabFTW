#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QR Code Module

Provides QR code generation and label creation functionality.
"""

# Import the QRCodeGenerator class but make sure to avoid conflicts with the third-party qrcode library
from .qrcode_generator import QRCodeGenerator

__all__ = ['QRCodeGenerator']