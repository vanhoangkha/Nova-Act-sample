#!/usr/bin/env python3
"""
Nova Act Demo: Basic E-commerce Operations
==========================================

This demo shows basic e-commerce operations like searching for products,
navigating product pages, and adding items to cart on Amazon.

Based on the Quick Start example from the Nova Act README.
"""

import os
import sys
from nova_act import NovaAct

def basic_amazon_demo():
    """
    Basic Amazon shopping demo - search and add to cart
    """
    print("🛒 Starting Basic E-commerce Demo")
    print("=" * 50)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/basic_ecommerce"
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
            print("Check the logs directory for detailed traces.")
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return False
    
    return True

def advanced_amazon_demo():
    """
    More advanced Amazon demo with multiple steps
    """
    print("\n🛒 Starting Advanced E-commerce Demo")
    print("=" * 50)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/advanced_ecommerce"
        ) as nova:
            # Search for specific product with filters
            print("🔍 Searching for wireless headphones...")
            nova.act("search for wireless headphones")
            
            # Apply filters
            print("🎛️ Applying filters...")
            nova.act("click on the filter for 'Customer Reviews' and select '4 Stars & Up'")
            
            # Sort results
            print("📊 Sorting results by price...")
            nova.act("sort results by price from low to high")
            
            # Select a product
            print("👆 Selecting a product...")
            nova.act("click on the second product in the results")
            
            # Check product details
            print("📋 Checking product details...")
            nova.act("scroll down to see product specifications and customer reviews")
            
            # Add to cart
            print("🛒 Adding to cart...")
            nova.act("click 'Add to Cart'")
            
            # Go to cart
            print("🛒 Viewing cart...")
            nova.act("click on the cart icon to view cart")
            
            print("✅ Advanced demo completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during advanced demo: {e}")
        return False
    
    return True

def main():
    """Main function to run both demos"""
    print("Nova Act E-commerce Demo Suite")
    print("==============================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    # Run basic demo
    success1 = basic_amazon_demo()
    
    # Run advanced demo
    success2 = advanced_amazon_demo()
    
    if success1 and success2:
        print("\n🎉 All e-commerce demos completed successfully!")
    else:
        print("\n⚠️ Some demos encountered issues. Check the logs for details.")

if __name__ == "__main__":
    main()
