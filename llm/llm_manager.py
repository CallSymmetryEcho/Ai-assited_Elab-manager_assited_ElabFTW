#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM管理模块

负责与不同的大型语言模型(LLM)进行交互，支持OpenAI、Anthropic和本地模型。
"""

import os
import base64
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """LLM基类，定义通用接口"""
    
    @abstractmethod
    def analyze_image(self, image_path: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """分析图像并返回结构化信息
        
        Args:
            image_path: 图像文件路径
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Returns:
            Dict: 结构化的分析结果
        """
        pass


class OpenAILLM(BaseLLM):
    """OpenAI LLM Implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-vision-preview", temperature: float = 0.7, max_tokens: int = 4000):
        """Initialize OpenAI LLM
        
        Args:
            api_key: OpenAI API key
            model: Model name
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def _model_supports_vision(self, model: str) -> bool:
        """Check if the model supports vision/image analysis
        
        Args:
            model: The model name to check
            
        Returns:
            bool: True if the model supports vision, False otherwise
        """
        # List of models that support vision capabilities
        vision_models = ["gpt-4-vision-preview", "gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
        
        # Check if the model is in the list of vision models
        return any(vision_model in model for vision_model in vision_models)
    
    def analyze_image(self, image_path: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Using OpenAI to analyze images"""
        try:
            # Check if the model supports vision capabilities
            if not self._model_supports_vision(self.model):
                error_msg = f"Model '{self.model}' does not support image analysis. Please use a vision-capable model like gpt-4-vision-preview, gpt-4o, or gpt-4o-mini."
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Read image and convert to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Build request headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Build request payload
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "response_format": {"type": "json_object"}
            }
            
            # Send request
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Try to parse JSON response
            import json
            try:
                parsed_content = json.loads(content)
                return parsed_content
            except json.JSONDecodeError:
                logger.warning("OpenAI returned content is not valid JSON format, returning raw text")
                return {"raw_text": content}
            
        except Exception as e:
            logger.error(f"OpenAI image analysis failed: {e}")
            return {"error": str(e)}


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM实现"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229", temperature: float = 0.7, max_tokens: int = 4000):
        """初始化Anthropic LLM
        
        Args:
            api_key: Anthropic API密钥
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def analyze_image(self, image_path: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """使用Anthropic Claude分析图像"""
        try:
            # 读取图像并转换为base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 构建请求
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # 发送请求
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            content = result["content"][0]["text"]
            
            # 尝试解析JSON响应
            import json
            try:
                # 尝试从文本中提取JSON部分
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start >= 0 and json_end >= 0:
                    json_str = content[json_start:json_end+1]
                    parsed_content = json.loads(json_str)
                    return parsed_content
                else:
                    return {"raw_text": content}
            except json.JSONDecodeError:
                logger.warning("Claude返回的内容不是有效的JSON格式，返回原始文本")
                return {"raw_text": content}
            
        except Exception as e:
            logger.error(f"Anthropic Claude分析图像失败: {e}")
            return {"error": str(e)}


class LocalLLM(BaseLLM):
    """Local LLM implementation"""
    
    def __init__(self, model_path: str, temperature: float = 0.7, max_tokens: int = 4000):
        """Initialize local LLM
        
        Args:
            model_path: Model path
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
        """
        self.model_path = model_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        # This can be implemented based on the actual local model framework
        # Such as llama.cpp, transformers, etc.
        self.model = None
        logger.warning("Local LLM functionality needs to be implemented based on the actual model framework")
    
    def analyze_image(self, image_path: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Analyze image using local LLM"""
        # This needs to be implemented based on the actual local model framework
        # Due to the diversity of local models, only a sample framework is provided here
        logger.warning("Local LLM image analysis functionality needs to be implemented based on the actual model framework")
        return {"error": "Local LLM functionality not yet implemented"}


