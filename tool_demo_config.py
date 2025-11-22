"""
Configuration module for ToolDemo demonstrations.
Supports loading and managing demo configurations.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class ToolDemoConfig:
    """Configuration manager for ToolDemo instances."""
    
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "max_features": 10,
        "auto_save": True,
        "output_format": "json",
        "debug_mode": False
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path or "tool_demo_config.json"
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
