#!/usr/bin/env python3
"""
Sample file created to demonstrate the Create tool capability.
This file showcases basic Python structure with docstrings.
"""

import os
import sys
from typing import Dict, List, Optional


class ToolDemo:
    """
    Enhanced demo class to showcase Factory tool capabilities.
    
    This class demonstrates the Factory tool suite's ability to:
    - Create well-structured Python code with proper documentation
    - Edit existing files with precise modifications
    - Maintain code quality and consistency
    - Support comprehensive tool demonstrations
    
    Attributes:
        name (str): The name identifier for this demo instance
        version (str): Semantic version string
        features (List[str]): Collection of demonstrated features
        created_at (str): Timestamp of file creation
        modified_count (int): Track file modification attempts
        modification_log (List[str]): Ordered list of modifications
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize the ToolDemo instance with enhanced tracking.
        
        Args:
            name: The name of the demo instance
            version: Semantic version string (default: "1.0.0")
        """
        self.name = name
        self.version = version
        self.features: List[str] = []
        self.created_at = "2025-11-21T10:53:00Z"
        self.modified_count = 0
        self.modification_log: List[str] = []
    
    def add_feature(self, feature: str) -> None:
        """
        Add a feature to the demo.
        
        Args:
            feature: Feature description to add
        """
        self.features.append(feature)
        self.record_modification(f"Added feature: {feature}")
        print(f"Added feature: {feature}")

    def record_modification(self, action: str) -> None:
        """Track modifications performed on the demo state."""
        self.modified_count += 1
        self.modification_log.append(action)

    def reset_features(self) -> None:
        """Clear tracked features while recording the action."""
        self.features.clear()
        self.record_modification("Reset features list")
    
    def get_info(self) -> Dict[str, any]:
        """
        Get demo information.
        
        Returns:
            Dictionary containing demo info
        """
        return {
            "name": self.name,
            "version": self.version,
            "features_count": len(self.features),
            "features": self.features.copy(),
            "modified_count": self.modified_count,
            "modification_log": self.modification_log.copy()
        }


def main():
    """Main function to demonstrate the ToolDemo class."""
    demo = ToolDemo("Factory Tools Demo", "1.0.0")
    
    # Add some features
    demo.add_feature("Read tool for file operations")
    demo.add_feature("LS tool for directory listing")
    demo.add_feature("Grep tool for text searching")
    demo.add_feature("Glob tool for pattern matching")
    demo.add_feature("Create tool for file generation")
    demo.record_modification("Initial feature loading complete")
    
    # Display info
    info = demo.get_info()
    print(f"\n=== {info['name']} v{info['version']} ===")
    print(f"Features added: {info['features_count']}")
    print(f"Modifications tracked: {info['modified_count']}")
    print("\nFeatures:")
    for i, feature in enumerate(info['features'], 1):
        print(f"  {i}. {feature}")
    if info["modification_log"]:
        print("\nModification log:")
        for entry in info["modification_log"]:
            print(f"  - {entry}")
    
    print(f"\nFile created successfully at: {__file__}")


if __name__ == "__main__":
    main()
