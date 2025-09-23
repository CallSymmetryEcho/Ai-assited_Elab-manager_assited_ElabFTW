#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fix script for qrcode module import issues
"""

import os
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to fix qrcode module issues"""
    try:
        # Get the project root directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check if qrcode directory exists
        qrcode_dir = os.path.join(project_dir, 'qrcode')
        if os.path.exists(qrcode_dir) and os.path.isdir(qrcode_dir):
            # Rename qrcode directory to qrcode_own to avoid conflicts
            qrcode_own_dir = os.path.join(project_dir, 'qrcode_own')
            if not os.path.exists(qrcode_own_dir):
                logger.info(f"Renaming {qrcode_dir} to {qrcode_own_dir}")
                shutil.move(qrcode_dir, qrcode_own_dir)
                logger.info("Directory renamed successfully")
            else:
                logger.info(f"{qrcode_own_dir} already exists, skipping rename")
        else:
            logger.info(f"{qrcode_dir} does not exist, no need to rename")
        
        # Update import statements in main.py
        main_py = os.path.join(project_dir, 'main.py')
        if os.path.exists(main_py):
            with open(main_py, 'r') as f:
                content = f.read()
            
            # Replace import statements
            if 'from qrcode.qrcode_generator import QRCodeGenerator' in content:
                content = content.replace(
                    'from qrcode.qrcode_generator import QRCodeGenerator',
                    'from qrcode_module.qrcode_generator import QRCodeGenerator'
                )
                logger.info(f"Updated import statement in {main_py}")
                
                with open(main_py, 'w') as f:
                    f.write(content)
        
        # Update import statements in ui/ui_manager.py
        ui_manager_py = os.path.join(project_dir, 'ui', 'ui_manager.py')
        if os.path.exists(ui_manager_py):
            with open(ui_manager_py, 'r') as f:
                content = f.read()
            
            # Replace import statements
            if 'from qrcode.qrcode_generator import QRCodeGenerator' in content:
                content = content.replace(
                    'from qrcode.qrcode_generator import QRCodeGenerator',
                    'from qrcode_module.qrcode_generator import QRCodeGenerator'
                )
                logger.info(f"Updated import statement in {ui_manager_py}")
                
                with open(ui_manager_py, 'w') as f:
                    f.write(content)
        
        # Ensure qrcode_module directory exists
        qrcode_module_dir = os.path.join(project_dir, 'qrcode_module')
        if not os.path.exists(qrcode_module_dir):
            os.makedirs(qrcode_module_dir)
            logger.info(f"Created directory {qrcode_module_dir}")
            
            # Create __init__.py
            init_py = os.path.join(qrcode_module_dir, '__init__.py')
            with open(init_py, 'w') as f:
                f.write('#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n\n"""\nQR Code Module\n\nProvides QR code generation and label creation functionality.\n"""\n\nfrom .qrcode_generator import QRCodeGenerator\n\n__all__ = ["QRCodeGenerator"]\n')
            logger.info(f"Created {init_py}")
            
            # Copy qrcode_generator.py from qrcode_own to qrcode_module
            qrcode_generator_py = os.path.join(qrcode_own_dir, 'qrcode_generator.py')
            if os.path.exists(qrcode_generator_py):
                qrcode_module_generator_py = os.path.join(qrcode_module_dir, 'qrcode_generator.py')
                with open(qrcode_generator_py, 'r') as f:
                    content = f.read()
                
                # Update import statements
                if 'import qrcode' in content:
                    content = content.replace(
                        'import qrcode',
                        '# Import the qrcode library with a different name to avoid conflicts\nimport sys\n\n# Remove current directory from sys.path to avoid import conflicts\nif \'\'\' in sys.path:\n    sys.path.remove(\'\'\')\n\nimport qrcode as qrcode_lib'
                    )
                    
                    # Replace qrcode.QRCode with qrcode_lib.QRCode
                    content = content.replace('qrcode.QRCode', 'qrcode_lib.QRCode')
                    content = content.replace('qrcode.constants', 'qrcode_lib.constants')
                    
                    with open(qrcode_module_generator_py, 'w') as f:
                        f.write(content)
                    logger.info(f"Created {qrcode_module_generator_py} with updated imports")
        
        logger.info("Fix completed successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Error fixing qrcode module: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())