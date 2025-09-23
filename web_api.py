#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lab Asset Manager Web API Server

独立的Web API服务器，复用现有的后端模块，为Web前端提供RESTful API接口。
与PyQt5 GUI共享相同的后端处理代码，但可以独立运行。
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import base64
import io
from PIL import Image

# 确保可以导入项目模块
if '' in sys.path:
    sys.path.remove('')

# 导入项目模块
from camera.camera_manager import CameraManager
from llm.llm_manager import LLMManager
from elabftw.elab_manager import ElabManager
from qrcode_module.qrcode_generator import QRCodeGenerator
from config import ConfigManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'lab_asset_manager_secret_key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局管理器实例
config_manager = None
camera_manager = None
llm_manager = None
elab_manager = None
qrcode_generator = None

def initialize_managers():
    """初始化所有管理器"""
    global config_manager, camera_manager, llm_manager, elab_manager, qrcode_generator
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        logger.info("Configuration manager initialized")
        
        # 初始化相机管理器
        config = config_manager.load_config()
        camera_config = config.get("camera", {})
        camera_manager = CameraManager(
            device_id=0,
            resolution=tuple(camera_config.get("resolution", [1280, 720]))
        )
        logger.info("Camera manager initialized")
        
        # 初始化LLM管理器
        config = config_manager.load_config()
        llm_manager = LLMManager(config.get("llm", {}))
        logger.info("LLM manager initialized")
        
        # 初始化ELabFTW管理器
        config = config_manager.load_config()
        elab_config = config.get("elabftw", {})
        elab_manager = ElabManager(
            api_url=elab_config.get("api_url", ""),
            api_key=elab_config.get("api_key", ""),
            verify_ssl=elab_config.get("verify_ssl", False)
        )
        logger.info("ELabFTW manager initialized")
        
        # 初始化二维码生成器
        config = config_manager.load_config()
        qrcode_config = config.get("storage", {})
        qrcode_generator = QRCodeGenerator(
            output_dir=qrcode_config.get("qrcode_dir", "qrcodes")
        )
        logger.info("QR code generator initialized")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize managers: {e}")
        return False

# API路由

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'camera': camera_manager is not None,
            'llm': llm_manager is not None,
            'elab': elab_manager is not None,
            'qrcode': qrcode_generator is not None
        }
    })

# 相机相关API
@app.route('/api/camera/status', methods=['GET'])
def get_camera_status():
    """获取相机状态"""
    try:
        if not camera_manager:
            return jsonify({'error': 'Camera manager not initialized'}), 500
        
        status = camera_manager.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/capture', methods=['POST'])