class OllamaLLM(BaseLLM):
    """Ollama LLM implementation"""
    
    def __init__(self, model: str = "llava", temperature: float = 0.7, max_tokens: int = 4000, host: str = "http://localhost:11434"):
        """Initialize Ollama LLM
        
        Args:
            model: Model name in Ollama
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
            host: Ollama API host URL
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.host = host
        self.api_url = f"{host}/api"
        
        try:
            import ollama
            self.client = ollama.Client(host=host)
            logger.info(f"Ollama client initialized with host: {host}")
        except ImportError:
            logger.error("Failed to import ollama. Please install it with 'pip install ollama'")
            self.client = None
    
    def analyze_image(self, image_path: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Analyze image using Ollama LLM"""
        if self.client is None:
            return {"error": "Ollama client not initialized. Please install ollama package."}
        
        try:
            # Read image and encode as base64
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Create messages for the chat request
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": user_prompt,
                    "images": [image_data]
                }
            ]
            
            # Call Ollama API
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response["message"]["content"]
            
            # Try to parse JSON response
            import json
            try:
                # Try to extract JSON part from the text
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start >= 0 and json_end >= 0:
                    json_str = content[json_start:json_end+1]
                    parsed_content = json.loads(json_str)
                    return parsed_content
                else:
                    return {"raw_text": content}
            except json.JSONDecodeError:
                logger.warning("Ollama returned content is not valid JSON format, returning raw text")
                return {"raw_text": content}
            
        except Exception as e:
            logger.error(f"Ollama image analysis failed: {e}")
            return {"error": str(e)}


