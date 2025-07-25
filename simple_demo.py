#!/usr/bin/env python3
"""
Simple Nova Act Demo
===================

A simple demo showing Nova Act's act() functionality.
"""

import os
from nova_act import NovaAct

def simple_demo():
    """Simple demo with act() functionality"""
    print("🚀 Starting Simple Nova Act Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://example.com",
            headless=True
        ) as nova:
            print("✅ Nova Act initialized successfully!")
            print("🌐 Browser opened to example.com")
            
            # Simple action with shorter prompt
            print("🎯 Performing simple action...")
            result = nova.act("click on the 'More information...' link")
            
            print(f"📝 Result: {result.response}")
            
            # Check the new page
            print("🔍 Checking current page...")
            current_url = nova.page.url
            page_title = nova.page.title()
            
            print(f"🔗 Current URL: {current_url}")
            print(f"📄 Page title: {page_title}")
            
            print("✅ Simple demo completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return False

if __name__ == "__main__":
    success = simple_demo()
    if success:
        print("\n🎉 Nova Act demo completed successfully!")
        print("💡 Nova Act is working with your API key!")
    else:
        print("\n💥 Demo failed")
