#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""User Interface Module - Main Window

Implements the system's main window and user interaction functionality.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Import PyQt5
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit, QFileDialog,
    QMessageBox, QTabWidget, QFrame, QSplitter, QProgressBar, QCheckBox,
    QGroupBox, QFormLayout, QSpinBox, QDialog, QDialogButtonBox, QListWidget,
    QTextBrowser
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, pyqtSlot, QThread

# Import custom modules
from camera.camera_manager import CameraManager
from llm.llm_manager import LLMManager
from elabftw.elab_manager import ElabManager
from qrcode_module.qrcode_generator import QRCodeGenerator
from config import ConfigManager

logger = logging.getLogger(__name__)


class CameraThread(QThread):
    """Camera thread for updating camera preview in the background"""
    
    # Define signals
    frame_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, camera_manager):
        super().__init__()
        self.camera_manager = camera_manager
        self.running = False
    
    def run(self):
        """Thread run function"""
        self.running = True
        while self.running:
            try:
                # Read a frame
                frame = self.camera_manager.read_frame()
                if frame is not None:
                    # Send frame signal
                    self.frame_ready.emit(frame)
                else:
                    # Send error signal
                    error = self.camera_manager.get_last_error()
                    self.error_occurred.emit(error or "Failed to read camera frame")
                    # Short pause before retry
                    time.sleep(1)
                
                # Control frame rate
                time.sleep(0.03)  # About 30fps
                
            except Exception as e:
                self.error_occurred.emit(f"Camera thread exception: {e}")
                time.sleep(1)
    
    def stop(self):
        """Stop thread"""
        self.running = False
        self.wait()