def capture_image():
    """捕获图像"""
    try:
        if not camera_manager:
            return jsonify({'error': 'Camera manager not initialized'}), 500
        
        # 捕获图像
        image_path = camera_manager.capture_image()
        
        if image_path:
            return jsonify({
                'success': True,
                'image_path': str(image_path),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to capture image'}), 500
            
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/settings', methods=['GET'])
def get_camera_settings():
    """获取相机设置"""
    try:
        if not camera_manager:
            return jsonify({'error': 'Camera manager not initialized'}), 500
        
        settings = camera_manager.get_settings()
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error getting camera settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/settings', methods=['POST'])
def update_camera_settings():
    """更新相机设置"""
    try:
        if not camera_manager:
            return jsonify({'error': 'Camera manager not initialized'}), 500
        
        settings = request.json
        result = camera_manager.update_settings(settings)
        
        if result:
            return jsonify({'success': True, 'message': 'Settings updated'})
        else:
            return jsonify({'error': 'Failed to update settings'}), 500
            
    except Exception as e:
        logger.error(f"Error updating camera settings: {e}")
        return jsonify({'error': str(e)}), 500

# LLM相关API
@app.route('/api/llm/analyze', methods=['POST'])
def analyze_image():
    """分析图像"""
    try:
        if not llm_manager:
            return jsonify({'error': 'LLM manager not initialized'}), 500
        
        # 获取图像数据
        if 'image' in request.files:
            # 文件上传
            image_file = request.files['image']
            image_data = image_file.read()
            # 分析图像
            analysis_result = llm_manager.analyze_image(image_data)
        elif 'image_path' in request.json:
            # 图像路径
            image_path = request.json['image_path']
            # 分析图像
            analysis_result = llm_manager.analyze_asset(image_path)
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/llm/settings', methods=['GET'])
def get_llm_settings():
    """获取LLM设置"""
    try:
        if not llm_manager:
            return jsonify({'error': 'LLM manager not initialized'}), 500
        
        # 获取LLM设置
        settings = llm_manager.get_settings()
        
        return jsonify({
            'success': True,
            'settings': settings,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting LLM settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/llm/settings', methods=['POST'])
def update_llm_settings():
    """更新LLM设置"""
    try:
        if not llm_manager:
            return jsonify({'error': 'LLM manager not initialized'}), 500
        
        settings = request.json
        if not settings:
            return jsonify({'error': 'No settings provided'}), 400
        
        # 更新LLM设置
        result = llm_manager.update_settings(settings)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating LLM settings: {e}")
        return jsonify({'error': str(e)}), 500

# ELabFTW相关API
@app.route('/api/elab/settings', methods=['GET'])
def get_elab_settings():
    """获取ELabFTW设置"""
    try:
        if not elab_manager:
            return jsonify({'error': 'ELab manager not initialized'}), 500
        
        # 获取ELabFTW设置
        settings = elab_manager.get_settings()
        
        return jsonify({
            'success': True,
            'settings': settings,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting ELab settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/elab/settings', methods=['POST'])
def update_elab_settings():
    """更新ELabFTW设置"""
    try:
        if not elab_manager:
            return jsonify({'error': 'ELab manager not initialized'}), 500
        
        settings = request.json
        if not settings:
            return jsonify({'error': 'No settings provided'}), 400
        
        # 更新ELabFTW设置
        result = elab_manager.update_settings(settings)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating ELab settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/elab/templates', methods=['GET'])
def get_elab_templates():
    """获取ELabFTW模板"""
    try:
        if not elab_manager:
            return jsonify({'error': 'ELabFTW manager not initialized'}), 500
        
        templates = elab_manager.get_templates()
        return jsonify(templates)
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/elab/items', methods=['GET'])
def get_elab_items():
    """获取ELabFTW物品列表"""
    try:
        if not elab_manager:
            return jsonify({'error': 'ELabFTW manager not initialized'}), 500
        
        items = elab_manager.get_items()
        return jsonify(items)
    except Exception as e:
        logger.error(f"Error getting items: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/elab/items', methods=['POST'])
def create_elab_item():
    """创建ELabFTW物品"""
    try:
        if not elab_manager:
            return jsonify({'error': 'ELabFTW manager not initialized'}), 500
        
        item_data = request.json
        result = elab_manager.create_item(item_data)
        
        return jsonify({
            'success': True,
            'item_id': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/elab/items/<int:item_id>', methods=['PUT'])
def update_elab_item(item_id):
    """更新ELabFTW物品"""
    try:
        if not elab_manager:
            return jsonify({'error': 'ELabFTW manager not initialized'}), 500
        
        item_data = request.json
        result = elab_manager.update_item(item_id, item_data)
        
        return jsonify({
            'success': True,
            'updated': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating item: {e}")
        return jsonify({'error': str(e)}), 500

# 二维码相关API
@app.route('/api/qrcode/generate', methods=['POST'])
def generate_qrcode():
    """生成二维码"""
    try:
        if not qrcode_generator:
            return jsonify({'error': 'QR code generator not initialized'}), 500
        
        data = request.json
        qr_data = data.get('data', '')
        filename = data.get('filename', f'qrcode_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        # 生成二维码
        qr_path = qrcode_generator.generate_qrcode(qr_data, filename)
        
        return jsonify({
            'success': True,
            'qr_path': str(qr_path),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/qrcode/<filename>')
def serve_qrcode(filename):
    """提供二维码文件"""
    try:
        qr_path = Path('qrcodes') / filename
        if qr_path.exists():
            return send_file(qr_path)
        else:
            return jsonify({'error': 'QR code not found'}), 404
    except Exception as e:
        logger.error(f"Error serving QR code: {e}")
        return jsonify({'error': str(e)}), 500

# Socket.IO事件处理
@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    logger.info('Client connected')
    emit('status', {'message': 'Connected to Lab Asset Manager API'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    logger.info('Client disconnected')

@socketio.on('camera_start')
def handle_camera_start():
    """开始相机流"""
    try:
        if camera_manager:
            camera_manager.start_stream()
            emit('camera_status', {'status': 'started'})
    except Exception as e:
        logger.error(f"Error starting camera: {e}")
        emit('error', {'message': str(e)})

@socketio.on('camera_stop')
def handle_camera_stop():
    """停止相机流"""
    try:
        if camera_manager:
            camera_manager.stop_stream()
            emit('camera_status', {'status': 'stopped'})
    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    # 初始化管理器
    if initialize_managers():
        logger.info("Starting Lab Asset Manager Web API Server...")
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        logger.error("Failed to initialize managers. Exiting.")
        sys.exit(1)