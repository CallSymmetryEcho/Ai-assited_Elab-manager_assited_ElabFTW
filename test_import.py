#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to check import issues
"""

import sys
import os

# Print current directory
print(f"Current directory: {os.getcwd()}")

# Print Python path
print(f"Python path: {sys.path}")

# Try to import qrcode
try:
    import qrcode
    print(f"Successfully imported qrcode: {qrcode.__file__}")
    print(f"qrcode version: {qrcode.__version__}")
    print(f"qrcode has QRCode: {hasattr(qrcode, 'QRCode')}")
    if hasattr(qrcode, 'QRCode'):
        print(f"QRCode type: {type(qrcode.QRCode)}")
    else:
        print("qrcode does not have QRCode attribute")
        print(f"qrcode dir: {dir(qrcode)}")
except Exception as e:
    print(f"Failed to import qrcode: {e}")

# Try to import our qrcode_module
try:
    import qrcode_module
    print(f"Successfully imported qrcode_module: {qrcode_module.__file__}")
    print(f"qrcode_module dir: {dir(qrcode_module)}")
except Exception as e:
    print(f"Failed to import qrcode_module: {e}")