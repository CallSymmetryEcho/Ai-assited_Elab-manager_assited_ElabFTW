#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for qrcode library
"""

import sys
import os

# Remove current directory from sys.path to avoid import conflicts
if '' in sys.path:
    sys.path.remove('')

# Try to import qrcode
try:
    import qrcode
    from PIL import Image
    
    print(f"Successfully imported qrcode: {qrcode.__file__}")
    print(f"qrcode version: {qrcode.__version__ if hasattr(qrcode, '__version__') else 'unknown'}")
    
    # Create a simple QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data('https://example.com')
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    print(f"Successfully created QR code image: {type(img)}")
    
    # Save the image
    img.save('test_qrcode.png')
    print("Saved QR code image to test_qrcode.png")
    
except Exception as e:
    print(f"Error: {e}")