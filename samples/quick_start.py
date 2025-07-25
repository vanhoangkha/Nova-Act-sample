#!/usr/bin/env python3
"""
Nova Act Samples Quick Start

This script helps you get started with Nova Act samples by running
simple examples from different categories.
"""

import os
import sys
from datetime import datetime

def check_api_key():
    """Check if Nova Act API key is configured"""
    api_key = os.getenv("NOVA_ACT_API_KEY")
    if not api_key:
        print("❌ NOVA_ACT_API_KEY environment variable not set!")
        print("Please set your API key:")
        print("export NOVA_ACT_API_KEY='your_api_key'")
        print("\nGet your API key from: https://nova.amazon.com/act")
        return False
    print("✅ API key configured")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import nova_act
        print("✅ Nova Act installed")
    except ImportError:
        print("❌ Nova Act not installed. Run: pip install nova-act")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic installed")
    except ImportError:
        print("❌ Pydantic not installed. Run: pip install pydantic")
        return False
    
    return True

def run_simple_example():
    """Run a simple Nova Act example"""
    print("\n🚀 Running simple Nova Act example...")
    
    try:
        from nova_act import NovaAct, BOOL_SCHEMA
        
        with NovaAct(starting_page="https://www.amazon.com") as nova:
            print("📱 Opened Amazon.com")
            
            # Simple search test
            nova.act("search for 'coffee maker'")
            print("✅ Performed search")
            
            # Check if results are displayed
            result = nova.act("Are search results displayed on the page?", schema=BOOL_SCHEMA)
            if result.matches_schema and result.parsed_response:
                print("✅ Search results found")
            else:
                print("⚠️ Search results not clearly visible")
            
            print("🎉 Simple example completed successfully!")
            
    except Exception as e:
        print(f"❌ Error running example: {e}")
        return False
    
    return True

def show_sample_menu():
    """Show available sample categories"""
    print("\n📁 Available Sample Categories:")
    print("1. 🛒 E-commerce - Product monitoring and competitor analysis")
    print("2. 📈 Data Extraction - News aggregation and job market analysis")
    print("3. 🏠 Real Estate - Property market analysis")
    print("4. 🤖 Automation - Form automation and workflow automation")
    print("5. 🔬 Research - Academic research and literature reviews")
    print("6. 🧪 Testing - Web application testing and QA automation")
    
    print("\n💡 To run a specific sample:")
    print("cd samples/ecommerce && python product_price_monitor.py")
    print("cd samples/data_extraction && python news_aggregator.py")
    print("cd samples/real_estate && python property_market_analyzer.py")
    print("cd samples/automation && python form_automation.py")
    print("cd samples/research && python academic_research_assistant.py")
    print("cd samples/testing && python web_app_tester.py")

def show_customization_tips():
    """Show tips for customizing samples"""
    print("\n🔧 Customization Tips:")
    print("1. Update target URLs in each sample to match your needs")
    print("2. Modify data models (Pydantic classes) for your specific data")
    print("3. Adjust parallel processing workers based on your system")
    print("4. Customize analysis functions for your use case")
    print("5. Add your own error handling and logging")
    
    print("\n📚 Key Files to Modify:")
    print("• sites_to_analyze = [...] - Change target websites")
    print("• class DataModel(BaseModel) - Modify data structure")
    print("• max_workers=3 - Adjust concurrency")
    print("• search_criteria = {...} - Update search parameters")

def main():
    print("🌟 Nova Act Samples Quick Start")
    print("=" * 40)
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    if not check_api_key():
        return 1
    
    if not check_dependencies():
        return 1
    
    # Run simple example
    print("\n🧪 Testing Nova Act functionality...")
    if not run_simple_example():
        return 1
    
    # Show available samples
    show_sample_menu()
    
    # Show customization tips
    show_customization_tips()
    
    print("\n🎯 Next Steps:")
    print("1. Choose a sample category that matches your use case")
    print("2. Navigate to the sample directory")
    print("3. Review and customize the sample code")
    print("4. Run the sample: python sample_name.py")
    print("5. Check the generated reports and logs")
    
    print("\n📞 Need Help?")
    print("• Check samples/README.md for detailed documentation")
    print("• Email: nova-act@amazon.com")
    print("• Main documentation: README.md")
    
    print(f"\n✅ Quick start completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
