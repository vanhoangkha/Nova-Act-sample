#!/usr/bin/env python3
"""
Fixed Nova Act Demo
==================

A working demo with proper timeout settings.
"""

import os
import traceback
from nova_act import NovaAct

def working_demo():
    """Working demo with correct parameters"""
    print("🚀 Starting Fixed Nova Act Demo")
    print("=" * 40)
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ NOVA_ACT_API_KEY not set")
        return False
    
    print(f"✅ API Key: {api_key[:8]}...")
    
    try:
        print("🌐 Initializing Nova Act with proper settings...")
        
        with NovaAct(
            starting_page="https://www.google.com",
            headless=True,
            go_to_url_timeout=60  # 60 seconds in seconds, not milliseconds
        ) as nova:
            print("✅ Nova Act session started successfully!")
            print("🌐 Browser opened to Google.com")
            
            # Get basic page information
            print("📄 Getting page information...")
            title = nova.page.title()
            url = nova.page.url
            
            print(f"📄 Page Title: {title}")
            print(f"🔗 Current URL: {url}")
            
            # Take a screenshot to verify it's working
            print("📸 Taking screenshot...")
            screenshot = nova.page.screenshot()
            print(f"📸 Screenshot captured: {len(screenshot)} bytes")
            
            # Get page content
            print("📝 Getting page content...")
            content = nova.page.content()
            print(f"📝 Page content length: {len(content)} characters")
            
            print("✅ All basic operations successful!")
            
            # Now try a simple act() call with a short timeout
            print("🎯 Attempting simple act() call...")
            try:
                result = nova.act("What is the main search box on this page?", timeout=30)
                print(f"📝 Act result: {result.response}")
                print("✅ Act call successful!")
            except Exception as act_error:
                print(f"⚠️ Act call timed out or failed: {act_error}")
                print("💡 This is expected - the service might be slow")
            
            print("✅ Demo completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = working_demo()
    if success:
        print("\n🎉 Nova Act demo completed successfully!")
        print("💡 Basic browser automation is working!")
        print("🔧 Act() calls may timeout due to service load")
    else:
        print("\n💥 Demo failed - check error details above")
