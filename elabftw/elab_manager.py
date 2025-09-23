#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
elabFTW Management Module

Responsible for interacting with the elabFTW system, implementing asset information entry and management.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any, Tuple

# 导入elabapi-python库
import elabapi_python

logger = logging.getLogger(__name__)


class ElabManager:
    """elabFTW Manager Class"""
    
    def __init__(self, api_url: str, api_key: str, verify_ssl: bool = False):
        """Initialize elabFTW manager
        
        Args:
            api_url: API URL
            api_key: API key
            verify_ssl: Whether to verify SSL certificate
        """
        self.api_url = api_url
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.api_client = None
        self.initialize_api()
    
    def initialize_api(self) -> bool:
        """Initialize API client
        
        Returns:
            bool: Whether initialization was successful
        """
        try:
            # 配置API客户端
            configuration = elabapi_python.Configuration()
            configuration.host = self.api_url
            configuration.verify_ssl = self.verify_ssl
            
            # 如果不验证SSL证书，禁用警告
            if not self.verify_ssl:
                import urllib3
                urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
            
            # 创建API客户端
            self.api_client = elabapi_python.ApiClient(configuration)
            
            # 设置API密钥
            self.api_client.set_default_header(header_name='Authorization', header_value=self.api_key)
            
            # 测试连接
            info_client = elabapi_python.InfoApi(self.api_client)
            info_client.get_info()
            
            logger.info(f"Successfully connected to elabFTW API: {self.api_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to elabFTW API: {e}")
            self.api_client = None
            return False
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information
        
        Returns:
            Dict: User information
        """
        if self.api_client is None:
            if not self.initialize_api():
                return {}
        
        try:
            # 获取用户API - 使用InfoApi替代，因为UsersApi可能没有read_user_me方法
            info_api = elabapi_python.InfoApi(self.api_client)
            
            # 获取当前用户信息
            info = info_api.get_info()
            
            # 提取用户信息 - 将对象转换为字典
            user_data = {}
            
            # 检查info是否有to_dict方法
            if hasattr(info, "to_dict"):
                info_dict = info.to_dict()
                user_data = {
                    "username": info_dict.get("username", "N/A"),
                    "email": info_dict.get("email", "N/A"),
                    "team": info_dict.get("team_name", "N/A")
                }
            else:
                # 尝试直接访问属性
                user_data = {
                    "username": getattr(info, "username", "N/A"),
                    "email": getattr(info, "email", "N/A"),
                    "team": getattr(info, "team_name", "N/A")
                }
            
            return user_data
            
        except Exception as e:
            logger.error(f"Failed to get user information: {e}")
            return {}
    
    def get_item_templates(self) -> List[Dict[str, Any]]:
        """Get item templates list
        
        Returns:
            List[Dict]: Templates list
        """
        if self.api_client is None:
            if not self.initialize_api():
                return []
        
        try:
            # 获取物品类型API
            items_types_api = elabapi_python.ItemsTypesApi(self.api_client)
            
            # 获取所有物品类型
            items_types = items_types_api.read_items_types()
            
            # 转换为简单的字典列表
            templates = []
            for item_type in items_types:
                template_data = {
                    "id": item_type.id,
                    "title": item_type.title,
                    "body": item_type.body,
                    "color": item_type.color
                }
                
                # 检查是否有category属性
                if hasattr(item_type, 'category'):
                    template_data["category"] = item_type.category
                
                templates.append(template_data)
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to get item templates: {e}")
            return []
    
    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get template by ID
        
        Args:
            template_id: Template ID
            
        Returns:
            Dict or None: Template information
        """
        templates = self.get_item_templates()
        for template in templates:
            if template["id"] == template_id:
                return template
        return None
    
    def create_item(self, category_id: int, data: Dict[str, Any]) -> Optional[int]:
        """Create item
        
        Args:
            category_id: Item category ID
            data: Item data
            
        Returns:
            int or None: Created item ID
        """
        if self.api_client is None:
            if not self.initialize_api():
                return None
        
        try:
            # 获取物品API
            items_api = elabapi_python.ItemsApi(self.api_client)
            
            # 准备创建数据
            create_data = {"category_id": category_id}
            
            # 添加其他数据
            if "title" in data:
                create_data["title"] = data["title"]
            if "body" in data:
                create_data["body"] = data["body"]
            if "tags" in data:
                create_data["tags"] = data["tags"]
            
            # 创建物品
            response_data, status_code, headers = items_api.post_item_with_http_info(body=create_data)
            
            # 从Location头中提取ID
            if status_code == 201 and "Location" in headers:
                location = headers.get("Location")
                item_id = int(location.split("/").pop())
                logger.info(f"Item created (ID: {item_id})")
                
                # If there is other data, update the item
                if len(data) > 3:  # Data other than title, body, tags
                    self.update_item(item_id, data)
                
                return item_id
            else:
                logger.error(f"Failed to create item, status code: {status_code}")
                return None
            
        except Exception as e:
            logger.error(f"Exception creating item: {e}")
            return None
    
    def update_item(self, item_id: int, data: Dict[str, Any]) -> bool:
        """Update item
        
        Args:
            item_id: Item ID
            data: Update data
            
        Returns:
            bool: Whether the update was successful
        """
        if self.api_client is None:
            if not self.initialize_api():
                return False
        
        try:
            # 获取物品API
            items_api = elabapi_python.ItemsApi(self.api_client)
            
            # Update item
            items_api.patch_item(item_id, body=data)
            logger.info(f"Item updated (ID: {item_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update item: {e}")
            return False
    
    def upload_image(self, item_id: int, image_path: str, comment: str = "Uploaded via automation system") -> Optional[int]:
        """Upload image
        
        Args:
            item_id: Item ID
            image_path: Image file path
            comment: Comment
            
        Returns:
            int or None: Upload file ID
        """
        if self.api_client is None:
            if not self.initialize_api():
                return None
        
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                logger.error(f"Image file does not exist: {image_path}")
                return None
            
            # Get upload API
            uploads_api = elabapi_python.UploadsApi(self.api_client)
            
            # Upload file
            response = uploads_api.post_upload_with_http_info(
                "items",  # Entity type
                item_id,  # Entity ID
                file=image_path,
                comment=comment
            )
            
            # Check response
            if response[1] == 201:  # Status code 201 means created successfully
                # Get uploaded file ID
                uploads = uploads_api.read_uploads("items", item_id)
                if uploads:
                    # Assume the last uploaded file is the one we just uploaded
                    upload_id = uploads[-1].id
                    logger.info(f"Image uploaded (ID: {upload_id})")
                    return upload_id
            
            logger.error("Failed to upload image")
            return None
            
        except Exception as e:
            logger.error(f"Exception uploading image: {e}")
            return None
    
    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get item information
        
        Args:
            item_id: Item ID
            
        Returns:
            Dict or None: Item information
        """
        if self.api_client is None:
            if not self.initialize_api():
                return None
        
        try:
            # Get items API
            items_api = elabapi_python.ItemsApi(self.api_client)
            
            # Get item
            item = items_api.get_item(item_id)
            
            # Convert to dictionary
            item_dict = {
                "id": item.id,
                "title": item.title,
                "body": item.body,
                "category": item.category,
                "tags": item.tags if hasattr(item, 'tags') else [],
                "metadata": item.metadata if hasattr(item, 'metadata') else {}
            }
            
            # 添加可选属性
            if hasattr(item, 'date'):
                item_dict["date"] = item.date
            
            return item_dict
            
        except Exception as e:
            logger.error(f"Failed to get item information: {e}")
            return None
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Get all items
        
        Returns:
            List[Dict]: List of items
        """
        if self.api_client is None:
            if not self.initialize_api():
                return []
        
        try:
            # Get items API
            items_api = elabapi_python.ItemsApi(self.api_client)
            
            # Get all items
            items = items_api.read_items(limit=100)  # Limit to 100 items for performance
            
            # Convert to dictionary list
            items_list = []
            for item in items:
                item_dict = {
                    "id": item.id,
                    "title": item.title,
                    "category": item.category,
                    "date": item.date if hasattr(item, 'date') else None,
                    "tags": item.tags if hasattr(item, 'tags') else []
                }
                items_list.append(item_dict)
            
            return items_list
            
        except Exception as e:
            logger.error(f"Failed to get items: {e}")
            return []
    
    def get_template_structure(self, template_id: int) -> str:
        """Get template structure for LLM prompt
        
        Args:
            template_id: Template ID
            
        Returns:
            str: Template structure description
        """
        template = self.get_template_by_id(template_id)
        if not template:
            return "Template not found"
        
        # Extract template structure
        # This needs to be parsed according to the actual template format
        # The following is a simple example, actual situations may require more complex parsing
        
        body = template.get("body", "")
        
        # Simple processing: remove HTML tags, keep text content
        import re
        body_text = re.sub(r'<[^>]+>', '', body)
        
        # Build template structure description
        structure = f"""
        Template name: {template.get('title', '')}
        
        Template structure:
        {body_text}
        
        Please provide asset information in JSON format based on the above structure.
        """
        
        return structure
        
    def export_qrcode(self, item_id: int, output_dir: str = None, filename: str = None) -> Tuple[bool, str]:
        """Export asset QR code from elabFTW
        
        Args:
            item_id: Asset ID
            output_dir: Output directory, uses default directory if None
            filename: Filename, auto-generated if None
            
        Returns:
            Tuple[bool, str]: (success flag, file path or error message)
        """
        try:
            # Get asset information
            asset_info = self.get_item(item_id)
            if not asset_info:
                return False, f"Unable to get asset information (ID: {item_id})"
            
            # Import QRCodeGenerator
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from qrcode.qrcode_generator import QRCodeGenerator
            
            # Create QRCodeGenerator instance
            # If no output directory specified, use the default qrcodes directory
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'qrcodes')
                # Ensure directory exists
                os.makedirs(output_dir, exist_ok=True)
                
            qrcode_generator = QRCodeGenerator(output_dir=output_dir)
            
            # Generate QR code
            success, result = qrcode_generator.create_asset_qrcode(item_id, asset_info, filename)
            
            if success:
                logger.info(f"Asset QR code successfully exported: {result}")
            else:
                logger.error(f"Failed to export asset QR code: {result}")
                
            return success, result
            
        except Exception as e:
            logger.error(f"Error exporting asset QR code: {e}")
            return False, str(e)
    
    def create_asset_from_llm_data(self, template_id: int, llm_data: Dict[str, Any], image_path: Optional[str] = None) -> Optional[int]:
        """Create asset from LLM analysis data
        
        Args:
            template_id: Template ID
            llm_data: LLM analysis data
            image_path: Image file path
            
        Returns:
            int or None: Created asset ID
        """
        try:
            # Prepare creation data
            create_data = {
                "title": llm_data.get("title", "Untitled Asset"),
                "body": self._format_body_from_llm_data(llm_data),
                "tags": llm_data.get("tags", [])
            }
            
            # Create item
            item_id = self.create_item(template_id, create_data)
            if not item_id:
                return None
            
            # If image is provided, upload it
            if image_path and os.path.exists(image_path):
                self.upload_image(item_id, image_path)
            
            return item_id
            
        except Exception as e:
            logger.error(f"Failed to create asset from LLM data: {e}")
            return None
    
    def _format_body_from_llm_data(self, llm_data: Dict[str, Any]) -> str:
        """Format item body from LLM data
        
        Args:
            llm_data: LLM analysis data
            
        Returns:
            str: Formatted HTML body
        """
        # Remove fields that should not be displayed in the body
        body_data = llm_data.copy()
        if "title" in body_data:
            del body_data["title"]
        if "tags" in body_data:
            del body_data["tags"]
        
        # Build HTML body
        html = "<div class='asset-details'>\n"
        
        # Add each field
        for key, value in body_data.items():
            # Format field name
            field_name = key.replace("_", " ").title()
            
            # Handle different types of values
            if isinstance(value, list):
                value_str = "<ul>\n"
                for item in value:
                    value_str += f"<li>{item}</li>\n"
                value_str += "</ul>"
            elif isinstance(value, dict):
                value_str = "<ul>\n"
                for k, v in value.items():
                    value_str += f"<li><strong>{k}:</strong> {v}</li>\n"
                value_str += "</ul>"
            else:
                value_str = str(value)
            
            # Add to HTML
            html += f"<div class='asset-field'>\n"
            html += f"<h3>{field_name}</h3>\n"
            html += f"<div class='asset-value'>{value_str}</div>\n"
            html += f"</div>\n"
        
        html += "</div>"
        return html
    
    def get_settings(self) -> Dict[str, Any]:
        """获取elabFTW设置
        
        Returns:
            Dict: 设置信息
        """
        try:
            # 返回当前配置的设置
            settings = {
                'url': self.api_url,
                'token': '***' if self.api_key else '',  # 隐藏实际token
                'teamId': 1,  # 默认团队ID
                'defaultCategory': '1',  # 默认分类
                'verifySSL': self.verify_ssl
            }
            
            logger.info("Retrieved elabFTW settings")
            return settings
            
        except Exception as e:
            logger.error(f"Error getting elabFTW settings: {e}")
            return {}
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """更新elabFTW设置
        
        Args:
            settings: 新的设置
            
        Returns:
            Dict: 更新结果
        """
        try:
            # 更新API URL
            if 'url' in settings:
                self.api_url = settings['url']
            
            # 更新API密钥
            if 'token' in settings and settings['token'] != '***':
                self.api_key = settings['token']
            
            # 更新SSL验证设置
            if 'verifySSL' in settings:
                self.verify_ssl = settings['verifySSL']
            
            # 重新初始化API客户端
            success = self.initialize_api()
            
            result = {
                'success': success,
                'message': 'Settings updated successfully' if success else 'Failed to update settings',
                'timestamp': json.dumps(settings, default=str)
            }
            
            logger.info(f"Updated elabFTW settings: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating elabFTW settings: {e}")
            return {
                'success': False,
                'message': f'Error updating settings: {str(e)}',
                'timestamp': ''
            }