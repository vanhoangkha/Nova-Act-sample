#!/usr/bin/env python3
"""
Nova Act Demo: Authentication and Session Management
===================================================

This demo shows how to handle authentication, manage persistent browser sessions,
and work with cookies as described in the Nova Act README.
"""

import os
import sys
import getpass
from nova_act import NovaAct, BOOL_SCHEMA

def setup_persistent_session_demo():
    """
    Demo for setting up a persistent browser session with authentication
    """
    print("🔐 Starting Persistent Session Setup Demo")
    print("=" * 50)
    
    # Create user data directory
    user_data_dir = "./demo/user_data"
    os.makedirs(user_data_dir, exist_ok=True)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            user_data_dir=user_data_dir,
            clone_user_data_dir=False,  # Don't clone, use persistent directory
            logs_directory="./demo/logs/auth_setup"
        ) as nova:
            print("🌐 Navigating to Amazon...")
            
            # Check if already logged in
            result = nova.act("Am I already logged in to Amazon?", schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Already logged in!")
                return True
            
            print("🔑 Setting up authentication...")
            print("📝 Please log in manually when the browser opens")
            
            # Navigate to sign-in page
            nova.act("click on 'Sign in' or 'Hello, sign in' link")
            
            # Wait for manual authentication
            input("👤 Please complete the login process in the browser, then press Enter to continue...")
            
            # Verify login
            result = nova.act("Am I now logged in? Check if I can see my account name or 'Hello, [name]'", 
                            schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Successfully authenticated! Session saved for future use.")
                return True
            else:
                print("❌ Authentication verification failed")
                return False
                
    except Exception as e:
        print(f"❌ Error during authentication setup: {e}")
        return False

def use_persistent_session_demo():
    """
    Demo for using a previously authenticated session
    """
    print("\n🔄 Starting Persistent Session Usage Demo")
    print("=" * 50)
    
    user_data_dir = "./demo/user_data"
    
    if not os.path.exists(user_data_dir):
        print("❌ No persistent session found. Run setup first.")
        return False
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            user_data_dir=user_data_dir,
            clone_user_data_dir=False,  # Use the persistent session
            logs_directory="./demo/logs/auth_usage"
        ) as nova:
            print("🔍 Checking authentication status...")
            
            # Check if logged in
            result = nova.act("Am I logged in? Look for my account name or sign-in status", 
                            schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Successfully using persistent authenticated session!")
                
                # Perform authenticated actions
                print("📋 Accessing account information...")
                nova.act("click on 'Account & Lists' or similar account menu")
                
                print("🛒 Checking order history...")
                nova.act("look for and click on 'Your Orders' or 'Order History'")
                
                print("✅ Successfully performed authenticated actions!")
                return True
            else:
                print("❌ Session expired or authentication lost")
                return False
                
    except Exception as e:
        print(f"❌ Error using persistent session: {e}")
        return False

def secure_login_demo():
    """
    Demo for secure login with sensitive information handling
    """
    print("\n🔒 Starting Secure Login Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://example-login-site.com",  # Replace with actual site
            logs_directory="./demo/logs/secure_login"
        ) as nova:
            print("🔑 Demonstrating secure credential handling...")
            
            # Navigate to login form
            nova.act("find and click on the login or sign-in button")
            
            # Focus on username field
            print("👤 Focusing on username field...")
            nova.act("click on the username or email input field")
            
            # Get username securely (in real scenario, this could come from env var or secure storage)
            username = input("Enter username: ")
            nova.page.keyboard.type(username)
            
            # Focus on password field
            print("🔐 Focusing on password field...")
            nova.act("click on the password input field")
            
            # Get password securely without echoing to terminal
            password = getpass.getpass("Enter password: ")
            nova.page.keyboard.type(password)
            
            # Submit login
            print("📤 Submitting login...")
            nova.act("click the login or submit button")
            
            # Verify login success
            result = nova.act("Did the login succeed? Look for success indicators or error messages", 
                            schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed or unclear")
                return False
                
    except Exception as e:
        print(f"❌ Error during secure login: {e}")
        return False

def captcha_handling_demo():
    """
    Demo for handling captchas during authentication
    """
    print("\n🤖 Starting CAPTCHA Handling Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/captcha_handling"
        ) as nova:
            print("🔍 Checking for CAPTCHAs...")
            
            # Navigate to a page that might trigger captcha
            nova.act("click on sign in")
            
            # Check for captcha
            result = nova.act("Is there a captcha, robot verification, or security check on the screen?", 
                            schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("🤖 CAPTCHA detected!")
                print("👤 Manual intervention required...")
                
                # Pause for manual captcha solving
                input("Please solve the CAPTCHA in the browser and press Enter when done...")
                
                # Verify captcha was solved
                result2 = nova.act("Is the captcha now solved? Can I proceed with normal actions?", 
                                 schema=BOOL_SCHEMA)
                
                if result2.matches_schema and result2.parsed_response:
                    print("✅ CAPTCHA successfully resolved!")
                    return True
                else:
                    print("❌ CAPTCHA still present or unresolved")
                    return False
            else:
                print("✅ No CAPTCHA detected - proceeding normally")
                return True
                
    except Exception as e:
        print(f"❌ Error during CAPTCHA handling: {e}")
        return False

def parallel_authenticated_sessions_demo():
    """
    Demo for running multiple authenticated sessions in parallel
    """
    print("\n🔄 Starting Parallel Authenticated Sessions Demo")
    print("=" * 55)
    
    user_data_dir = "./demo/user_data"
    
    if not os.path.exists(user_data_dir):
        print("❌ No persistent session found. Run setup first.")
        return False
    
    from concurrent.futures import ThreadPoolExecutor
    
    def authenticated_task(task_id: int):
        """Perform a task with an authenticated session"""
        try:
            with NovaAct(
                starting_page="https://www.amazon.com",
                user_data_dir=user_data_dir,
                clone_user_data_dir=True,  # Clone for parallel use
                logs_directory=f"./demo/logs/parallel_auth_{task_id}"
            ) as nova:
                print(f"🔍 Task {task_id}: Checking authentication...")
                
                result = nova.act("Am I logged in?", schema=BOOL_SCHEMA)
                
                if result.matches_schema and result.parsed_response:
                    print(f"✅ Task {task_id}: Authenticated successfully")
                    
                    # Perform different tasks based on task_id
                    if task_id == 1:
                        nova.act("search for books")
                    elif task_id == 2:
                        nova.act("search for electronics")
                    else:
                        nova.act("search for home and garden")
                    
                    return f"Task {task_id} completed successfully"
                else:
                    return f"Task {task_id} authentication failed"
                    
        except Exception as e:
            return f"Task {task_id} error: {e}"
    
    # Run multiple authenticated sessions in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(authenticated_task, i) for i in range(1, 4)]
        
        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
                print(f"📊 {result}")
            except Exception as e:
                print(f"❌ Parallel task error: {e}")
    
    return results

def main():
    """Main function to run all authentication demos"""
    print("Nova Act Authentication & Session Management Demo Suite")
    print("======================================================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    print("🔐 Authentication Demo Options:")
    print("1. Setup persistent session (first time)")
    print("2. Use existing persistent session")
    print("3. Secure login demonstration")
    print("4. CAPTCHA handling demonstration")
    print("5. Parallel authenticated sessions")
    print("6. Run all demos")
    
    choice = input("\nSelect demo (1-6): ").strip()
    
    if choice == "1":
        setup_persistent_session_demo()
    elif choice == "2":
        use_persistent_session_demo()
    elif choice == "3":
        secure_login_demo()
    elif choice == "4":
        captcha_handling_demo()
    elif choice == "5":
        parallel_authenticated_sessions_demo()
    elif choice == "6":
        # Run all demos in sequence
        results = []
        results.append(setup_persistent_session_demo())
        results.append(use_persistent_session_demo())
        results.append(secure_login_demo())
        results.append(captcha_handling_demo())
        results.append(parallel_authenticated_sessions_demo())
        
        successful = sum(1 for result in results if result)
        total = len(results)
        
        print(f"\n📊 Authentication Demo Summary: {successful}/{total} successful")
        
        if successful == total:
            print("🎉 All authentication demos completed successfully!")
        else:
            print("⚠️ Some demos encountered issues. Check the logs for details.")
    else:
        print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()