class LLMProcessThread(QThread):
    """LLM processing thread for background image analysis"""
    
    # Define signals
    result_ready = pyqtSignal(dict)
    progress_update = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, llm_manager, image_path, template_info, additional_prompt=""):
        super().__init__()
        self.llm_manager = llm_manager
        self.image_path = image_path
        self.template_info = template_info
        self.additional_prompt = additional_prompt
    
    def run(self):
        """Thread run function"""
        try:
            # Update progress
            self.progress_update.emit(10, "Preparing image analysis...")
            
            # Analyze image
            self.progress_update.emit(30, "Analyzing image with LLM...")
            result = self.llm_manager.analyze_asset(
                self.image_path,
                self.template_info,
                self.additional_prompt
            )
            
            # Check result
            if "error" in result:
                self.error_occurred.emit(f"LLM analysis failed: {result['error']}")
                return
            
            # Update progress
            self.progress_update.emit(90, "Analysis complete, processing results...")
            
            # Send result signal
            self.result_ready.emit(result)
            
            # Complete
            self.progress_update.emit(100, "Analysis complete")
            
        except Exception as e:
            self.error_occurred.emit(f"LLM processing thread exception: {e}")


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # LLM settings tab
        llm_tab = QWidget()
        llm_layout = QFormLayout(llm_tab)
        
        # LLM provider selection
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["OpenAI", "Anthropic", "Ollama", "Azure OpenAI", "Google AI", "Local Model"])
        current_provider = self.config["llm"]["provider"]
        if current_provider == "openai":
            self.llm_provider_combo.setCurrentIndex(0)
        elif current_provider == "anthropic":
            self.llm_provider_combo.setCurrentIndex(1)
        elif current_provider == "ollama":
            self.llm_provider_combo.setCurrentIndex(2)
        elif current_provider == "azure":
            self.llm_provider_combo.setCurrentIndex(3)
        elif current_provider == "google":
            self.llm_provider_combo.setCurrentIndex(4)
        elif current_provider == "local":
            self.llm_provider_combo.setCurrentIndex(5)
        self.llm_provider_combo.currentIndexChanged.connect(self.on_llm_provider_changed)
        llm_layout.addRow("LLM Provider:", self.llm_provider_combo)
        
        # Model selection group box
        model_group = QGroupBox("Model Selection")
        model_group_layout = QVBoxLayout(model_group)
        
        # OpenAI models
        self.openai_model_combo = QComboBox()
        self.openai_model_combo.addItems(["gpt-4-vision-preview", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"])
        if current_provider == "openai":
            self.openai_model_combo.setCurrentText(self.config["llm"]["model"])
        model_group_layout.addWidget(QLabel("OpenAI Models:"))
        model_group_layout.addWidget(self.openai_model_combo)
        
        # Anthropic models
        self.anthropic_model_combo = QComboBox()
        self.anthropic_model_combo.addItems(["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-2.1"])
        if current_provider == "anthropic":
            self.anthropic_model_combo.setCurrentText(self.config["llm"]["model"])
        model_group_layout.addWidget(QLabel("Anthropic Models:"))
        model_group_layout.addWidget(self.anthropic_model_combo)
        
        # Ollama models
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.addItems(["llava", "llava:13b", "bakllava", "llava-llama3"])
        self.ollama_model_combo.setEditable(True)
        if current_provider == "ollama":
            self.ollama_model_combo.setCurrentText(self.config["llm"]["model"])
        model_group_layout.addWidget(QLabel("Ollama Models:"))
        model_group_layout.addWidget(self.ollama_model_combo)
        
        # Azure OpenAI models
        self.azure_model_combo = QComboBox()
        self.azure_model_combo.addItems(["gpt-4-vision", "gpt-4", "gpt-4-turbo", "gpt-35-turbo"])
        self.azure_model_combo.setEditable(True)
        if current_provider == "azure":
            self.azure_model_combo.setCurrentText(self.config["llm"].get("model", "gpt-4-vision"))
        model_group_layout.addWidget(QLabel("Azure OpenAI Models:"))
        model_group_layout.addWidget(self.azure_model_combo)
        
        # Google AI models
        self.google_model_combo = QComboBox()
        self.google_model_combo.addItems(["gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"])
        self.google_model_combo.setEditable(True)
        if current_provider == "google":
            self.google_model_combo.setCurrentText(self.config["llm"].get("model", "gemini-pro-vision"))
        model_group_layout.addWidget(QLabel("Google AI Models:"))
        model_group_layout.addWidget(self.google_model_combo)
        
        llm_layout.addRow("", model_group)
        
        # API key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(self.config["llm"]["api_key"])
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        llm_layout.addRow("API Key:", self.api_key_edit)
        
        # Model name
        self.model_edit = QLineEdit()
        self.model_edit.setText(self.config["llm"]["model"])
        llm_layout.addRow("Model Name:", self.model_edit)
        
        # Ollama URL
        self.ollama_url_edit = QLineEdit()
        self.ollama_url_edit.setText(self.config["llm"].get("ollama_url", "http://localhost:11434"))
        llm_layout.addRow("Ollama URL:", self.ollama_url_edit)
        
        # Local model path
        self.local_model_path_edit = QLineEdit()
        self.local_model_path_edit.setText(self.config["llm"]["local_model_path"])
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_local_model)
        local_model_layout = QHBoxLayout()
        local_model_layout.addWidget(self.local_model_path_edit)
        local_model_layout.addWidget(self.browse_button)
        llm_layout.addRow("Local Model Path:", local_model_layout)
        
        # Temperature parameter
        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 100)
        self.temperature_spin.setValue(int(self.config["llm"]["temperature"] * 100))
        self.temperature_spin.setSuffix("%")
        llm_layout.addRow("Temperature:", self.temperature_spin)
        
        # Max tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 10000)
        self.max_tokens_spin.setSingleStep(100)
        self.max_tokens_spin.setValue(self.config["llm"]["max_tokens"])
        llm_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        # elabFTW settings tab
        elab_tab = QWidget()
        elab_layout = QVBoxLayout(elab_tab)
        
        # Connection group
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QFormLayout(connection_group)
        
        # Server address
        server_layout = QHBoxLayout()
        self.server_protocol_combo = QComboBox()
        self.server_protocol_combo.addItems(["https://", "http://"])
        
        # Extract protocol and server from API URL
        api_url = self.config["elabftw"]["api_url"]
        server_address = ""
        if api_url.startswith("https://"):
            self.server_protocol_combo.setCurrentIndex(0)
            server_address = api_url[8:].split("/api")[0]
        elif api_url.startswith("http://"):
            self.server_protocol_combo.setCurrentIndex(1)
            server_address = api_url[7:].split("/api")[0]
        
        self.server_address_edit = QLineEdit()
        self.server_address_edit.setText(server_address)
        self.server_address_edit.setPlaceholderText("example.elabftw.net or IP:port")
        
        server_layout.addWidget(self.server_protocol_combo)
        server_layout.addWidget(self.server_address_edit)
        connection_layout.addRow("Server Address:", server_layout)
        
        # API path
        self.api_path_edit = QLineEdit()
        self.api_path_edit.setText("/api/v2")
        self.api_path_edit.setPlaceholderText("/api/v2")
        connection_layout.addRow("API Path:", self.api_path_edit)
        
        # API Key
        self.elab_api_key_edit = QLineEdit()
        self.elab_api_key_edit.setText(self.config["elabftw"]["api_key"])
        self.elab_api_key_edit.setEchoMode(QLineEdit.Password)
        self.elab_api_key_edit.setPlaceholderText("Enter your elabFTW API key")
        connection_layout.addRow("API Key:", self.elab_api_key_edit)
        
        # Verify SSL
        self.verify_ssl_check = QCheckBox("Verify SSL Certificate")
        self.verify_ssl_check.setChecked(self.config["elabftw"]["verify_ssl"])
        connection_layout.addRow("", self.verify_ssl_check)
        
        # Test connection button
        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self.test_elab_connection)
        connection_layout.addRow("", self.test_connection_button)
        
        elab_layout.addWidget(connection_group)
        
        # Templates group
        templates_group = QGroupBox("Templates Settings")
        templates_layout = QVBoxLayout(templates_group)
        
        # Refresh templates button
        self.refresh_templates_button = QPushButton("Refresh Templates")
        self.refresh_templates_button.clicked.connect(self.refresh_templates)
        templates_layout.addWidget(self.refresh_templates_button)
        
        # Templates list
        self.templates_list = QListWidget()
        templates_layout.addWidget(self.templates_list)
        
        elab_layout.addWidget(templates_group)
        
        # Camera settings tab
        camera_tab = QWidget()
        camera_layout = QFormLayout(camera_tab)
        
        # Auto start camera
        self.auto_start_camera_check = QCheckBox("Auto start camera when application launches")
        self.auto_start_camera_check.setChecked(self.config.get("camera", {}).get("auto_start", True))
        camera_layout.addRow("", self.auto_start_camera_check)
        
        # Resolution
        resolution_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(320, 3840)
        self.width_spin.setSingleStep(10)
        self.width_spin.setValue(self.config["camera"]["resolution"][0])
        self.height_spin = QSpinBox()
        self.height_spin.setRange(240, 2160)
        self.height_spin.setSingleStep(10)
        self.height_spin.setValue(self.config["camera"]["resolution"][1])
        resolution_layout.addWidget(self.width_spin)
        resolution_layout.addWidget(QLabel("x"))
        resolution_layout.addWidget(self.height_spin)
        camera_layout.addRow("Resolution:", resolution_layout)
        
        # Auto focus
        self.auto_focus_check = QCheckBox("Enable Auto Focus")
        self.auto_focus_check.setChecked(self.config["camera"]["auto_focus"])
        camera_layout.addRow("", self.auto_focus_check)
        
        # Capture delay
        self.capture_delay_spin = QSpinBox()
        self.capture_delay_spin.setRange(0, 10)
        self.capture_delay_spin.setValue(self.config["camera"]["capture_delay"])
        self.capture_delay_spin.setSuffix(" sec")
        camera_layout.addRow("Capture Delay:", self.capture_delay_spin)
        
        # Add tabs
        tab_widget.addTab(llm_tab, "LLM Settings")
        tab_widget.addTab(elab_tab, "elabFTW Settings")
        tab_widget.addTab(camera_tab, "Camera Settings")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Update UI based on current LLM provider
        self.on_llm_provider_changed()
    
    def on_llm_provider_changed(self):
        """Handle LLM provider change"""
        provider_index = self.llm_provider_combo.currentIndex()
        
        # Update UI element visibility
        if provider_index == 0:  # OpenAI
            self.api_key_edit.setEnabled(True)
            self.local_model_path_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.ollama_url_edit.setEnabled(False)
            self.openai_model_combo.setVisible(True)
            self.anthropic_model_combo.setVisible(False)
            self.ollama_model_combo.setVisible(False)
            self.azure_model_combo.setVisible(False)
            self.google_model_combo.setVisible(False)
            self.model_edit.setText(self.openai_model_combo.currentText())
        elif provider_index == 1:  # Anthropic
            self.api_key_edit.setEnabled(True)
            self.local_model_path_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.ollama_url_edit.setEnabled(False)
            self.openai_model_combo.setVisible(False)
            self.anthropic_model_combo.setVisible(True)
            self.ollama_model_combo.setVisible(False)
            self.azure_model_combo.setVisible(False)
            self.google_model_combo.setVisible(False)
            self.model_edit.setText(self.anthropic_model_combo.currentText())
        elif provider_index == 2:  # Ollama
            self.api_key_edit.setEnabled(False)
            self.local_model_path_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.ollama_url_edit.setEnabled(True)
            self.openai_model_combo.setVisible(False)
            self.anthropic_model_combo.setVisible(False)
            self.ollama_model_combo.setVisible(True)
            self.azure_model_combo.setVisible(False)
            self.google_model_combo.setVisible(False)
            self.model_edit.setText(self.ollama_model_combo.currentText())
        elif provider_index == 3:  # Azure OpenAI
            self.api_key_edit.setEnabled(True)
            self.local_model_path_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.ollama_url_edit.setEnabled(False)
            self.openai_model_combo.setVisible(False)
            self.anthropic_model_combo.setVisible(False)
            self.ollama_model_combo.setVisible(False)
            self.azure_model_combo.setVisible(True)
            self.google_model_combo.setVisible(False)
            self.model_edit.setText(self.azure_model_combo.currentText())
        elif provider_index == 4:  # Google AI
            self.api_key_edit.setEnabled(True)
            self.local_model_path_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.ollama_url_edit.setEnabled(False)
            self.openai_model_combo.setVisible(False)
            self.anthropic_model_combo.setVisible(False)
            self.ollama_model_combo.setVisible(False)
            self.azure_model_combo.setVisible(False)
            self.google_model_combo.setVisible(True)
            self.model_edit.setText(self.google_model_combo.currentText())
        elif provider_index == 5:  # Local model
            self.api_key_edit.setEnabled(False)
            self.local_model_path_edit.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.ollama_url_edit.setEnabled(False)
            self.openai_model_combo.setVisible(False)
            self.anthropic_model_combo.setVisible(False)
            self.ollama_model_combo.setVisible(False)
            self.azure_model_combo.setVisible(False)
            self.google_model_combo.setVisible(False)
    
    def browse_local_model(self):
        """Browse local model file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Model File", "", "Model Files (*.bin *.gguf *.ggml);;All Files (*)"
        )
        if file_path:
            self.local_model_path_edit.setText(file_path)
    
    def test_elab_connection(self):
        """Test connection to elabFTW server"""
        try:
            # Get current settings
            protocol = self.server_protocol_combo.currentText()
            server = self.server_address_edit.text()
            api_path = self.api_path_edit.text()
            api_url = f"{protocol}{server}{api_path}"
            api_key = self.elab_api_key_edit.text()
            verify_ssl = self.verify_ssl_check.isChecked()
            
            # Create temporary ElabManager to test connection
            from elabftw.elab_manager import ElabManager
            temp_elab_manager = ElabManager(api_url, api_key, verify_ssl)
            
            # Try to get templates as a connection test
            templates = temp_elab_manager.get_item_templates()
            
            # Update templates list
            self.templates_list.clear()
            for template in templates:
                self.templates_list.addItem(f"{template['id']}: {template['title']}")
            
            # Show success message
            QMessageBox.information(self, "Connection Test", 
                                   f"Successfully connected to elabFTW server.\n\nFound {len(templates)} templates.")
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Test Failed", 
                                f"Failed to connect to elabFTW server: {str(e)}")
    
    def refresh_templates(self):
        """Refresh templates list"""
        try:
            # Get current settings
            protocol = self.server_protocol_combo.currentText()
            server = self.server_address_edit.text()
            api_path = self.api_path_edit.text()
            api_url = f"{protocol}{server}{api_path}"
            api_key = self.elab_api_key_edit.text()
            verify_ssl = self.verify_ssl_check.isChecked()
            
            # Create temporary ElabManager to get templates
            from elabftw.elab_manager import ElabManager
            temp_elab_manager = ElabManager(api_url, api_key, verify_ssl)
            
            # Get templates
            templates = temp_elab_manager.get_item_templates()
            
            # Update templates list
            self.templates_list.clear()
            for template in templates:
                self.templates_list.addItem(f"{template['id']}: {template['title']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Refresh Templates Failed", 
                                f"Failed to refresh templates: {str(e)}")
    
    def get_config(self):
        """Get updated configuration"""
        # Get LLM provider
        provider_index = self.llm_provider_combo.currentIndex()
        if provider_index == 0:
            provider = "openai"
            model = self.openai_model_combo.currentText()
        elif provider_index == 1:
            provider = "anthropic"
            model = self.anthropic_model_combo.currentText()
        elif provider_index == 2:
            provider = "ollama"
            model = self.ollama_model_combo.currentText()
        elif provider_index == 3:  # Azure OpenAI
            provider = "azure"
            model = self.azure_model_combo.currentText()
        elif provider_index == 4:  # Google AI
            provider = "google"
            model = self.google_model_combo.currentText()
        else:
            provider = "local"
            model = ""
        
        # Update configuration
        config = self.config.copy()
        
        # LLM settings
        config["llm"]["provider"] = provider
        config["llm"]["api_key"] = self.api_key_edit.text()
        config["llm"]["model"] = model
        config["llm"]["local_model_path"] = self.local_model_path_edit.text()
        config["llm"]["ollama_url"] = self.ollama_url_edit.text()
        config["llm"]["temperature"] = self.temperature_spin.value() / 100.0
        config["llm"]["max_tokens"] = self.max_tokens_spin.value()
        
        # elabFTW settings
        protocol = self.server_protocol_combo.currentText()
        server = self.server_address_edit.text()
        api_path = self.api_path_edit.text()
        config["elabftw"]["api_url"] = f"{protocol}{server}{api_path}"
        config["elabftw"]["api_key"] = self.elab_api_key_edit.text()
        config["elabftw"]["verify_ssl"] = self.verify_ssl_check.isChecked()
        
        # Camera settings
        config["camera"]["resolution"] = [self.width_spin.value(), self.height_spin.value()]
        config["camera"]["auto_focus"] = self.auto_focus_check.isChecked()
        config["camera"]["capture_delay"] = self.capture_delay_spin.value()
        config["camera"]["auto_start"] = self.auto_start_camera_check.isChecked()
        
        return config


class ElabFTWInfoWindow(QDialog):
    """elabFTW Information Window"""
    
    def __init__(self, elab_manager, parent=None):
        super().__init__(parent)
        self.elab_manager = elab_manager
        self.setWindowTitle("elabFTW Information")
        self.resize(600, 400)
        self.init_ui()
        self.refresh_info()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Info display area
        self.info_browser = QTextBrowser()
        layout.addWidget(self.info_browser)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Information")
        refresh_btn.clicked.connect(self.refresh_info)
        layout.addWidget(refresh_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def refresh_info(self):
        """Refresh elabFTW information"""
        try:
            # Get server info
            info_html = "<h2>elabFTW Connection Information</h2>"
            info_html += f"<p><b>Server URL:</b> {self.elab_manager.api_url}</p>"
            info_html += f"<p><b>API Verification:</b> {'Enabled' if self.elab_manager.verify_ssl else 'Disabled'}</p>"
            
            # Get user info
            try:
                user_info = self.elab_manager.get_user_info()
                if user_info:
                    info_html += "<h3>User Information</h3>"
                    info_html += f"<p><b>Username:</b> {user_info.get('username', 'N/A')}</p>"
                    info_html += f"<p><b>Email:</b> {user_info.get('email', 'N/A')}</p>"
                    info_html += f"<p><b>Team:</b> {user_info.get('team', 'N/A')}</p>"
            except Exception as e:
                info_html += f"<p><b>User Information:</b> Could not retrieve (Error: {str(e)})</p>"
            
            # Get templates
            templates = self.elab_manager.get_item_templates()
            info_html += "<h3>Available Templates</h3>"
            info_html += "<ul>"
            for template in templates:
                info_html += f"<li>{template['id']}: {template['title']}</li>"
            info_html += "</ul>"
            
            self.info_browser.setHtml(info_html)
        except Exception as e:
            self.info_browser.setHtml(f"<h3>Error retrieving elabFTW information</h3><p>{str(e)}</p>")


class MainWindow(QMainWindow):
    """Main Window Class"""
    
    def __init__(self, camera_manager, llm_manager, elab_manager, qrcode_generator, config):
        super().__init__()
        
        # Save manager instances
        self.camera_manager = camera_manager
        self.llm_manager = llm_manager
        self.elab_manager = elab_manager
        self.qrcode_generator = qrcode_generator
        self.config = config
        self.config_manager = ConfigManager()
        
        # Status variables
        self.camera_thread = None
        self.llm_thread = None
        self.current_image_path = None
        self.current_llm_result = None
        self.current_asset_id = None
        
        # elabFTW info window
        self.elab_info_window = None
        
        # Initialize UI
        self.init_ui()
        
        # Start camera if auto_start is enabled
        if self.config.get("camera", {}).get("auto_start", True):
            self.start_camera()
    
    def init_ui(self):
        """Initialize UI"""
        # Set window properties
        self.setWindowTitle("Laboratory Asset Management System")
        self.setMinimumSize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Camera and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Camera preview
        self.camera_label = QLabel("Initializing camera...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("background-color: #000;")
        left_layout.addWidget(self.camera_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.camera_toggle_button = QPushButton("Start Camera")
        self.camera_toggle_button.setIcon(QIcon.fromTheme("camera-video"))
        self.camera_toggle_button.clicked.connect(self.toggle_camera)
        control_layout.addWidget(self.camera_toggle_button)
        
        self.capture_button = QPushButton("Capture Image")
        self.capture_button.setIcon(QIcon.fromTheme("camera-photo"))
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setEnabled(False)  # Disabled until camera is started
        control_layout.addWidget(self.capture_button)
        
        self.load_image_button = QPushButton("Load Image")
        self.load_image_button.setIcon(QIcon.fromTheme("document-open"))
        self.load_image_button.clicked.connect(self.load_image_from_file)
        control_layout.addWidget(self.load_image_button)
        
        self.analyze_button = QPushButton("Analyze Image")
        self.analyze_button.setIcon(QIcon.fromTheme("system-search"))
        self.analyze_button.clicked.connect(self.analyze_image)
        self.analyze_button.setEnabled(False)
        control_layout.addWidget(self.analyze_button)
        
        self.save_button = QPushButton("Save to elabFTW")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self.save_to_elabftw)
        self.save_button.setEnabled(False)
        control_layout.addWidget(self.save_button)
        
        left_layout.addLayout(control_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% %v/100")
        left_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        left_layout.addWidget(self.status_label)
        
        # Right panel - Analysis results and settings
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # Analysis results tab
        result_tab = QWidget()
        result_layout = QVBoxLayout(result_tab)
        
        # Template selection
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Select Template:"))
        self.template_combo = QComboBox()
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        template_layout.addWidget(self.template_combo)
        result_layout.addLayout(template_layout)
        
        # Analysis results
        result_layout.addWidget(QLabel("Analysis Results:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        # QR Code tab
        qrcode_tab = QWidget()
        qrcode_layout = QVBoxLayout(qrcode_tab)
        
        # QR Code preview
        self.qrcode_label = QLabel("QR Code will be displayed here")
        self.qrcode_label.setAlignment(Qt.AlignCenter)
        self.qrcode_label.setMinimumSize(200, 200)
        self.qrcode_label.setStyleSheet("background-color: #f0f0f0;")
        qrcode_layout.addWidget(self.qrcode_label)
        
        # QR Code controls
        qrcode_control_layout = QHBoxLayout()
        
        # We disable the generate QR code button as it will be auto-generated after saving to elabFTW
        self.generate_qrcode_button = QPushButton("Generate QR Code")
        self.generate_qrcode_button.clicked.connect(self.generate_qrcode)
        self.generate_qrcode_button.setEnabled(False)
        self.generate_qrcode_button.setVisible(False)  # Hide the button as it's no longer needed
        qrcode_control_layout.addWidget(self.generate_qrcode_button)
        
        self.save_qrcode_button = QPushButton("Save QR Code")
        self.save_qrcode_button.clicked.connect(self.save_qrcode)
        self.save_qrcode_button.setEnabled(False)
        qrcode_control_layout.addWidget(self.save_qrcode_button)
        
        qrcode_layout.addLayout(qrcode_control_layout)
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Settings button
        self.settings_button = QPushButton("Open Settings")
        self.settings_button.clicked.connect(self.open_settings)
        settings_layout.addWidget(self.settings_button)
        
        # elabFTW info button
        self.elab_info_button = QPushButton("View elabFTW Information")
        self.elab_info_button.clicked.connect(self.show_elab_info)
        settings_layout.addWidget(self.elab_info_button)
        
        # Add tabs
        tab_widget.addTab(result_tab, "Analysis Results")
        tab_widget.addTab(qrcode_tab, "QR Code")
        tab_widget.addTab(settings_tab, "Settings")
        
        right_layout.addWidget(tab_widget)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Load templates
        self.load_templates()
    
    def load_templates(self):
        """Load elabFTW templates"""
        try:
            # Get template list
            templates = self.elab_manager.get_item_templates()
            
            # Clear dropdown
            self.template_combo.clear()
            
            # Add templates
            for template in templates:
                self.template_combo.addItem(template["title"], template["id"])
            
            if templates:
                self.set_status(f"Loaded {len(templates)} templates")
            else:
                self.set_status("No templates found")
                
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            self.set_status(f"Failed to load templates: {e}")
    
    def on_template_changed(self):
        """Template change handler"""
        # If there are analysis results, re-analyze
        if self.current_image_path and self.current_llm_result:
            self.analyze_image()
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.camera_thread is None:
            # Camera is off, turn it on
            self.start_camera()
        else:
            # Camera is on, turn it off
            self.stop_camera()
    
    def start_camera(self):
        """Start camera"""
        try:
            # Initialize camera
            if not self.camera_manager.initialize():
                self.set_status(f"Camera initialization failed: {self.camera_manager.get_last_error()}")
                return
            
            # Create and start camera thread
            self.camera_thread = CameraThread(self.camera_manager)
            self.camera_thread.frame_ready.connect(self.update_camera_preview)
            self.camera_thread.error_occurred.connect(self.set_status)
            self.camera_thread.start()
            
            # Update UI
            self.camera_toggle_button.setText("Stop Camera")
            self.capture_button.setEnabled(True)
            self.set_status("Camera started")
            
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            self.set_status(f"Failed to start camera: {e}")
    
    def stop_camera(self):
        """Stop camera"""
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread = None
        
        self.camera_manager.release()
        
        # Update UI
        self.camera_toggle_button.setText("Start Camera")
        self.capture_button.setEnabled(False)
        self.camera_label.setText("Camera stopped")
        self.set_status("Camera stopped")
    
    @pyqtSlot(object)
    def update_camera_preview(self, frame):
        """Update camera preview"""
        try:
            # Convert OpenCV image format to Qt image format
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            
            # Resize image to fit the label
            pixmap = QPixmap.fromImage(q_img)
            pixmap = pixmap.scaled(self.camera_label.width(), self.camera_label.height(), 
                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Update label
            self.camera_label.setPixmap(pixmap)
            
        except Exception as e:
            logger.error(f"Failed to update camera preview: {e}")
    
    def load_image_from_file(self):
        """Load image from file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # Load the image
                import cv2
                image = cv2.imread(file_path)
                if image is None:
                    raise ValueError("Failed to load image")
                
                # Convert to RGB for display
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                h, w, c = image_rgb.shape
                q_image = QImage(image_rgb.data, w, h, w * c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.camera_label.setPixmap(pixmap.scaled(
                    self.camera_label.width(), 
                    self.camera_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                
                # Save the image path
                self.current_image_path = file_path
                
                # Enable analyze button
                self.analyze_button.setEnabled(True)
                
                self.set_status(f"Loaded image from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                self.set_status(f"Failed to load image: {e}")
    
    def capture_image(self):
        """Capture image from camera"""
        try:
            # Disable button
            self.capture_button.setEnabled(False)
            self.set_status("Capturing image...")
            
            # Create save directory
            image_dir = self.config["storage"]["image_dir"]
            Path(image_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(image_dir, f"asset_{timestamp}.jpg")
            
            # Capture image
            delay = self.config["camera"]["capture_delay"]
            success, result = self.camera_manager.capture_image(image_path, delay)
            
            if success:
                self.current_image_path = image_path
                self.set_status(f"Image saved: {image_path}")
                self.analyze_button.setEnabled(True)
                
                # 自动分析捕获的图像
                self.analyze_image()
            else:
                self.set_status(f"Image capture failed: {result}")
            
        except Exception as e:
            logger.error(f"Image capture exception: {e}")
            self.set_status(f"Image capture exception: {e}")
        finally:
            # Restore button
            self.capture_button.setEnabled(True)
    
    def analyze_image(self):
        """Analyze image"""
        if not self.current_image_path:
            self.set_status("Please capture an image first")
            return
        
        try:
            # Disable buttons
            self.analyze_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.generate_qrcode_button.setEnabled(False)
            self.save_qrcode_button.setEnabled(False)
            
            # Reset progress bar
            self.progress_bar.setValue(0)
            self.set_status("Preparing analysis...")
            
            # Get current template ID
            template_id = self.template_combo.currentData()
            if not template_id:
                self.set_status("Please select a template")
                self.analyze_button.setEnabled(True)
                return
            
            # Get template structure
            template_info = self.elab_manager.get_template_structure(template_id)
            
            # Create and start LLM processing thread
            self.llm_thread = LLMProcessThread(
                self.llm_manager,
                self.current_image_path,
                template_info
            )
            self.llm_thread.result_ready.connect(self.on_analysis_complete)
            self.llm_thread.progress_update.connect(self.update_progress)
            self.llm_thread.error_occurred.connect(self.set_status)
            self.llm_thread.start()
            
        except Exception as e:
            logger.error(f"Image analysis exception: {e}")
            self.set_status(f"Image analysis exception: {e}")
            self.analyze_button.setEnabled(True)
    
    @pyqtSlot(int, str)
    def update_progress(self, value, message):
        """Update progress"""
        self.progress_bar.setValue(value)
        self.set_status(message)
    
    @pyqtSlot(dict)
    def on_analysis_complete(self, result):
        """Handle analysis completion"""
        try:
            # Save result
            self.current_llm_result = result
            
            # Extract asset name for title if available
            self.update_asset_title_from_result(result)
            
            # Display result in editable format
            import json
            formatted_json = json.dumps(result, indent=2, ensure_ascii=False)
            self.result_text.setText(formatted_json)
            self.result_text.setReadOnly(False)  # Make the text editable
            
            # Connect text changed signal for real-time editing
            self.result_text.textChanged.connect(self.on_result_text_changed)
            
            # Enable buttons
            self.analyze_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.generate_qrcode_button.setEnabled(False)  # Need to save to elabFTW first
            
            self.set_status("Analysis complete, you can edit the results before saving")
            
        except Exception as e:
            logger.error(f"Error processing analysis result: {e}")
            self.set_status(f"Error processing analysis result: {e}")
            self.analyze_button.setEnabled(True)
    
    def on_result_text_changed(self):
        """Handle real-time editing of analysis results"""
        try:
            # Get the edited result from the text field
            import json
            edited_text = self.result_text.toPlainText()
            edited_result = json.loads(edited_text)
            
            # Update the current result with edited version
            self.current_llm_result = edited_result
            
            # Update asset title based on edited content
            self.update_asset_title_from_result(edited_result)
            
        except json.JSONDecodeError:
            # Don't update if JSON is invalid (user might be in the middle of editing)
            pass
        except Exception as e:
            logger.error(f"Error updating result in real-time: {e}")
    
    def update_asset_title_from_result(self, result):
        """Extract and update asset title from analysis result"""
        title = "Untitled Asset"  # Default English title
        
        # First check if we have a summary section with asset_name
        if "summary" in result and isinstance(result["summary"], dict):
            if "asset_name" in result["summary"] and result["summary"]["asset_name"] and result["summary"]["asset_name"].lower() != "unknown":
                name_value = result["summary"]["asset_name"].strip()
                if name_value:
                    title = name_value
                    logger.debug(f"Extracted asset title from summary: {title}")
                    return title
        
        # If no summary or no valid asset_name in summary, fall back to detailed fields
        # Priority order for asset name extraction
        name_fields = [
            "name",                # Generic name field
            "asset_name",         # Explicit asset name
            "chemical_name",      # Chemical specific name
            "equipment_name",     # Equipment specific name
            "reagent_name",       # Reagent specific name
            "product_name",       # Product specific name
            "title"               # Fallback to title field
        ]
        
        # Try each field in priority order
        for field in name_fields:
            if field in result and result[field] and result[field].lower() != "unknown":
                # Clean up the name - remove any "unknown" values
                name_value = result[field].strip()
                if name_value and not name_value.lower() == "unknown":
                    title = name_value
                    break
        
        # Log the extracted title for debugging
        logger.debug(f"Extracted asset title from detailed fields: {title}")
        
        # Update title display if we have a UI element for it
        # This could be added in future UI updates
        
        return title
    
    def save_to_elabftw(self):
        """Save to elabFTW"""
        if not self.current_llm_result:
            self.set_status("Please analyze the image first")
            return
        
        try:
            # Disable button
            self.save_button.setEnabled(False)
            self.set_status("Saving to elabFTW...")
            
            # Get current template ID
            template_id = self.template_combo.currentData()
            if not template_id:
                self.set_status("Please select a template")
                self.save_button.setEnabled(True)
                return
            
            # Get the edited result from the text field
            try:
                import json
                edited_result = json.loads(self.result_text.toPlainText())
                self.current_llm_result = edited_result  # Update the current result with edited version
            except json.JSONDecodeError as e:
                self.set_status("The edited result contains invalid JSON. Please correct it before saving.")
                self.save_button.setEnabled(True)
                return
            
            # Extract asset name for title if available
            title = self.update_asset_title_from_result(self.current_llm_result)
            
            # Create a copy of the data with the extracted title
            asset_data = self.current_llm_result.copy()
            asset_data["title"] = title  # Ensure title is in the data
            
            # Create asset
            asset_id = self.elab_manager.create_asset_from_llm_data(
                template_id,
                asset_data,
                self.current_image_path
            )
            
            if asset_id:
                self.current_asset_id = asset_id
                self.set_status(f"Saved to elabFTW (ID: {asset_id}")
                # Automatically generate QR code after saving to elabFTW
                self.generate_qrcode()
                # Disable the generate QR code button in QR code tab
                self.generate_qrcode_button.setEnabled(False)
            else:
                self.set_status("Failed to save to elabFTW")
            
        except Exception as e:
            logger.error(f"Error saving to elabFTW: {e}")
            self.set_status(f"Error saving to elabFTW: {e}")
        finally:
            # Restore button
            self.save_button.setEnabled(True)
    
    def generate_qrcode(self):
        """Generate QR code"""
        if not self.current_asset_id:
            self.set_status("Please save to elabFTW first")
            return
        
        try:
            # Disable button
            self.generate_qrcode_button.setEnabled(False)
            self.set_status("Generating QR code...")
            
            # Get asset information
            asset_info = self.elab_manager.get_item(self.current_asset_id)
            if not asset_info:
                self.set_status("Failed to get asset information")
                self.generate_qrcode_button.setEnabled(True)
                return
            
            # Generate QR code
            success, file_path = self.qrcode_generator.create_asset_qrcode(
                self.current_asset_id,
                asset_info
            )
            
            if success:
                # Display QR code
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.qrcode_label.setPixmap(pixmap)
                
                self.set_status(f"QR code generated: {file_path}")
                self.save_qrcode_button.setEnabled(True)
            else:
                self.set_status(f"Failed to generate QR code: {file_path}")
            
        except Exception as e:
            # Ensure error message is in English
            error_msg = str(e)
            if "生成二维码失败" in error_msg or "生成二维码图像失败" in error_msg:
                error_msg = "Failed to generate QR code image"
            logger.error(f"QR code generation error: {error_msg}")
            self.set_status(f"QR code generation error: {error_msg}")
        finally:
            # Restore button
            self.generate_qrcode_button.setEnabled(True)
    
    def save_qrcode(self):
        """Save QR code"""
        if not self.current_asset_id:
            self.set_status("Please save to elabFTW and generate QR code first")
            return
        
        try:
            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save QR Code", "", "PNG Image (*.png);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # Ensure filename has .png extension
            if not file_path.lower().endswith(".png"):
                file_path += ".png"
            
            # Get asset information
            asset_info = self.elab_manager.get_item(self.current_asset_id)
            if not asset_info:
                self.set_status("Failed to get asset information")
                return
            
            # Generate label
            success, label_path = self.qrcode_generator.create_label(
                self.current_asset_id,
                asset_info,
                filename=os.path.basename(file_path)
            )
            
            if success:
                # Copy file to user-selected location
                import shutil
                shutil.copy2(label_path, file_path)
                
                self.set_status(f"QR code label saved: {file_path}")
            else:
                self.set_status(f"Failed to save QR code label: {label_path}")
            
        except Exception as e:
            logger.error(f"QR code save error: {e}")
            self.set_status(f"QR code save error: {e}")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            # Get updated configuration
            new_config = dialog.get_config()
            
            # Save configuration
            self.config_manager.update_config(new_config)
            self.config = new_config
            
            # Apply new configuration
            self.apply_config()
            
            self.set_status("Settings updated")
    
    def apply_config(self):
        """Apply configuration"""
        # Update LLM manager
        self.llm_manager.change_provider(
            self.config["llm"]["provider"],
            self.config["llm"]
        )
        
        # Update elabFTW manager
        self.elab_manager = ElabManager(
            api_url=self.config["elabftw"]["api_url"],
            api_key=self.config["elabftw"]["api_key"],
            verify_ssl=self.config["elabftw"]["verify_ssl"]
        )
        
        # Reload templates
        self.load_templates()
        
        # Restart camera
        self.stop_camera()
        self.camera_manager = CameraManager(
            device_id=0,  # Device ID remains unchanged
            resolution=tuple(self.config["camera"]["resolution"])
        )
        self.start_camera()
    
    def set_status(self, message):
        """Set status message"""
        self.status_label.setText(message)
        logger.info(message)
    
    def show_elab_info(self):
        """Show elabFTW information window"""
        if not self.elab_info_window:
            self.elab_info_window = ElabFTWInfoWindow(self.elab_manager, self)
        self.elab_info_window.show()
        self.elab_info_window.refresh_info()
    
    def closeEvent(self, event):
        """Window close event handler"""
        # 停止摄像头
        self.stop_camera()
        
        # 停止LLM线程
        if self.llm_thread and self.llm_thread.isRunning():
            self.llm_thread.wait()
        
        # Close elabFTW info window if open
        if self.elab_info_window:
            self.elab_info_window.close()
        
        event.accept()
    
    def run(self):
        """Run the application (deprecated, kept for compatibility)"""
        # This method is no longer needed as QApplication is initialized in main.py
        # and show() is called directly
        self.show()
        return 0