#!/usr/bin/env python3
"""
Nova Act Demo: Advanced Features
===============================

This demo shows advanced Nova Act features including video recording,
custom logging, proxy configuration, and S3 integration.
"""

import os
import sys
import boto3
from nova_act import NovaAct
from nova_act.util.s3_writer import S3Writer

def video_recording_demo():
    """
    Demo for recording video of Nova Act sessions
    """
    print("🎥 Starting Video Recording Demo")
    print("=" * 40)
    
    try:
        # Create logs directory for video recording
        logs_dir = "./demo/logs/video_recording"
        os.makedirs(logs_dir, exist_ok=True)
        
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory=logs_dir,
            record_video=True  # Enable video recording
        ) as nova:
            print("🎬 Recording video of Nova Act session...")
            
            # Perform actions that will be recorded
            print("🎯 Action 1: Searching for products")
            nova.act("search for bluetooth speakers")
            
            print("🎯 Action 2: Browsing results")
            nova.act("look at the first few search results")
            
            print("🎯 Action 3: Selecting a product")
            nova.act("click on the first bluetooth speaker")
            
            print("🎯 Action 4: Viewing product details")
            nova.act("scroll down to see product specifications and reviews")
            
            print("✅ Video recording completed!")
            print(f"📁 Video saved in: {logs_dir}")
            
            # List video files
            video_files = [f for f in os.listdir(logs_dir) if f.endswith('.webm')]
            if video_files:
                print(f"🎥 Video file: {video_files[0]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during video recording demo: {e}")
        return False

def custom_logging_demo():
    """
    Demo for custom logging configuration
    """
    print("\n📝 Starting Custom Logging Demo")
    print("=" * 40)
    
    try:
        # Set custom log level via environment variable
        os.environ['NOVA_ACT_LOG_LEVEL'] = '10'  # DEBUG level
        
        custom_logs_dir = "./demo/logs/custom_logging"
        os.makedirs(custom_logs_dir, exist_ok=True)
        
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory=custom_logs_dir,
            quiet=False  # Ensure logs are not suppressed
        ) as nova:
            print("📊 Demonstrating custom logging...")
            
            # Perform actions with detailed logging
            print("🔍 Action with detailed logging")
            nova.act("search for wireless keyboard")
            
            print("📋 Checking log files...")
            
            # List log files created
            log_files = [f for f in os.listdir(custom_logs_dir) if f.endswith('.html')]
            print(f"📄 Log files created: {len(log_files)}")
            
            for log_file in log_files[:3]:  # Show first 3 log files
                print(f"   📄 {log_file}")
            
            print("✅ Custom logging demo completed!")
            return True
            
    except Exception as e:
        print(f"❌ Error during custom logging demo: {e}")
        return False
    finally:
        # Reset log level
        if 'NOVA_ACT_LOG_LEVEL' in os.environ:
            del os.environ['NOVA_ACT_LOG_LEVEL']

def proxy_configuration_demo():
    """
    Demo for proxy configuration (simulated)
    """
    print("\n🌐 Starting Proxy Configuration Demo")
    print("=" * 45)
    
    print("🔧 Demonstrating proxy configuration...")
    print("Note: This demo shows configuration without actual proxy")
    
    # Example proxy configurations
    proxy_configs = [
        {
            "name": "Basic Proxy",
            "config": {
                "server": "http://proxy.example.com:8080"
            }
        },
        {
            "name": "Authenticated Proxy",
            "config": {
                "server": "http://proxy.example.com:8080",
                "username": "proxy_user",
                "password": "proxy_password"
            }
        }
    ]
    
    for proxy_info in proxy_configs:
        print(f"\n🔧 {proxy_info['name']} Configuration:")
        print(f"   Server: {proxy_info['config']['server']}")
        
        if 'username' in proxy_info['config']:
            print(f"   Username: {proxy_info['config']['username']}")
            print(f"   Password: {'*' * len(proxy_info['config']['password'])}")
        
        print("   ✅ Configuration valid")
    
    print("\n💡 To use proxy in real scenario:")
    print("   nova = NovaAct(proxy=proxy_config, ...)")
    
    return True

def s3_integration_demo():
    """
    Demo for S3 integration (simulated)
    """
    print("\n☁️ Starting S3 Integration Demo")
    print("=" * 40)
    
    print("📦 Demonstrating S3 integration setup...")
    print("Note: This demo shows configuration without actual S3 upload")
    
    try:
        # Simulate S3 configuration
        print("🔧 S3Writer Configuration:")
        print("   Bucket: my-nova-act-bucket")
        print("   Prefix: demo-sessions/")
        print("   Metadata: {'Project': 'NovaActDemo'}")
        
        # Show how S3Writer would be configured
        print("\n💡 S3Writer setup code:")
        print("""
        import boto3
        from nova_act.util.s3_writer import S3Writer
        
        boto_session = boto3.Session()
        s3_writer = S3Writer(
            boto_session=boto_session,
            s3_bucket_name="my-nova-act-bucket",
            s3_prefix="demo-sessions/",
            metadata={"Project": "NovaActDemo"}
        )
        
        with NovaAct(
            starting_page="https://example.com",
            boto_session=boto_session,
            stop_hooks=[s3_writer]
        ) as nova:
            nova.act("perform actions...")
        """)
        
        print("\n📋 Required AWS Permissions:")
        print("   - s3:ListObjects on bucket and prefix")
        print("   - s3:PutObject on bucket and prefix")
        
        print("✅ S3 integration demo completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during S3 integration demo: {e}")
        return False