class LLMManager:
    """LLM Manager for selecting and using different LLMs"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize LLM Manager
        
        Args:
            config: LLM configuration dictionary
        """
        self.config = config
        self.llm = None
        self.provider = config.get("provider", "openai")
        self.initialize_llm()
    
    def initialize_llm(self) -> bool:
        """Initialize LLM
        
        Returns:
            bool: Whether initialization was successful
        """
        try:
            if self.provider == "openai":
                self.llm = OpenAILLM(
                    api_key=self.config.get("api_key", ""),
                    model=self.config.get("model", "gpt-4-vision-preview"),
                    temperature=self.config.get("temperature", 0.7),
                    max_tokens=self.config.get("max_tokens", 4000)
                )
                logger.info(f"Initialized OpenAI LLM (model: {self.config.get('model')})")
                
            elif self.provider == "anthropic":
                self.llm = AnthropicLLM(
                    api_key=self.config.get("api_key", ""),
                    model=self.config.get("model", "claude-3-opus-20240229"),
                    temperature=self.config.get("temperature", 0.7),
                    max_tokens=self.config.get("max_tokens", 4000)
                )
                logger.info(f"Initialized Anthropic Claude LLM (model: {self.config.get('model')})")
                
            elif self.provider == "ollama":
                self.llm = OllamaLLM(
                    model=self.config.get("model", "llava"),
                    temperature=self.config.get("temperature", 0.7),
                    max_tokens=self.config.get("max_tokens", 4000),
                    host=self.config.get("ollama_url", "http://localhost:11434")
                )
                logger.info(f"Initialized Ollama LLM (model: {self.config.get('model')})")
                
            elif self.provider == "local":
                self.llm = LocalLLM(
                    model_path=self.config.get("local_model_path", ""),
                    temperature=self.config.get("temperature", 0.7),
                    max_tokens=self.config.get("max_tokens", 4000)
                )
                logger.info(f"Initialized Local LLM (model path: {self.config.get('local_model_path')})")
                
            else:
                logger.error(f"Unsupported LLM provider: {self.provider}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return False
    
    def change_provider(self, provider: str, config: Dict[str, Any] = None) -> bool:
        """Change LLM provider
        
        Args:
            provider: Provider name (openai, anthropic, ollama, local)
            config: New configuration dictionary
            
        Returns:
            bool: Whether the change was successful
        """
        if config is not None:
            self.config.update(config)
        
        self.provider = provider
        return self.initialize_llm()
    
    def analyze_asset(self, image_path: str, template_info: str, additional_prompt: str = "") -> Dict[str, Any]:
        """Analyze laboratory asset
        
        Args:
            image_path: Image file path
            template_info: elabFTW template information
            additional_prompt: Additional prompt information
            
        Returns:
            Dict: Structured analysis result
        """
        if self.llm is None:
            if not self.initialize_llm():
                return {"error": "LLM not initialized"}
        
        # Build system prompt
        system_prompt = f"""
        You are a professional laboratory asset analysis assistant. Your task is to analyze laboratory equipment or items in the image and provide detailed structured information for the asset management system.
        
        IMPORTANT: The most critical field is the asset name. You MUST carefully identify the exact name of the chemical, equipment, or item from the image. Look for labels, markings, or text on the item itself. The name should be specific (e.g., "Hydrofluoric Acid" rather than just "Acid", or "K-Type Thermocouple" rather than just "Thermocouple").
        
        Your response MUST follow this two-part structure:
        1. FIRST, provide a summary section with ONLY the asset name and type at the very beginning of your JSON response, like this:
           "summary": {{
             "asset_name": "[Exact name of the asset]",
             "asset_type": "[Type of asset: chemical/equipment/tool/etc.]"
           }},
        
        2. THEN, provide the complete detailed information according to the following template format:
        
        {template_info}
        
        Please ensure your answer is in JSON format and includes both the summary section AND all necessary detailed fields. If some information cannot be obtained from the image, please mark it as "unknown" or provide the most reasonable guess. The asset name in both the summary and detailed sections MUST match and be accurate - this is your highest priority.
        """
        
        # Build user prompt
        user_prompt = f"""
        Please analyze the laboratory equipment or item in this image and provide detailed information according to the template in the system prompt.
        Remember to FIRST provide the summary section with the asset name and type, THEN provide the complete detailed information.
        Pay special attention to accurately identifying the asset name from any visible labels, markings, or text on the item.
        {additional_prompt}
        """
        
        # Call LLM to analyze the image
        result = self.llm.analyze_image(image_path, system_prompt, user_prompt)
        
        return result
    
    def get_settings(self) -> Dict[str, Any]:
        """获取LLM设置
        
        Returns:
            Dict: LLM设置信息
        """
        return {
            "provider": self.provider,
            "model": self.config.get("model", ""),
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4000),
            "api_key_configured": bool(self.config.get("api_key", "")),
            "ollama_url": self.config.get("ollama_url", "http://localhost:11434"),
            "local_model_path": self.config.get("local_model_path", ""),
            "status": "initialized" if self.llm else "not_initialized"
        }
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """更新LLM设置
        
        Args:
            settings: 新的设置
            
        Returns:
            Dict: 更新结果
        """
        try:
            # 更新配置
            old_provider = self.provider
            
            if "provider" in settings:
                self.provider = settings["provider"]
            if "model" in settings:
                self.config["model"] = settings["model"]
            if "temperature" in settings:
                self.config["temperature"] = settings["temperature"]
            if "max_tokens" in settings:
                self.config["max_tokens"] = settings["max_tokens"]
            if "api_key" in settings:
                self.config["api_key"] = settings["api_key"]
            if "ollama_url" in settings:
                self.config["ollama_url"] = settings["ollama_url"]
            if "local_model_path" in settings:
                self.config["local_model_path"] = settings["local_model_path"]
            
            # 如果提供商改变了，重新初始化LLM
            if old_provider != self.provider or "api_key" in settings:
                success = self.initialize_llm()
                if not success:
                    return {"success": False, "error": "Failed to initialize LLM with new settings"}
            
            return {
                "success": True,
                "message": "Settings updated successfully",
                "current_settings": self.get_settings()
            }
            
        except Exception as e:
            logger.error(f"Error updating LLM settings: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_image(self, image_data: bytes, additional_prompt: str = "") -> Dict[str, Any]:
        """分析图像数据
        
        Args:
            image_data: 图像二进制数据
            additional_prompt: 额外的提示信息
            
        Returns:
            Dict: 分析结果
        """
        if self.llm is None:
            if not self.initialize_llm():
                return {"error": "LLM not initialized"}
        
        try:
            # 将图像数据保存为临时文件
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                temp_path = temp_file.name
            
            try:
                # 使用现有的analyze_asset方法
                result = self.analyze_asset(temp_path, "", additional_prompt)
                return result
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error analyzing image data: {e}")
            return {"error": str(e)}