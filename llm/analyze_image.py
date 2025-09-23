#!/usr/bin/env python3

"""
Bridge script to analyze images using the LLM processor.
This script is called by the web server to process image analysis requests.
"""

import argparse
import json
import sys
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('analyze_image')

# Add parent directory to path to import local modules
sys.path.append(str(Path(__file__).parent.parent))

# Import after path setup to avoid import errors
try:
    from llm.llm_manager import LLMManager
    from config import ConfigManager
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def analyze_image(image_path, template_id=None, additional_prompt=""):
    """
    Analyze an image using the LLM processor with eLab FTW template integration.
    
    Args:
        image_path (str): Path to the image file
        template_id (int, optional): eLab FTW template ID for structured analysis
        additional_prompt (str, optional): Additional instructions for the LLM
        
    Returns:
        dict: Analysis results
    """
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize LLM manager
        llm_manager = LLMManager(config)
        
        # Get template structure if template_id is provided
        template_structure = "Please analyze this laboratory asset and provide relevant information including name, type, and any visible details."
        
        if template_id:
            try:
                # Import eLab manager
                from elabftw.elab_manager import ElabManager
                
                # Get elabFTW configuration
                elab_config = config.get("elabftw", {})
                api_url = elab_config.get("api_url", "")
                api_key = elab_config.get("api_key", "")
                
                if api_url and api_key:
                    elab_manager = ElabManager(api_url, api_key)
                    template_structure = elab_manager.get_template_structure(template_id)
                    logger.info(f"Using eLab FTW template {template_id} for analysis")
                else:
                    logger.warning("eLab FTW configuration not found, using default template")
                    
            except Exception as e:
                logger.warning(f"Failed to get template structure: {e}, using default template")
        
        # Prepare user prompt
        user_prompt = "Analyze this laboratory asset image and identify key details."
        if additional_prompt:
            user_prompt += f" {additional_prompt}"
        
        # Process the image using the LLM manager's analyze_asset method
        logger.info(f"Analyzing image: {image_path}")
        result = llm_manager.analyze_asset(image_path, template_structure, user_prompt)
        
        # Parse the result into a structured format
        structured_result = parse_llm_response(result, template_id)
        
        return structured_result
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {"error": str(e)}

def parse_llm_response(llm_response, template_id=None):
    """
    Parse the LLM response into a structured format.
    
    Args:
        llm_response (str or dict): Raw response from the LLM
        template_id (int, optional): eLab FTW template ID used for analysis
        
    Returns:
        dict: Structured data extracted from the response
    """
    result = {}
    
    try:
        # If the response is already a dictionary (e.g., error response), return it
        if isinstance(llm_response, dict):
            return llm_response
            
        # First try to parse as JSON
        try:
            # Check if the response is already in JSON format
            if llm_response.strip().startswith('{') and llm_response.strip().endswith('}'): 
                result = json.loads(llm_response)
                return result
        except json.JSONDecodeError:
            pass
        
        # If not JSON, try to extract key-value pairs
        lines = llm_response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                result[key] = value
        
        # Always include a name field if not present
        if 'name' not in result and 'asset_name' not in result:
            result['asset_name'] = "Unnamed Asset"
            
        # Add template_id to result for reference
        if template_id:
            result['template_id'] = template_id
            
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        result = {"error": f"Failed to parse LLM response: {str(e)}"}
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Analyze an image using LLM with eLab FTW template integration')
    parser.add_argument('--image', required=True, help='Path to the image file')
    parser.add_argument('--template-id', type=int, help='eLab FTW template ID for structured analysis')
    parser.add_argument('--prompt', help='Additional instructions for the LLM')
    parser.add_argument('--output', help='Path to save the analysis results (JSON)')
    
    args = parser.parse_args()
    
    # Analyze the image
    result = analyze_image(args.image, args.template_id, args.prompt or "")
    
    # Output the result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()