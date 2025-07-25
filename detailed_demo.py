#!/usr/bin/env python3
"""
Detailed Nova Act Demo
=====================

A demo with detailed error reporting.
"""

import os
import traceback
from nova_act import NovaAct

def detailed_demo():
    """Demo with detailed error reporting"""
    print("🚀 Starting Detailed Nova Act Demo")
    print("=" * 40)
    
    try:
        print("🌐 Creating Nova Act instance...")
        nova = NovaAct(
            starting_page="https://example.com",
            headless=True
        )
        
        print("🚀 Starting session...")
        nova.start()
        
        print("✅ Session started successfully!")
        print(f"🔗 Current URL: {nova.page.url}")
        print(f"📄 Page title: {nova.page.title()}")
        
        # Try a simple act() call
        print("🎯 Attempting act() call...")
        try:
            result = nova.act("What is the main heading on this page?", timeout=60)
            print(f"📝 Act result: {result.response}")
            print("✅ Act call successful!")
        except Exception as act_error:
            print(f"❌ Act call failed: {act_error}")
            print("📋 Act error traceback:")
            traceback.print_exc()
        
        print("🛑 Stopping session...")
        nova.stop()
        
        print("✅ Demo completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = detailed_demo()
    if success:
        print("\n🎉 Detailed demo completed!")
    else:
        print("\n💥 Demo failed - check error details above")
