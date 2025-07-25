#!/usr/bin/env python3
"""
Run Demo 1 with detailed error reporting
"""

import os
import traceback
from nova_act import NovaAct

def run_basic_ecommerce_demo():
    """
    Basic Amazon shopping demo with detailed error handling
    """
    print("🛒 Starting Basic E-commerce Demo")
    print("=" * 50)
    
    try:
        # Create logs directory
        os.makedirs("./demo/logs/basic_ecommerce", exist_ok=True)
        
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/basic_ecommerce",
            headless=True  # Run in headless mode
        ) as nova:
            print("📱 Navigating to Amazon...")
            
            # Step 1: Search for a product
            print("🔍 Searching for coffee maker...")
            nova.act("search for a coffee maker")
            
            # Step 2: Select first result
            print("👆 Selecting first result...")
            nova.act("select the first result")
            
            # Step 3: Add to cart
            print("🛒 Adding to cart...")
            nova.act("scroll down or up until you see 'add to cart' and then click 'add to cart'")
            
            print("✅ Demo completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = run_basic_ecommerce_demo()
    print(f"Final result: {'SUCCESS' if result else 'FAILED'}")
