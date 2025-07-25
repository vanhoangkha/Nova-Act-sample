#!/usr/bin/env python3
"""
Nova Act Demo Suite Runner
==========================

This script runs all Nova Act demo use cases and provides a comprehensive
overview of Nova Act's capabilities.
"""

import os
import sys
import time
import importlib.util
from pathlib import Path

def load_demo_module(demo_path):
    """Load a demo module dynamically"""
    spec = importlib.util.spec_from_file_location("demo_module", demo_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_demo_safely(demo_name, demo_function):
    """Run a demo function safely with error handling"""
    print(f"\n{'='*60}")
    print(f"🚀 Running {demo_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = demo_function()
        end_time = time.time()
        execution_time = end_time - start_time
        
        if result:
            print(f"✅ {demo_name} completed successfully in {execution_time:.2f}s")
            return True, execution_time
        else:
            print(f"❌ {demo_name} completed with issues in {execution_time:.2f}s")
            return False, execution_time
            
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"💥 {demo_name} failed with error: {e}")
        print(f"⏱️ Failed after {execution_time:.2f}s")
        return False, execution_time

def main():
    """Main function to run all demos"""
    print("Nova Act Complete Demo Suite")
    print("============================")
    print("This will run all Nova Act demo use cases")
    print()
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("./demo/logs", exist_ok=True)
    os.makedirs("./demo/results", exist_ok=True)
    
    # Define all demo modules and their main functions
    demos = [
        ("01_basic_ecommerce.py", "Basic E-commerce Operations", "basic_amazon_demo"),
        ("02_information_extraction.py", "Information Extraction", "extract_books_demo"),
        ("03_parallel_processing.py", "Parallel Processing", "parallel_price_comparison_demo"),
        ("04_authentication_demo.py", "Authentication & Sessions", "setup_persistent_session_demo"),
        ("05_file_operations.py", "File Upload/Download", "file_upload_demo"),
        ("06_form_filling.py", "Form Filling", "basic_contact_form_demo"),
        ("07_search_filter.py", "Search & Filter", "basic_search_demo"),
        ("08_real_estate.py", "Real Estate Analysis", "search_properties_demo"),
        ("09_interactive_demo.py", "Interactive Mode", "interactive_session_demo"),
        ("10_advanced_features.py", "Advanced Features", "video_recording_demo")
    ]
    
    print(f"📋 Found {len(demos)} demo modules to run")
    print()
    
    # Ask user for confirmation
    run_all = input("Run all demos? This may take 15-30 minutes (y/n): ").strip().lower()
    
    if run_all != 'y':
        print("Demo suite cancelled by user")
        return
    
    # Track results
    results = []
    total_start_time = time.time()
    
    # Run each demo
    for demo_file, demo_name, demo_function in demos:
        demo_path = Path(__file__).parent / demo_file
        
        if not demo_path.exists():
            print(f"⚠️ Demo file not found: {demo_file}")
            results.append((demo_name, False, 0))
            continue
        
        try:
            # Load the demo module
            module = load_demo_module(demo_path)
            
            # Get the demo function
            if hasattr(module, demo_function):
                func = getattr(module, demo_function)
                success, exec_time = run_demo_safely(demo_name, func)
                results.append((demo_name, success, exec_time))
            else:
                print(f"⚠️ Function {demo_function} not found in {demo_file}")
                results.append((demo_name, False, 0))
                
        except Exception as e:
            print(f"💥 Failed to load demo {demo_file}: {e}")
            results.append((demo_name, False, 0))
        
        # Brief pause between demos
        time.sleep(2)
    
    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("📊 NOVA ACT DEMO SUITE RESULTS")
    print(f"{'='*80}")
    
    successful_demos = sum(1 for _, success, _ in results if success)
    total_demos = len(results)
    success_rate = (successful_demos / total_demos) * 100 if total_demos > 0 else 0
    
    print(f"🎯 Overall Success Rate: {successful_demos}/{total_demos} ({success_rate:.1f}%)")
    print(f"⏱️ Total Execution Time: {total_execution_time:.2f} seconds ({total_execution_time/60:.1f} minutes)")
    print()
    
    # Detailed results
    print("📋 Detailed Results:")
    print("-" * 80)
    
    for demo_name, success, exec_time in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:<8} {demo_name:<35} {exec_time:>8.2f}s")
    
    print("-" * 80)
    
    # Performance statistics
    successful_times = [exec_time for _, success, exec_time in results if success and exec_time > 0]
    if successful_times:
        avg_time = sum(successful_times) / len(successful_times)
        min_time = min(successful_times)
        max_time = max(successful_times)
        
        print(f"📈 Performance Statistics (successful demos only):")
        print(f"   Average execution time: {avg_time:.2f}s")
        print(f"   Fastest demo: {min_time:.2f}s")
        print(f"   Slowest demo: {max_time:.2f}s")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if success_rate >= 80:
        print("🎉 Excellent! Nova Act is working well in your environment.")
        print("   You can confidently use Nova Act for your automation needs.")
    elif success_rate >= 60:
        print("👍 Good! Most demos passed successfully.")
        print("   Check the failed demos for specific issues.")
    elif success_rate >= 40:
        print("⚠️ Mixed results. Some demos had issues.")
        print("   Review your setup and network connectivity.")
    else:
        print("❌ Many demos failed. Please check:")
        print("   - API key is valid and set correctly")
        print("   - Network connectivity is stable")
        print("   - Required dependencies are installed")
    
    # Save results to file
    results_file = "./demo/results/demo_suite_results.txt"
    with open(results_file, "w") as f:
        f.write("Nova Act Demo Suite Results\n")
        f.write("===========================\n\n")
        f.write(f"Execution Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Success Rate: {successful_demos}/{total_demos} ({success_rate:.1f}%)\n")
        f.write(f"Total Time: {total_execution_time:.2f}s\n\n")
        
        f.write("Detailed Results:\n")
        for demo_name, success, exec_time in results:
            status = "PASS" if success else "FAIL"
            f.write(f"{status:<8} {demo_name:<35} {exec_time:>8.2f}s\n")
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Final message
    if success_rate >= 80:
        print("\n🎉 Demo suite completed successfully!")
        print("Nova Act is ready for your automation projects!")
    else:
        print(f"\n⚠️ Demo suite completed with {total_demos - successful_demos} failures.")
        print("Check the logs in ./demo/logs/ for detailed error information.")

if __name__ == "__main__":
    main()
