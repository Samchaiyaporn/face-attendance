"""
Simple API Configuration Loader
โหลด API configuration ได้จากทุกที่ในโปรเจค
"""

import os
import json

class APIConfig:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_config()
    
    def _load_config(self):
        """Load API configuration from settings.json files"""
        # Default configuration
        default_config = {
            "base_url": "https://smart-school-uat.belib.app",
            "api_path": "/api",
            "timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 1.0
        }
        
        # Try to find and load configuration files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Possible config file locations
        config_paths = [
            # From current directory
            os.path.join(current_dir, 'settings.json'),
            # From config directory (if we're in config)
            os.path.join(current_dir, '..', 'settings.json'),
            # From project root config
            os.path.join(current_dir, '..', '..', 'config', 'settings.json'),
            os.path.join(current_dir, '..', '..', '..', 'config', 'settings.json'),
            # From installer config
            os.path.join(current_dir, '..', '..', 'installer', 'config', 'settings.json'),
            os.path.join(current_dir, '..', '..', '..', 'installer', 'config', 'settings.json'),
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Remove JSON comments
                        lines = []
                        for line in content.split('\n'):
                            if '//' in line:
                                line = line.split('//')[0]
                            lines.append(line)
                        clean_content = '\n'.join(lines)
                        
                        data = json.loads(clean_content)
                        if 'api' in data:
                            # Merge with default config
                            api_config = default_config.copy()
                            api_config.update(data['api'])
                            return api_config
                except Exception as e:
                    continue
        
        return default_config
    
    def get_base_url(self):
        """Get base API URL"""
        return f"{self._config['base_url']}{self._config['api_path']}"
    
    def get_endpoint(self, category, endpoint, **kwargs):
        """Get specific API endpoint URL"""
        base_url = self.get_base_url()
        
        # Define endpoints
        endpoints = {
            "auth": {
                "login": "/auth",
                "logout": "/auth/logout",
                "refresh": "/auth/refresh",
                "verify": "/auth/verify"
            },
            "students": {
                "list": "/users/group/student",
                "detail": "/users/{id}",
                "search": "/users/search"
            },
            "attendance": {
                "mark": "/face-attendance",
                "list": "/attendance",
                "report": "/attendance/report"
            },
            "health": {
                "check": "/health"
            }
        }
        
        if category in endpoints and endpoint in endpoints[category]:
            endpoint_path = endpoints[category][endpoint]
            if kwargs:
                endpoint_path = endpoint_path.format(**kwargs)
            return f"{base_url}{endpoint_path}"
        
        return base_url
    
    def get_timeout(self):
        """Get API timeout"""
        return self._config.get('timeout', 30)
    
    def get_retry_config(self):
        """Get retry configuration"""
        return {
            'attempts': self._config.get('retry_attempts', 3),
            'delay': self._config.get('retry_delay', 1.0)
        }

# Global instance
api_config = APIConfig()

# Convenience functions
def get_api_base_url():
    """Get base API URL"""
    return api_config.get_base_url()

def get_api_endpoint(category, endpoint, **kwargs):
    """Get specific API endpoint URL"""
    return api_config.get_endpoint(category, endpoint, **kwargs)

def get_api_timeout():
    """Get API timeout"""
    return api_config.get_timeout()

def get_api_retry_config():
    """Get retry configuration"""
    return api_config.get_retry_config()
