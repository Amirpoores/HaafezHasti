import re
import requests
import uuid

def detect_device_info(user_agent):
    device_info = {
        'device_type': 'desktop',
        'browser': 'unknown',
        'os': 'unknown'
    }
    
    if 'Mobile' in user_agent:
        device_info['device_type'] = 'mobile'
    elif 'iPad' in user_agent:
        device_info['device_type'] = 'tablet'
    
    if 'Chrome' in user_agent:
        device_info['browser'] = 'chrome'
    elif 'Firefox' in user_agent:
        device_info['browser'] = 'firefox'
    
    if 'Windows' in user_agent:
        device_info['os'] = 'windows'
    elif 'Mac' in user_agent:
        device_info['os'] = 'macos'
    
    return device_info

def get_location_from_ip(ip):
    try:
        if ip in ['127.0.0.1', 'localhost']:
            return {'country': 'Iran', 'city': 'Local', 'region': 'Local'}
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return {
                'country': data.get('country', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'region': data.get('regionName', 'Unknown')
            }
    except:
        pass
    return {'country': 'Unknown', 'city': 'Unknown', 'region': 'Unknown'}

def generate_session_id():
    return str(uuid.uuid4())[:8]