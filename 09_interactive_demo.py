#!/usr/bin/env python3
"""
Nova Act Demo: Interactive Mode Usage
====================================

This demo shows how to use Nova Act in interactive mode,
as described in the Nova Act README.
"""

import os
import sys
from nova_act import NovaAct, BOOL_SCHEMA

def interactive_session_demo():
    """
    Demo for using Nova Act in interactive mode
    """
    print("🎮 Starting Interactive Session Demo")
    print("=" * 45)
    print("This demo simulates interactive usage of Nova Act")
    print("In real usage, you would run this in a Python shell")
    print()
    
    try:
        # Initialize Nova Act (similar to interactive mode)
        nova = NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/interactive_session"
        )
        
        print("🚀 Starting Nova Act session...")
        nova.start()
        
        print("✅ Nova Act session started successfully!")
        print("🌐 Browser opened to Amazon.com")
        print()
        
        # Simulate interactive commands
        interactive_commands = [
            "search for wireless headphones",
            "select the first result",
            "scroll down to see product details",
            "check if this product has good reviews",
            "go back to search results",
            "look at the second product"
        ]
        
        for i, command in enumerate(interactive_commands, 1):
            print(f"Step {i}: {command}")
            
            # In real interactive mode, user would type this command
            print(f">>> nova.act('{command}')")
            
            # Execute the command
            result = nova.act(command)
            
            print(f"✅ Command executed successfully")
            print(f"📝 Response: {result.response[:100]}...")
            print()
            
            # Simulate user deciding to continue or stop
            if i < len(interactive_commands):
                print("Press Enter to continue to next step...")
                input()  # Wait for user input
        
        print("🎯 Interactive session completed!")
        print("In real usage, you could continue with more commands or call nova.stop()")
        
        # Stop the session
        nova.stop()
        print("🛑 Nova Act session stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during interactive demo: {e}")
        return False

def step_by_step_debugging_demo():
    """
    Demo for step-by-step debugging and inspection
    """
    print("\n🔍 Starting Step-by-Step Debugging Demo")
    print("=" * 50)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/debugging_session"
        ) as nova:
            print("🐛 Demonstrating debugging capabilities...")
            
            # Step 1: Initial action
            print("\n🔍 Step 1: Performing initial search")
            result1 = nova.act("search for laptop")
            print(f"✅ Search completed: {result1.response[:50]}...")
            
            # Debugging: Check current page state
            print("\n🔍 Debug: Checking current page state")
            page_title = nova.page.title()
            current_url = nova.page.url
            print(f"📄 Page title: {page_title}")
            print(f"🔗 Current URL: {current_url}")
            
            # Step 2: Verify search results
            print("\n🔍 Step 2: Verifying search results")
            verification = nova.act("Are there search results displayed on the page?", schema=BOOL_SCHEMA)
            
            if verification.matches_schema and verification.parsed_response:
                print("✅ Search results confirmed")
                
                # Step 3: Take screenshot for debugging
                print("\n📸 Debug: Taking screenshot")
                screenshot_path = "./demo/logs/debugging_session/debug_screenshot.png"
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                nova.page.screenshot(path=screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Step 4: Inspect page content
                print("\n🔍 Debug: Inspecting page content")
                page_content = nova.page.content()
                print(f"📄 Page content length: {len(page_content)} characters")
                
                # Step 5: Continue with next action
                print("\n🔍 Step 3: Selecting first result")
                result2 = nova.act("click on the first laptop result")
                print(f"✅ Selection completed: {result2.response[:50]}...")
                
                # Final verification
                print("\n🔍 Final verification")
                final_check = nova.act("Am I now viewing a specific laptop product page?", schema=BOOL_SCHEMA)
                
                if final_check.matches_schema and final_check.parsed_response:
                    print("✅ Successfully navigated to product page")
                    return True
                else:
                    print("❌ Navigation verification failed")
                    return False
            else:
                print("❌ Search results not found")
                return False
                
    except Exception as e:
        print(f"❌ Error during debugging demo: {e}")
        return False

def manual_intervention_demo():
    """
    Demo for handling manual intervention points
    """
    print("\n👤 Starting Manual Intervention Demo")
    print("=" * 45)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/manual_intervention"
        ) as nova:
            print("🤖 Demonstrating manual intervention points...")
            
            # Automated action
            print("\n🤖 Automated: Searching for products")
            nova.act("search for gaming laptop")
            
            # Check for potential issues requiring manual intervention
            print("\n🔍 Checking for issues requiring manual intervention...")
            
            # Check for CAPTCHA
            captcha_check = nova.act("Is there a CAPTCHA or robot verification on the screen?", schema=BOOL_SCHEMA)
            
            if captcha_check.matches_schema and captcha_check.parsed_response:
                print("🤖 CAPTCHA detected - manual intervention required")
                print("👤 In real usage, you would solve the CAPTCHA manually")
                print("⏸️ Pausing automation...")
                
                # Simulate manual intervention
                input("Press Enter after solving CAPTCHA (simulation)...")
                print("✅ Manual intervention completed")
            else:
                print("✅ No CAPTCHA detected - continuing automation")
            
            # Check for login requirement
            login_check = nova.act("Is there a sign-in or login prompt?", schema=BOOL_SCHEMA)
            
            if login_check.matches_schema and login_check.parsed_response:
                print("🔐 Login required - manual intervention point")
                print("👤 In real usage, you might:")
                print("   - Handle login programmatically")
                print("   - Pause for manual login")
                print("   - Skip this step")
                
                choice = input("Choose action (skip/manual): ").strip().lower()
                
                if choice == "manual":
                    print("👤 Manual login simulation...")
                    input("Press Enter after completing login...")
                    print("✅ Login completed")
                else:
                    print("⏭️ Skipping login for demo")
            else:
                print("✅ No login required")
            
            # Continue with automated actions
            print("\n🤖 Resuming automation...")
            nova.act("look at the first few laptop results")
            
            print("✅ Manual intervention demo completed")
            return True
            
    except Exception as e:
        print(f"❌ Error during manual intervention demo: {e}")
        return False