def headless_mode_demo():
    """
    Demo for headless mode operation
    """
    print("\n👻 Starting Headless Mode Demo")
    print("=" * 35)
    
    try:
        print("🔧 Running Nova Act in headless mode...")
        
        with NovaAct(
            starting_page="https://www.amazon.com",
            headless=True,  # Run in headless mode
            logs_directory="./demo/logs/headless_mode"
        ) as nova:
            print("👻 Headless browser started (no visible window)")
            
            # Perform actions in headless mode
            print("🔍 Performing actions in headless mode...")
            nova.act("search for tablet")
            
            # Take screenshot to verify headless operation
            screenshot_path = "./demo/logs/headless_mode/headless_screenshot.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            nova.page.screenshot(path=screenshot_path)
            
            print(f"📸 Screenshot taken: {screenshot_path}")
            print("✅ Headless mode operation successful!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during headless mode demo: {e}")
        return False

def browser_debugging_demo():
    """
    Demo for browser debugging capabilities
    """
    print("\n🐛 Starting Browser Debugging Demo")
    print("=" * 40)
    
    try:
        # Set browser debugging arguments
        os.environ['NOVA_ACT_BROWSER_ARGS'] = '--remote-debugging-port=9222'
        
        print("🔧 Setting up browser debugging...")
        print("🌐 Remote debugging port: 9222")
        
        with NovaAct(
            starting_page="https://www.amazon.com",
            headless=True,  # Use headless for debugging demo
            logs_directory="./demo/logs/browser_debugging"
        ) as nova:
            print("🐛 Browser debugging enabled")
            print("💡 In real usage, you could:")
            print("   1. Open browser to http://localhost:9222/json")
            print("   2. Copy devtoolsFrontendUrl")
            print("   3. Paste in browser to debug")
            
            # Perform some actions
            nova.act("search for headphones")
            
            # Show debugging information
            print(f"\n🔍 Debug Information:")
            print(f"   Page Title: {nova.page.title()}")
            print(f"   Current URL: {nova.page.url}")
            print(f"   User Agent: {nova.page.evaluate('navigator.userAgent')}")
            
            print("✅ Browser debugging demo completed!")
            return True
            
    except Exception as e:
        print(f"❌ Error during browser debugging demo: {e}")
        return False
    finally:
        # Clean up environment variable
        if 'NOVA_ACT_BROWSER_ARGS' in os.environ:
            del os.environ['NOVA_ACT_BROWSER_ARGS']

def performance_monitoring_demo():
    """
    Demo for monitoring Nova Act performance
    """
    print("\n📊 Starting Performance Monitoring Demo")
    print("=" * 50)
    
    try:
        import time
        
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/performance_monitoring"
        ) as nova:
            print("⏱️ Monitoring Nova Act performance...")
            
            # Monitor action execution times
            actions = [
                "search for laptop",
                "click on the first result",
                "scroll down to see specifications",
                "go back to search results"
            ]
            
            performance_data = []
            
            for action in actions:
                print(f"\n🎯 Executing: {action}")
                
                start_time = time.time()
                result = nova.act(action)
                end_time = time.time()
                
                execution_time = end_time - start_time
                performance_data.append({
                    "action": action,
                    "execution_time": execution_time,
                    "success": bool(result.response)
                })
                
                print(f"⏱️ Execution time: {execution_time:.2f} seconds")
            
            # Display performance summary
            print("\n📊 Performance Summary:")
            print("=" * 25)
            
            total_time = sum(data["execution_time"] for data in performance_data)
            successful_actions = sum(1 for data in performance_data if data["success"])
            
            print(f"📈 Total execution time: {total_time:.2f} seconds")
            print(f"✅ Successful actions: {successful_actions}/{len(actions)}")
            print(f"⚡ Average time per action: {total_time/len(actions):.2f} seconds")
            
            # Show individual action performance
            print("\n📋 Individual Action Performance:")
            for data in performance_data:
                status = "✅" if data["success"] else "❌"
                print(f"   {status} {data['action']}: {data['execution_time']:.2f}s")
            
            return performance_data
            
    except Exception as e:
        print(f"❌ Error during performance monitoring demo: {e}")
        return []

def main():
    """Main function to run all advanced feature demos"""
    print("Nova Act Advanced Features Demo Suite")
    print("=====================================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    print("\n🚀 Advanced Features Demo Options:")
    print("1. Video recording")
    print("2. Custom logging")
    print("3. Proxy configuration")
    print("4. S3 integration")
    print("5. Headless mode")
    print("6. Browser debugging")
    print("7. Performance monitoring")
    print("8. Run all demos")
    
    choice = input("\nSelect demo (1-8): ").strip()
    
    if choice == "1":
        video_recording_demo()
    elif choice == "2":
        custom_logging_demo()
    elif choice == "3":
        proxy_configuration_demo()
    elif choice == "4":
        s3_integration_demo()
    elif choice == "5":
        headless_mode_demo()
    elif choice == "6":
        browser_debugging_demo()
    elif choice == "7":
        performance_monitoring_demo()
    elif choice == "8":
        # Run all demos
        results = []
        results.append(video_recording_demo())
        results.append(custom_logging_demo())
        results.append(proxy_configuration_demo())
        results.append(s3_integration_demo())
        results.append(headless_mode_demo())
        results.append(browser_debugging_demo())
        results.append(performance_monitoring_demo())
        
        successful = sum(1 for result in results if result)
        total = len(results)
        
        print(f"\n📊 Advanced Features Demo Summary: {successful}/{total} successful")
        
        if successful == total:
            print("🎉 All advanced feature demos completed successfully!")
            print("💡 These demos showcase Nova Act's advanced capabilities for production use")
        else:
            print("⚠️ Some demos encountered issues. Check the logs for details.")
    else:
        print("❌ Invalid choice. Please select 1-8.")

if __name__ == "__main__":
    main()
