#!/usr/bin/env python3
"""
Debug Nova Act Test
==================

A test with detailed error reporting to debug Nova Act issues.
"""

import os
import traceback
from nova_act import NovaAct

def debug_test():
    """Debug test with detailed error reporting"""
    print("🔍 Starting Nova Act Debug Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ NOVA_ACT_API_KEY not set")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    try:
        print("🌐 Initializing Nova Act with detailed settings...")
        
        # Try with explicit settings
        nova = NovaAct(
            starting_page="https://example.com",
            headless=True,  # Run in headless mode
            quiet=False     # Show all logs
        )
        
        print("✅ Nova Act object created")
        
        print("🚀 Starting Nova Act session...")
        nova.start()
        
        print("✅ Nova Act session started successfully!")
        print("🌐 Browser opened to example.com")
        
        # Simple action
        print("🎯 Performing simple action...")
        result = nova.act("What is the main heading on this page?")
        
        print(f"📝 Result: {result.response}")
        
        # Stop the session
        nova.stop()
        print("🛑 Nova Act session stopped")
        
        print("✅ Debug test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_test()
    if success:
        print("\n🎉 Nova Act is working correctly!")
    else:
        print("\n💥 Nova Act test failed - check the error details above")
