#!/usr/bin/env python3
"""
Test Nova Act API Key
"""

import os
from nova_act import NovaAct

def test_api_key():
    """Test if API key works"""
    print("🔑 Testing Nova Act API Key...")
    print(f"API Key length: {len(os.getenv('NOVA_ACT_API_KEY', ''))}")
    
    try:
        with NovaAct(
            starting_page="https://www.google.com",
            headless=True,
            logs_directory="./demo/logs/api_test"
        ) as nova:
            print("✅ API key is valid and Nova Act initialized successfully!")
            
            # Simple test action
            nova.act("check if this is Google homepage")
            print("✅ Basic action completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

if __name__ == "__main__":
    test_api_key()
