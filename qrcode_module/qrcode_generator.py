#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QR Code Generation Module

Responsible for generating and exporting QR code labels for assets.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont

# Remove current directory from sys.path to avoid import conflicts with local packages
# This ensures that third-party libraries are imported from site-packages
if '' in sys.path:
    sys.path.remove('')

# Import the qrcode library
import qrcode

# Import configuration manager
from config import ConfigManager

logger = logging.getLogger(__name__)


class QRCodeGenerator:
    """QR Code Generator Class"""
    
    def __init__(self, output_dir: str = "qrcodes"):
        """Initialize QR code generator
        
        Args:
            output_dir: Output directory
        """
        self.output_dir = output_dir
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Get API URL from config
        api_url = self.config.get('elabftw', {}).get('api_url', '')
        # Extract base URL (remove /api/v2 part)
        self.base_url = api_url.split('/api/')[0] if '/api/' in api_url else 'https://elab.local'
        
        self.logger = logger
    
    def generate_qrcode(self, data: str, size: int = 10, border: int = 4) -> Optional[Image.Image]:
        """Generate QR code image
        
        Args:
            data: QR code data
            size: QR code size
            border: QR code border width
            
        Returns:
            PIL.Image.Image: QR code image, returns None if generation fails
        """
        try:
            # Use a simpler approach with qrcode.make
            # This avoids the region size error
            img = qrcode.make(data)
            return img
            
        except Exception as e:
            # Ensure error message is in English
            error_msg = str(e)
            if "生成二维码失败" in error_msg:
                error_msg = "Failed to generate QR code image"
            logger.error(f"Failed to generate QR code: {error_msg}")
            return None
    
    def create_asset_qrcode(self, asset_id: int, asset_info: Dict, filename: Optional[str] = None) -> Tuple[bool, str]:
        """Create asset QR code with title
        
        Args:
            asset_id: Asset ID
            asset_info: Asset information dictionary
            filename: Filename, auto-generated if None
            
        Returns:
            Tuple[bool, str]: (success flag, file path or error message)
        """
        try:
            # Build QR code data using the correct URL structure from config
            # Use the base_url that was extracted during initialization
            qr_data = f"{self.base_url}/database.php?mode=view&id={asset_id}"
            
            # Generate QR code using direct approach to avoid region size error
            try:
                # Use qrcode.make directly instead of going through our generate_qrcode method
                # This is a workaround for the "cannot determine region size" error
                qr_img = qrcode.make(qr_data)
                
                # Get asset title
                asset_title = asset_info.get("title", f"Asset #{asset_id}")
                
                # Create a new image with space for the title
                qr_width, qr_height = qr_img.size
                title_height = 30  # Height for title text
                new_img = Image.new("RGB", (qr_width, qr_height + title_height), "white")
                
                # Convert QR code to RGB if it's not already
                if qr_img.mode != "RGB":
                    qr_img = qr_img.convert("RGB")
                    
                # Paste QR code at the top
                new_img.paste(qr_img, (0, 0))
            except Exception as e:
                self.logger.error(f"Error creating QR code: {str(e)}")
                return False, f"Failed to generate QR code: {str(e)}"
            
            # Add title text
            draw = ImageDraw.Draw(new_img)
            try:
                # Try to load a font
                font = ImageFont.truetype("Arial", 16)
            except IOError:
                # Use default font if Arial is not available
                font = ImageFont.load_default()
            
            # Draw title text centered below QR code
            text_width = draw.textlength(asset_title, font=font)
            text_x = (qr_width - text_width) / 2
            text_y = qr_height + 5  # 5 pixels padding from QR code
            draw.text((text_x, text_y), asset_title, fill="black", font=font)
            
            # If no filename provided, auto-generate one
            if filename is None:
                asset_name = asset_info.get("title", f"asset_{asset_id}")
                # Remove characters not suitable for filenames
                asset_name = "".join(c for c in asset_name if c.isalnum() or c in "_ -")
                filename = f"{asset_name}_{asset_id}.png"
            
            # Ensure filename has .png extension
            if not filename.lower().endswith(".png"):
                filename += ".png"
            
            # Complete file path
            file_path = os.path.join(self.output_dir, filename)
            
            # Save QR code image with title
            new_img.save(file_path)
            logger.info(f"Asset QR code with title saved: {file_path}")
            
            return True, file_path
            
        except Exception as e:
            # Ensure error message is in English
            error_msg = str(e)
            if "生成二维码失败" in error_msg:
                error_msg = "Failed to generate QR code image"
            logger.error(f"Failed to create asset QR code: {error_msg}")
            return False, error_msg
    
    def create_label(self, asset_id: int, asset_info: Dict, include_qrcode: bool = True, 
                     label_size: Tuple[int, int] = (400, 200), filename: Optional[str] = None) -> Tuple[bool, str]:
        """Create asset label
        
        Args:
            asset_id: Asset ID
            asset_info: Asset information dictionary
            include_qrcode: Whether to include QR code
            label_size: Label size (width, height)
            filename: Filename, auto-generated if None
            
        Returns:
            Tuple[bool, str]: (success flag, file path or error message)
        """
        try:
            # Create label image
            label_img = Image.new("RGB", label_size, "white")
            draw = ImageDraw.Draw(label_img)
            
            # Try to load fonts, use default if failed
            try:
                # Title font
                title_font = ImageFont.truetype("Arial", 20)
                # Body text font
                text_font = ImageFont.truetype("Arial", 14)
            except IOError:
                # Use default font
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Get asset information
            asset_title = asset_info.get("title", f"Asset #{asset_id}")
            asset_category = asset_info.get("category", "")
            
            # If including QR code
            if include_qrcode:
                # Generate QR code
                qr_data = f"https://elab.local/database.php?mode=view&id={asset_id}"
                qr_img = self.generate_qrcode(qr_data, size=5, border=2)
                if qr_img is None:
                    return False, "Failed to generate QR code image"
                
                # Resize QR code
                qr_size = min(label_size[1] - 20, 150)
                qr_img = qr_img.resize((qr_size, qr_size))
                
                # Paste QR code onto the label
                label_img.paste(qr_img, (label_size[0] - qr_size - 10, 10))
                
                # Calculate text area width
                text_width = label_size[0] - qr_size - 30
            else:
                # If not including QR code, text area is the entire label width minus margins
                text_width = label_size[0] - 20
            
            # Draw title
            draw.text((10, 10), asset_title, fill="black", font=title_font)
            
            # Draw ID and category
            draw.text((10, 40), f"ID: {asset_id}", fill="black", font=text_font)
            draw.text((10, 60), f"Category: {asset_category}", fill="black", font=text_font)
            
            # Add other information
            y_pos = 80
            for key, value in asset_info.items():
                # Skip already displayed fields
                if key in ["title", "category"]:
                    continue
                
                # Skip complex types
                if isinstance(value, (dict, list)):
                    continue
                
                # Format field name
                field_name = key.replace("_", " ").title()
                
                # Draw field
                text = f"{field_name}: {value}"
                # If text is too long, truncate and add ellipsis
                if draw.textlength(text, font=text_font) > text_width:
                    while draw.textlength(text + "...", font=text_font) > text_width and len(text) > 0:
                        text = text[:-1]
                    text += "..."
                
                draw.text((10, y_pos), text, fill="black", font=text_font)
                y_pos += 20
                
                # If exceeding label height, stop adding more fields
                if y_pos >= label_size[1] - 10:
                    break
            
            # If no filename provided, auto-generate one
            if filename is None:
                asset_name = asset_info.get("title", f"asset_{asset_id}")
                # Remove characters not suitable for filenames
                asset_name = "".join(c for c in asset_name if c.isalnum() or c in "_ -")
                filename = f"{asset_name}_{asset_id}_label.png"
            
            # Ensure filename has .png extension
            if not filename.lower().endswith(".png"):
                filename += ".png"
            
            # Complete file path
            file_path = os.path.join(self.output_dir, filename)
            
            # Save label image
            label_img.save(file_path)
            logger.info(f"Asset label saved: {file_path}")
            
            return True, file_path
            
        except Exception as e:
            # Ensure error message is in English
            error_msg = str(e)
            if "生成二维码失败" in error_msg:
                error_msg = "Failed to generate QR code image"
            logger.error(f"Failed to create asset label: {error_msg}")
            return False, error_msg