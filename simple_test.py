#!/usr/bin/env python3
"""
Simple Nova Act Test
===================

A minimal test to verify Nova Act is working with the API key.
"""

import os
from nova_act import NovaAct

def simple_test():
    """Simple test of Nova Act functionality"""
    print("🚀 Starting Simple Nova Act Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ NOVA_ACT_API_KEY not set")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    try:
        print("🌐 Initializing Nova Act...")
        
        with NovaAct(starting_page="https://example.com") as nova:
            print("✅ Nova Act initialized successfully!")
            print("🌐 Browser opened to example.com")
            
            # Simple action
            print("🎯 Performing simple action...")
            result = nova.act("What is the main heading on this page?")
            
            print(f"📝 Result: {result.response}")
            print("✅ Simple test completed successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n🎉 Nova Act is working correctly!")
    else:
        print("\n💥 Nova Act test failed!")
