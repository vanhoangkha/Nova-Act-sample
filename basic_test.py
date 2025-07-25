#!/usr/bin/env python3
"""
Basic Nova Act Test
==================

Test basic Nova Act functionality without complex AI operations.
"""

import os
import traceback
from nova_act import NovaAct

def basic_test():
    """Test basic Nova Act functionality"""
    print("🔍 Starting Basic Nova Act Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ NOVA_ACT_API_KEY not set")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    try:
        print("🌐 Initializing Nova Act in headless mode...")
        
        # Initialize Nova Act
        nova = NovaAct(
            starting_page="https://example.com",
            headless=True
        )
        
        print("✅ Nova Act object created")
        
        print("🚀 Starting Nova Act session...")
        nova.start()
        
        print("✅ Nova Act session started successfully!")
        print("🌐 Browser opened to example.com (headless)")
        
        # Check basic browser functionality
        print("🔍 Checking page title...")
        page_title = nova.page.title()
        print(f"📄 Page title: {page_title}")
        
        print("🔍 Checking current URL...")
        current_url = nova.page.url
        print(f"🔗 Current URL: {current_url}")
        
        # Take a screenshot to verify it's working
        print("📸 Taking screenshot...")
        screenshot_bytes = nova.page.screenshot()
        print(f"📸 Screenshot taken: {len(screenshot_bytes)} bytes")
        
        # Stop the session
        print("🛑 Stopping Nova Act session...")
        nova.stop()
        
        print("✅ Basic test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = basic_test()
    if success:
        print("\n🎉 Nova Act basic functionality is working!")
        print("💡 You can now run the full demos")
    else:
        print("\n💥 Nova Act basic test failed")
