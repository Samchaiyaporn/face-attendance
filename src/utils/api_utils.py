"""
API Configuration Utility
ช่วยจัดการการกำหนดค่า API URL ในทุกส่วนของระบบ
"""

import os
import json
import sys

# Default API configuration
DEFAULT_API_CONFIG = {
    "base_url": "https://smart-school-uat.belib.app",
    "api_path": "/api",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0
}

def get_config_path():
    """Get the configuration directory path"""
    # Try to find config directory from current location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in the config directory
    if os.path.basename(current_dir) == 'config':
        return current_dir
    
    # Otherwise, try to find config directory
    config_paths = [
        os.path.join(current_dir, 'config'),
        os.path.join(current_dir, '..', 'config'),
        os.path.join(current_dir, '..', '..', 'config'),
        os.path.join(current_dir, '..', '..', '..', 'config'),
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    return current_dir

def load_api_config():
    """Load API configuration from settings.json"""
    config_dir = get_config_path()
    settings_file = os.path.join(config_dir, 'settings.json')
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove comments from JSON
                lines = content.split('\n')
                clean_lines = []
                for line in lines:
                    # Remove single line comments
                    if '//' in line:
                        line = line.split('//')[0]
                    clean_lines.append(line)
                clean_content = '\n'.join(clean_lines)
                
                data = json.loads(clean_content)
                if 'api' in data:
                    return data['api']
        except Exception as e:
            print(f"Error loading API config: {e}")
    
    return DEFAULT_API_CONFIG

def get_api_base_url():
    """Get the base API URL"""
    config = load_api_config()
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
            "search": "/users/search",
            "create": "/users",
            "update": "/users/{id}",
            "delete": "/users/{id}"
        },
        "attendance": {
            "mark": "/face-attendance",
            "list": "/attendance",
            "report": "/attendance/report",
            "export": "/attendance/export"
        },
        "health": {
            "check": "/health"
        }
    }
    
    if category not in endpoints:
        raise ValueError(f"Unknown endpoint category: {category}")
    
    if endpoint not in endpoints[category]:
        raise ValueError(f"Unknown endpoint: {endpoint} in {category}")
    
    endpoint_path = endpoints[category][endpoint]
    
    # Format endpoint with provided variables
    if kwargs:
        endpoint_path = endpoint_path.format(**kwargs)
    
    return f"{base_url}{endpoint_path}"

def setup_api_imports():
    """Setup imports for API configuration across the project"""
    config_dir = get_config_path()
    if config_dir not in sys.path:
        sys.path.insert(0, config_dir)

# Auto-setup when imported
setup_api_imports()

# Convenience functions for backwards compatibility
def get_base_api_url():
    """Alias for get_api_base_url"""
    return get_api_base_url()

def get_api_url(category, endpoint, **kwargs):
    """Alias for get_api_endpoint"""
    return get_api_endpoint(category, endpoint, **kwargs)

# Convenience function to get API URL without imports for fallback
def get_fallback_api_base_url():
    """Get API base URL using configuration or fallback"""
    try:
        config = load_api_config()
        return f"{config['base_url']}{config['api_path']}"
    except:
        return f"{DEFAULT_API_CONFIG['base_url']}{DEFAULT_API_CONFIG['api_path']}"

def get_fallback_api_endpoint(category, endpoint):
    """Get API endpoint URL using configuration or fallback"""
    try:
        return get_api_endpoint(category, endpoint)
    except:
        # Basic fallback endpoints
        if category == "auth" and endpoint == "login":
            return f"{get_fallback_api_base_url()}/auth"
        return get_fallback_api_base_url()

# Configuration constants
API_BASE_URL = get_api_base_url()
API_TIMEOUT = load_api_config().get('timeout', 30)
API_RETRY_ATTEMPTS = load_api_config().get('retry_attempts', 3)
API_RETRY_DELAY = load_api_config().get('retry_delay', 1.0)
