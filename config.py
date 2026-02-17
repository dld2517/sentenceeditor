#!/usr/bin/env python3
"""
Configuration Manager
Handles reading and managing application configuration
"""

import os
import configparser
from pathlib import Path


class Config:
    """Configuration manager for sentence editor"""
    
    DEFAULT_CONFIG_FILE = "sentence_editor.conf"
    
    # Default values
    DEFAULTS = {
        'database-home': './data',
        'export-directory': './exports'
    }
    
    def __init__(self, config_file=None):
        """Initialize configuration"""
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create with defaults"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            # Create default config file
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file"""
        self.config['Paths'] = self.DEFAULTS
        
        with open(self.config_file, 'w') as f:
            f.write("# Sentence Editor Configuration\n")
            f.write("# This file controls where data is stored and exported\n\n")
            self.config.write(f)
        
        print(f"Created default configuration file: {self.config_file}")
    
    def get(self, key, fallback=None):
        """Get configuration value"""
        try:
            return self.config.get('Paths', key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback or self.DEFAULTS.get(key)
    
    def get_database_path(self):
        """Get full path to database file"""
        db_home = self.get('database-home')
        
        # Expand user home directory if needed
        db_home = os.path.expanduser(db_home)
        
        # Create directory if it doesn't exist
        os.makedirs(db_home, exist_ok=True)
        
        # Return full path to database file
        return os.path.join(db_home, 'project_outlines.db')
    
    def get_export_directory(self):
        """Get export directory path"""
        export_dir = self.get('export-directory')
        
        # Expand user home directory if needed
        export_dir = os.path.expanduser(export_dir)
        
        # Create directory if it doesn't exist
        os.makedirs(export_dir, exist_ok=True)
        
        return export_dir
    
    def get_project_export_path(self, project_name):
        """
        Get versioned export path for a specific project
        Creates: export-directory/project_name/yyyy-mm-dd-v1/
        If that exists, creates yyyy-mm-dd-v2, etc.
        
        Args:
            project_name: Name of the project
        
        Returns:
            Full path to versioned project export directory
        """
        from datetime import datetime
        
        export_dir = self.get_export_directory()
        
        # Sanitize project name for filesystem
        safe_project_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' 
                                    for c in project_name)
        safe_project_name = safe_project_name.strip().replace(' ', '_')
        
        # Get today's date in yyyy-mm-dd format
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Build base path: export-directory/project_name/
        project_dir = os.path.join(export_dir, safe_project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Find next available version number
        version = 1
        while True:
            versioned_dir = os.path.join(project_dir, f"{today}-v{version}")
            if not os.path.exists(versioned_dir):
                os.makedirs(versioned_dir)
                return versioned_dir
            version += 1
    
    def set(self, key, value):
        """Set configuration value and save"""
        if 'Paths' not in self.config:
            self.config['Paths'] = {}
        
        self.config['Paths'][key] = value
        
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def display_config(self):
        """Display current configuration"""
        print("\nCurrent Configuration:")
        print(f"  Config file: {self.config_file}")
        print(f"  Database: {self.get_database_path()}")
        print(f"  Exports: {self.get_export_directory()}")


# Global config instance
_config = None

def get_config():
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config


if __name__ == "__main__":
    # Test configuration
    config = Config()
    config.display_config()
    
    # Test project export path (versioned)
    export_path = config.get_project_export_path("My Test Project")
    print(f"\nExample export path: {export_path}")
    
    # Test again to see versioning
    export_path2 = config.get_project_export_path("My Test Project")
    print(f"Second export path: {export_path2}")
    print(f"\nNote: Each export creates a new versioned directory to prevent overwriting.")