def breakpoint_simulation_demo():
    """
    Demo for simulating breakpoints in automation
    """
    print("\n⏸️ Starting Breakpoint Simulation Demo")
    print("=" * 45)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/breakpoint_simulation"
        ) as nova:
            print("🔍 Demonstrating breakpoint usage in automation...")
            
            # Action 1
            print("\n🎯 Action 1: Initial search")
            nova.act("search for wireless mouse")
            
            # Breakpoint 1
            print("\n⏸️ BREAKPOINT 1: Search completed")
            print("🔍 Current state: Search results displayed")
            print("💭 At this point, you could:")
            print("   - Inspect the results")
            print("   - Modify the search")
            print("   - Continue with selection")
            
            continue_choice = input("Continue to next action? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("🛑 Stopping at breakpoint")
                return True
            
            # Action 2
            print("\n🎯 Action 2: Applying filters")
            nova.act("apply price filter for items under $50")
            
            # Breakpoint 2
            print("\n⏸️ BREAKPOINT 2: Filters applied")
            print("🔍 Current state: Filtered results")
            print("💭 Checking if filters worked correctly...")
            
            filter_check = nova.act("Are the results now filtered by price?", schema=BOOL_SCHEMA)
            
            if filter_check.matches_schema and filter_check.parsed_response:
                print("✅ Filters applied successfully")
            else:
                print("⚠️ Filters may not have applied correctly")
                print("🔧 This is where you might debug or retry")
            
            continue_choice = input("Continue to final action? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("🛑 Stopping at breakpoint")
                return True
            
            # Action 3
            print("\n🎯 Action 3: Final selection")
            nova.act("select the first wireless mouse from the filtered results")
            
            # Final breakpoint
            print("\n⏸️ FINAL BREAKPOINT: Product selected")
            print("🔍 Current state: Product page")
            print("✅ Automation workflow completed with breakpoints")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during breakpoint simulation demo: {e}")
        return False

def interactive_exploration_demo():
    """
    Demo for interactive exploration of a website
    """
    print("\n🗺️ Starting Interactive Exploration Demo")
    print("=" * 50)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/interactive_exploration"
        ) as nova:
            print("🗺️ Interactive website exploration...")
            
            exploration_steps = [
                ("Explore main categories", "click on 'All' or categories menu to see what's available"),
                ("Check today's deals", "look for and click on 'Today's Deals' or similar"),
                ("Explore electronics", "navigate to Electronics section"),
                ("Check customer service", "look for customer service or help section"),
                ("Explore account options", "check what account-related options are available")
            ]
            
            for step_name, action in exploration_steps:
                print(f"\n🔍 Exploration: {step_name}")
                print(f"Action: {action}")
                
                # Execute exploration step
                result = nova.act(action)
                print(f"📝 Discovered: {result.response[:100]}...")
                
                # Ask user if they want to continue exploring
                continue_exploring = input("Continue exploring? (y/n): ").strip().lower()
                if continue_exploring != 'y':
                    print("🛑 Exploration stopped by user")
                    break
            
            print("✅ Interactive exploration completed")
            return True
            
    except Exception as e:
        print(f"❌ Error during interactive exploration demo: {e}")
        return False

def main():
    """Main function to run all interactive demos"""
    print("Nova Act Interactive Mode Demo Suite")
    print("====================================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    print("\n🎮 Interactive Demo Options:")
    print("1. Interactive session simulation")
    print("2. Step-by-step debugging")
    print("3. Manual intervention handling")
    print("4. Breakpoint simulation")
    print("5. Interactive exploration")
    print("6. Run all demos")
    
    choice = input("\nSelect demo (1-6): ").strip()
    
    if choice == "1":
        interactive_session_demo()
    elif choice == "2":
        step_by_step_debugging_demo()
    elif choice == "3":
        manual_intervention_demo()
    elif choice == "4":
        breakpoint_simulation_demo()
    elif choice == "5":
        interactive_exploration_demo()
    elif choice == "6":
        # Run all demos
        results = []
        results.append(interactive_session_demo())
        results.append(step_by_step_debugging_demo())
        results.append(manual_intervention_demo())
        results.append(breakpoint_simulation_demo())
        results.append(interactive_exploration_demo())
        
        successful = sum(1 for result in results if result)
        total = len(results)
        
        print(f"\n📊 Interactive Demo Summary: {successful}/{total} successful")
        
        if successful == total:
            print("🎉 All interactive demos completed successfully!")
            print("💡 These demos show how Nova Act can be used interactively for development and debugging")
        else:
            print("⚠️ Some demos encountered issues. Check the logs for details.")
    else:
        print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()
