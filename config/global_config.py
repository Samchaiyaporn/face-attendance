"""
Global API Configuration
ไฟล์กลางสำหรับการกำหนดค่า API ที่สามารถใช้ได้จากทุกที่ในโปรเจค
"""

import os
import json

# Global API configuration - will be loaded once and used everywhere
_api_config = None

def _load_api_config():
    """Load API configuration from settings files"""
    global _api_config
    
    if _api_config is not None:
        return _api_config
    
    # Default configuration
    default_config = {
        "base_url": "https://smart-school-uat.belib.app",
        "api_path": "/api",
        "timeout": 30,
        "retry_attempts": 3,
        "retry_delay": 1.0
    }
    
    # Try to find config files from different locations
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file))  # Go up to project root
    
    # Possible config file paths
    config_paths = [
        # Main config
        os.path.join(project_root, 'config', 'settings.json'),
        # Installer config
        os.path.join(project_root, 'installer', 'config', 'settings.json'),
        # Fallback paths
        os.path.join(os.path.dirname(current_file), 'settings.json'),
        os.path.join(os.path.dirname(os.path.dirname(current_file)), 'settings.json'),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Remove JSON comments more carefully
                    lines = []
                    for line in content.split('\n'):
                        # Remove comments but preserve strings
                        if '//' in line:
                            # Simple comment removal - only remove if // is not in quotes
                            in_string = False
                            quote_char = None
                            comment_pos = -1
                            
                            for i, char in enumerate(line):
                                if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                                    if not in_string:
                                        in_string = True
                                        quote_char = char
                                    elif char == quote_char:
                                        in_string = False
                                        quote_char = None
                                elif char == '/' and i < len(line) - 1 and line[i+1] == '/' and not in_string:
                                    comment_pos = i
                                    break
                            
                            if comment_pos >= 0:
                                line = line[:comment_pos].rstrip()
                                
                        lines.append(line)
                    clean_content = '\n'.join(lines)
                    
                    data = json.loads(clean_content)
                    if 'api' in data:
                        # Merge with default config
                        config = default_config.copy()
                        config.update(data['api'])
                        _api_config = config
                        return _api_config
            except Exception as e:
                # Silently continue to next config file
                continue
    
    # If no config found, use default
    _api_config = default_config
    return _api_config

def get_api_base_url():
    """Get base API URL (base_url + api_path)"""
    config = _load_api_config()
    return f"{config['base_url']}{config['api_path']}"

def get_api_endpoint(category, endpoint, **kwargs):
    """Get specific API endpoint URL"""
    base_url = get_api_base_url()
    
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

def get_api_timeout():
    """Get API timeout"""
    config = _load_api_config()
    return config.get('timeout', 30)

def get_api_retry_config():
    """Get retry configuration"""
    config = _load_api_config()
    return {
        'attempts': config.get('retry_attempts', 3),
        'delay': config.get('retry_delay', 1.0)
    }

# Constants that can be imported
API_BASE_URL = get_api_base_url()
API_TIMEOUT = get_api_timeout()
