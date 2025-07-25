#!/usr/bin/env python3
"""
Minimal Nova Act Test
====================

The most basic test possible to verify Nova Act functionality.
"""

import os
import traceback
from nova_act import NovaAct

def minimal_test():
    """Minimal test with basic parameters only"""
    print("🔍 Starting Minimal Nova Act Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ NOVA_ACT_API_KEY not set")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    try:
        print("🌐 Initializing Nova Act with minimal settings...")
        
        # Try with just the required parameter
        with NovaAct(starting_page="https://example.com") as nova:
            print("✅ Nova Act initialized successfully!")
            print("🌐 Browser opened to example.com")
            
            # Simple action
            print("🎯 Performing simple action...")
            result = nova.act("What is the main heading on this page?")
            
            print(f"📝 Result: {result.response}")
            print("✅ Minimal test completed successfully!")
            
            return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = minimal_test()
    if success:
        print("\n🎉 Nova Act is working correctly!")
    else:
        print("\n💥 Nova Act test failed - check the error details above")
