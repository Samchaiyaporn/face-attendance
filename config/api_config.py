"""
API Configuration for Smart School Face Attendance System
"""

# API Configuration
API_CONFIG = {
    "base_url": "https://smart-school-uat.belib.app",
    "api_path": "/api",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "SmartSchool-FaceAttendance/1.0"
    }
}

# API Endpoints
API_ENDPOINTS = {
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

def get_api_url(endpoint_category=None, endpoint_name=None, **kwargs):
    """
    Get full API URL for a specific endpoint
    
    Args:
        endpoint_category (str): Category of endpoint (auth, students, etc.)
        endpoint_name (str): Name of endpoint within category
        **kwargs: Variables to format into URL (e.g., id=123)
    
    Returns:
        str: Full API URL
    """
    base_url = API_CONFIG["base_url"]
    api_path = API_CONFIG["api_path"]
    
    if not endpoint_category or not endpoint_name:
        return f"{base_url}{api_path}"
    
    if endpoint_category not in API_ENDPOINTS:
        raise ValueError(f"Unknown endpoint category: {endpoint_category}")
    
    if endpoint_name not in API_ENDPOINTS[endpoint_category]:
        raise ValueError(f"Unknown endpoint: {endpoint_name} in {endpoint_category}")
    
    endpoint = API_ENDPOINTS[endpoint_category][endpoint_name]
    
    # Format endpoint with provided variables
    if kwargs:
        endpoint = endpoint.format(**kwargs)
    
    return f"{base_url}{api_path}{endpoint}"

def get_base_api_url():
    """Get base API URL (base_url + api_path)"""
    return f"{API_CONFIG['base_url']}{API_CONFIG['api_path']}"

def get_headers():
    """Get default headers for API requests"""
    return API_CONFIG["headers"].copy()

def get_timeout():
    """Get default timeout for API requests"""
    return API_CONFIG["timeout"]

def get_retry_config():
    """Get retry configuration"""
    return {
        "attempts": API_CONFIG["retry_attempts"],
        "delay": API_CONFIG["retry_delay"]
    }

def update_api_url(new_base_url):
    """Update the base API URL"""
    API_CONFIG["base_url"] = new_base_url
