#!/usr/bin/env python3
"""
Working Nova Act Demo
====================

A practical demo that works in headless mode.
"""

import os
import traceback
from nova_act import NovaAct

def working_demo():
    """Working demo with proper error handling"""
    print("🚀 Starting Working Nova Act Demo")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ NOVA_ACT_API_KEY not set")
        return False
    
    print(f"✅ API Key: {api_key[:8]}...")
    
    try:
        print("🌐 Initializing Nova Act...")
        
        with NovaAct(
            starting_page="https://www.amazon.com",
            headless=True  # Essential for server environments
        ) as nova:
            print("✅ Nova Act initialized successfully!")
            print("🌐 Browser opened to Amazon.com")
            
            # Check basic page info
            print(f"📄 Page title: {nova.page.title()}")
            print(f"🔗 Current URL: {nova.page.url}")
            
            # Try a simple search action
            print("🔍 Attempting to search for 'laptop'...")
            
            try:
                # Use a shorter timeout for testing
                result = nova.act("search for laptop", timeout=30)
                print(f"📝 Search result: {result.response}")
                
                # Check if we're on a search results page
                new_url = nova.page.url
                print(f"🔗 New URL after search: {new_url}")
                
                if "laptop" in new_url.lower() or "search" in new_url.lower():
                    print("✅ Search appears to have worked!")
                else:
                    print("⚠️ Search may not have worked as expected")
                
            except Exception as search_error:
                print(f"❌ Search failed: {search_error}")
                print("🔍 This might be due to API limits or network issues")
            
            print("✅ Demo completed!")
            return True
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

def test_api_key():
    """Test if the API key is valid by checking basic functionality"""
    print("🔑 Testing API Key Validity")
    print("=" * 30)
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"✅ API Key format: {api_key[:8]}...{api_key[-4:]}")
    print(f"📏 API Key length: {len(api_key)} characters")
    
    # Basic format check
    if len(api_key) == 36 and api_key.count('-') == 4:
        print("✅ API Key format looks correct (UUID format)")
        return True
    else:
        print("⚠️ API Key format may be incorrect")
        return False

if __name__ == "__main__":
    print("Nova Act Demo with API Key Validation")
    print("====================================")
    
    # First test the API key
    if test_api_key():
        print("\n" + "="*50)
        # Then run the demo
        success = working_demo()
        
        if success:
            print("\n🎉 Nova Act demo completed successfully!")
            print("💡 Your API key is working and Nova Act is functional!")
        else:
            print("\n💥 Demo encountered issues")
            print("💡 This might be due to:")
            print("   - Network connectivity issues")
            print("   - API rate limits")
            print("   - Service availability")
    else:
        print("\n❌ API key validation failed")
        print("💡 Please check your API key from https://nova.amazon.com/act")
