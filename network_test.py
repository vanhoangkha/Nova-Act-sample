#!/usr/bin/env python3
"""
Network Test for Nova Act
=========================

Test Nova Act with different starting pages to find one that works.
"""

import os
import traceback
from nova_act import NovaAct

def test_websites():
    """Test different websites to find one that works"""
    print("🌐 Testing Network Connectivity for Nova Act")
    print("=" * 50)
    
    # Test different websites
    test_sites = [
        "https://httpbin.org/html",
        "https://www.google.com",
        "https://github.com",
        "https://stackoverflow.com",
        "about:blank"  # Local blank page
    ]
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ NOVA_ACT_API_KEY not set")
        return False
    
    print(f"✅ API Key: {api_key[:8]}...")
    
    for site in test_sites:
        print(f"\n🔍 Testing: {site}")
        try:
            with NovaAct(
                starting_page=site,
                headless=True,
                go_to_url_timeout=30000  # 30 seconds timeout
            ) as nova:
                print(f"✅ Successfully loaded: {site}")
                print(f"📄 Page title: {nova.page.title()}")
                print(f"🔗 Current URL: {nova.page.url}")
                
                # Try a simple screenshot
                screenshot = nova.page.screenshot()
                print(f"📸 Screenshot: {len(screenshot)} bytes")
                
                print(f"🎉 {site} works perfectly!")
                return site
                
        except Exception as e:
            print(f"❌ Failed to load {site}: {str(e)[:100]}...")
            continue
    
    print("\n💥 All test sites failed")
    return None

def run_simple_demo(working_site):
    """Run a simple demo with the working site"""
    print(f"\n🚀 Running Simple Demo with {working_site}")
    print("=" * 50)
    
    try:
        with NovaAct(
            starting_page=working_site,
            headless=True,
            go_to_url_timeout=30000
        ) as nova:
            print("✅ Nova Act session started successfully!")
            
            # Get basic page information
            title = nova.page.title()
            url = nova.page.url
            
            print(f"📄 Page Title: {title}")
            print(f"🔗 Current URL: {url}")
            
            # Try to get page content
            content = nova.page.content()
            print(f"📝 Page Content Length: {len(content)} characters")
            
            # Take a screenshot
            screenshot = nova.page.screenshot()
            print(f"📸 Screenshot Size: {len(screenshot)} bytes")
            
            print("✅ Basic Nova Act functionality confirmed!")
            return True
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Nova Act Network Connectivity Test")
    print("==================================")
    
    # First test which sites work
    working_site = test_websites()
    
    if working_site:
        # Run a simple demo with the working site
        success = run_simple_demo(working_site)
        
        if success:
            print("\n🎉 Nova Act is working correctly!")
            print("💡 You can now run demos with this configuration")
        else:
            print("\n💥 Demo failed even with working site")
    else:
        print("\n❌ No working sites found - check network connectivity")
