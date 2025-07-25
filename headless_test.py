#!/usr/bin/env python3
"""
Headless Nova Act Test
=====================

Test Nova Act in headless mode for server environments.
"""

import os
import traceback
from nova_act import NovaAct

def headless_test():
    """Test Nova Act in headless mode"""
    print("🔍 Starting Headless Nova Act Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ NOVA_ACT_API_KEY not set")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    try:
        print("🌐 Initializing Nova Act in headless mode...")
        
        # Run in headless mode for server environment
        with NovaAct(
            starting_page="https://example.com",
            headless=True  # This is the key for server environments
        ) as nova:
            print("✅ Nova Act initialized successfully in headless mode!")
            print("🌐 Browser opened to example.com (headless)")
            
            # Simple action
            print("🎯 Performing simple action...")
            result = nova.act("What is the main heading on this page?")
            
            print(f"📝 Result: {result.response}")
            print("✅ Headless test completed successfully!")
            
            return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = headless_test()
    if success:
        print("\n🎉 Nova Act is working correctly in headless mode!")
    else:
        print("\n💥 Nova Act test failed - check the error details above")
