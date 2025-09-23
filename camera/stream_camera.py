#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Camera Streaming Module

Streams camera frames as base64-encoded images for the web frontend.
"""

import os
import sys
import time
import json
import base64
import logging
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import camera manager
from camera.camera_manager import CameraManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Camera Streaming Module')
    parser.add_argument('--device', type=int, default=0, help='Camera device ID')
    parser.add_argument('--width', type=int, default=640, help='Frame width')
    parser.add_argument('--height', type=int, default=480, help='Frame height')
    parser.add_argument('--fps', type=int, default=15, help='Frames per second')
    return parser.parse_args()


def main():
    """Main function"""
    # Parse arguments
    args = parse_args()
    
    # Initialize camera manager
    camera_manager = CameraManager(device_id=args.device, resolution=(args.width, args.height))
    
    # Initialize camera
    if not camera_manager.initialize():
        logger.error("Failed to initialize camera")
        sys.exit(1)
    
    # Start camera
    if not camera_manager.start():
        logger.error("Failed to start camera")
        sys.exit(1)
    
    try:
        # Stream frames
        frame_interval = 1.0 / args.fps
        last_frame_time = 0
        
        while True:
            current_time = time.time()
            
            # Control frame rate
            if current_time - last_frame_time >= frame_interval:
                # Read frame
                frame = camera_manager.read_frame()
                
                if frame is not None:
                    # Convert frame to JPEG
                    _, buffer = cv2.imencode('.jpg', frame)
                    
                    # Convert to base64
                    base64_frame = base64.b64encode(buffer).decode('utf-8')
                    
                    # Create frame data
                    frame_data = {
                        'image': base64_frame,
                        'timestamp': current_time,
                        'width': args.width,
                        'height': args.height
                    }
                    
                    # Output as JSON
                    print(json.dumps(frame_data), flush=True)
                    
                    # Update last frame time
                    last_frame_time = current_time
                else:
                    logger.error("Failed to read frame")
                    time.sleep(1)
            
            # Small sleep to prevent CPU overuse
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        logger.info("Streaming stopped by user")
    except Exception as e:
        logger.error(f"Streaming error: {e}")
    finally:
        # Stop camera
        camera_manager.stop()


if __name__ == "__main__":
    # Import OpenCV here to avoid import errors
    import cv2
    main()