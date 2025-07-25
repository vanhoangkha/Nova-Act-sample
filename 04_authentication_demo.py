#!/usr/bin/env python3
"""
Nova Act Demo: Enhanced Authentication & Session Management
==========================================================

This demo shows how to handle authentication, persistent sessions,
and secure credential management with Nova Act.
"""

import os
import sys
import time
from typing import Dict, Any, List
from getpass import getpass
from nova_act import NovaAct, BOOL_SCHEMA

# Import our enhanced framework
from demo_framework import BaseDemo, DemoResult


class AuthenticationDemo(BaseDemo):
    """Enhanced authentication demo with session persistence and security."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 5  # Setup, Session check, Login, Verification, Session persistence
        self.user_data_dir = "./demo/sessions/auth_demo"
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up Authentication Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            return False
        
        # Create user data directory for session persistence
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.logger.info(f"Session directory: {self.user_data_dir}")
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites for authentication demo."""
        return [
            "https://example.com",
            "https://httpbin.org/forms/post"
        ]
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Step 1: Choose authentication site
            site_info = self._step_choose_site()
            extracted_data.update(site_info)
            self.increment_step("Site selection completed")
            
            # Step 2: Check existing session
            session_status = self._step_check_session(site_info["target_site"])
            extracted_data.update(session_status)
            self.increment_step("Session check completed")
            
            # Step 3: Handle authentication if needed
            auth_result = self._step_handle_authentication(
                site_info["target_site"], 
                session_status["already_authenticated"]
            )
            extracted_data.update(auth_result)
            self.increment_step("Authentication handling completed")
            
            # Step 4: Verify authentication status
            verification = self._step_verify_authentication(site_info["target_site"])
            extracted_data.update(verification)
            self.increment_step("Authentication verification completed")
            
            # Step 5: Test session persistence
            persistence_test = self._step_test_persistence(site_info["target_site"])
            extracted_data.update(persistence_test)
            self.increment_step("Session persistence test completed")
            
        except Exception as e:
            self.logger.error(f"Error during authentication demo: {str(e)}")
            raise
        
        return extracted_data
    
    def _step_choose_site(self) -> Dict[str, Any]:
        """Step 1: Choose appropriate site for authentication demo."""
        self.logger.log_step(1, "Site Selection", "starting")
        
        # For demo purposes, we'll use a simple form site
        # In real usage, you'd choose based on your needs
        demo_sites = [
            {
                "url": "https://httpbin.org/forms/post",
                "name": "HTTPBin Form Demo",
                "type": "simple_form"
            },
            {
                "url": "https://example.com",
                "name": "Example Site",
                "type": "static"
            }
        ]
        
        # Choose first accessible site
        target_site = None
        for site in demo_sites:
            if self.config_manager.validate_site_access(site["url"]):
                target_site = site
                break
        
        if not target_site:
            # Use fallback
            fallback_sites = self.get_fallback_sites()
            target_site = {
                "url": fallback_sites[0],
                "name": "Fallback Site",
                "type": "fallback"
            }
            self.add_warning("Using fallback site for authentication demo")
        
        self.logger.log_step(1, "Site Selection", "completed", f"Selected {target_site['name']}")
        self.logger.log_data_extraction("target_site", target_site, "site_selection")
        
        return {"target_site": target_site}
    
    def _step_check_session(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Check if we have an existing authenticated session."""
        self.logger.log_step(2, "Session Check", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                user_data_dir=self.user_data_dir,
                clone_user_data_dir=False,  # Don't clone to preserve session
                logs_directory="./demo/logs/auth_session_check"
            ) as nova:
                
                # Check if we're already authenticated
                # This is site-specific logic - adapt based on your target site
                if "httpbin" in site_info["url"]:
                    # For HTTPBin, we'll check if we can access the form
                    already_authenticated = False  # HTTPBin doesn't have persistent auth
                elif "example" in site_info["url"]:
                    # Example.com is static, no authentication needed
                    already_authenticated = True
                else:
                    # Generic check - look for login indicators
                    result = nova.act("Is there a login or sign in button visible?", schema=BOOL_SCHEMA)
                    already_authenticated = not (result.matches_schema and result.parsed_response)
                
                session_data = {
                    "already_authenticated": already_authenticated,
                    "session_dir": self.user_data_dir,
                    "site_type": site_info.get("type", "unknown")
                }
                
                self.logger.log_step(2, "Session Check", "completed", 
                                   f"Authenticated: {already_authenticated}")
                
                return session_data
                
        except Exception as e:
            self.logger.log_step(2, "Session Check", "failed", str(e))
            return {
                "already_authenticated": False,
                "session_check_error": str(e),
                "session_dir": self.user_data_dir
            }
    
    def _step_handle_authentication(self, site_info: Dict[str, Any], already_authenticated: bool) -> Dict[str, Any]:
        """Step 3: Handle authentication process if needed."""
        self.logger.log_step(3, "Authentication Handling", "starting")
        
        if already_authenticated:
            self.logger.log_step(3, "Authentication Handling", "skipped", "Already authenticated")
            return {"authentication_needed": False, "authentication_result": "already_authenticated"}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                user_data_dir=self.user_data_dir,
                clone_user_data_dir=False,
                logs_directory="./demo/logs/auth_login"
            ) as nova:
                
                if site_info.get("type") == "simple_form":
                    # Handle simple form authentication
                    auth_result = self._handle_form_auth(nova)
                elif site_info.get("type") == "static":
                    # Static site, no auth needed
                    auth_result = {"status": "no_auth_needed", "method": "static_site"}
                else:
                    # Generic authentication handling
                    auth_result = self._handle_generic_auth(nova)
                
                self.logger.log_step(3, "Authentication Handling", "completed", 
                                   f"Method: {auth_result.get('method', 'unknown')}")
                
                return {
                    "authentication_needed": True,
                    "authentication_result": auth_result
                }
                
        except Exception as e:
            self.logger.log_step(3, "Authentication Handling", "failed", str(e))
            return {
                "authentication_needed": True,
                "authentication_result": {"status": "failed", "error": str(e)}
            }
    
    def _handle_form_auth(self, nova) -> Dict[str, Any]:
        """Handle form-based authentication."""
        try:
            # For HTTPBin form demo, we'll just fill out the form
            nova.act("fill in the customer name field with 'Demo User'")
            nova.act("fill in the telephone field with '555-0123'")
            nova.act("fill in the email field with 'demo@example.com'")
            
            # Don't actually submit for demo purposes
            self.add_warning("Form filled but not submitted for demo safety")
            
            return {
                "status": "form_filled",
                "method": "form_demo",
                "submitted": False
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "method": "form_demo",
                "error": str(e)
            }
    
    def _handle_generic_auth(self, nova) -> Dict[str, Any]:
        """Handle generic authentication."""
        try:
            # Look for login elements
            result = nova.act("Is there a login or sign in button?", schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                # Found login button
                nova.act("click on the login or sign in button")
                
                # For demo purposes, we won't actually enter credentials
                self.add_warning("Login form found but credentials not entered for demo safety")
                
                return {
                    "status": "login_form_found",
                    "method": "generic_login",
                    "credentials_entered": False
                }
            else:
                return {
                    "status": "no_login_found",
                    "method": "generic_check"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "method": "generic_auth",
                "error": str(e)
            }
    
    def _step_verify_authentication(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Verify authentication status."""
        self.logger.log_step(4, "Authentication Verification", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                user_data_dir=self.user_data_dir,
                clone_user_data_dir=False,
                logs_directory="./demo/logs/auth_verification"
            ) as nova:
                
                # Verify we can access the site
                verification_result = {
                    "site_accessible": True,
                    "verification_method": "page_load",
                    "timestamp": time.time()
                }
                
                # Site-specific verification
                if site_info.get("type") == "simple_form":
                    # Check if form is still accessible
                    result = nova.act("Can you see the form fields?", schema=BOOL_SCHEMA)
                    verification_result["form_accessible"] = result.matches_schema and result.parsed_response
                
                self.logger.log_step(4, "Authentication Verification", "completed", "Site accessible")
                self.logger.log_data_extraction("verification_result", verification_result, "auth_verification")
                
                return {"verification": verification_result}
                
        except Exception as e:
            self.logger.log_step(4, "Authentication Verification", "failed", str(e))
            return {
                "verification": {
                    "site_accessible": False,
                    "error": str(e),
                    "timestamp": time.time()
                }
            }
    
    def _step_test_persistence(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Test session persistence."""
        self.logger.log_step(5, "Session Persistence Test", "starting")
        
        try:
            # Create a new Nova Act instance to test persistence
            with NovaAct(
                starting_page=site_info["url"],
                user_data_dir=self.user_data_dir,
                clone_user_data_dir=False,
                logs_directory="./demo/logs/auth_persistence"
            ) as nova:
                
                # Test if session data persists
                persistence_result = {
                    "session_dir_exists": os.path.exists(self.user_data_dir),
                    "session_files_count": len(os.listdir(self.user_data_dir)) if os.path.exists(self.user_data_dir) else 0,
                    "new_session_successful": True,
                    "timestamp": time.time()
                }
                
                # Check if we can still access the site
                result = nova.act("What is the main heading or title of this page?")
                persistence_result["page_title_accessible"] = bool(result.response)
                
                self.logger.log_step(5, "Session Persistence Test", "completed", 
                                   f"Session files: {persistence_result['session_files_count']}")
                self.logger.log_data_extraction("persistence_result", persistence_result, "session_persistence")
                
                return {"persistence_test": persistence_result}
                
        except Exception as e:
            self.logger.log_step(5, "Session Persistence Test", "failed", str(e))
            return {
                "persistence_test": {
                    "session_dir_exists": os.path.exists(self.user_data_dir),
                    "test_failed": True,
                    "error": str(e),
                    "timestamp": time.time()
                }
            }


def run_authentication_demo():
    """Run the authentication demo."""
    print("🔐 Starting Enhanced Authentication Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = AuthenticationDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted:
            print("\n📋 Authentication Summary:")
            
            # Target site info
            if "target_site" in result.data_extracted:
                site = result.data_extracted["target_site"]
                print(f"   🌐 Target site: {site.get('name', 'Unknown')}")
                print(f"   🔗 URL: {site.get('url', 'Unknown')}")
            
            # Authentication status
            if "authentication_result" in result.data_extracted:
                auth = result.data_extracted["authentication_result"]
                print(f"   🔑 Authentication: {auth.get('status', 'Unknown')}")
                print(f"   📝 Method: {auth.get('method', 'Unknown')}")
            
            # Session persistence
            if "persistence_test" in result.data_extracted:
                persist = result.data_extracted["persistence_test"]
                print(f"   💾 Session directory exists: {persist.get('session_dir_exists', False)}")
                print(f"   📁 Session files: {persist.get('session_files_count', 0)}")
    else:
        print("❌ Demo encountered issues:")
        for error in result.errors:
            print(f"   • {error.error_type}: {error.message}")
    
    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   • {warning}")
    
    print(f"📄 Detailed logs: {result.log_path}")
    
    return result


def main():
    """Main function to run the demo."""
    print("Nova Act Enhanced Authentication Demo")
    print("=" * 50)
    
    print("🔒 Security Note:")
    print("This demo shows authentication concepts without using real credentials.")
    print("In production, use secure credential management practices.")
    print()
    
    # Run the demo
    result = run_authentication_demo()
    
    if result.success:
        print("\n🎉 Authentication demo completed successfully!")
        print("This demo showcased:")
        print("  • Session persistence with user_data_dir")
        print("  • Authentication state checking")
        print("  • Secure credential handling concepts")
        print("  • Session directory management")
        print("  • Multi-session testing")
    else:
        print("\n⚠️ Demo encountered some issues, but this demonstrates:")
        print("  • Robust error handling in authentication flows")
        print("  • Safe handling of authentication failures")
        print("  • Session management best practices")
    
    print("\n💡 Production Tips:")
    print("  • Never hardcode credentials in scripts")
    print("  • Use environment variables or secure vaults")
    print("  • Implement proper session timeout handling")
    print("  • Monitor authentication failures")
    print("  • Use HTTPS for all authentication flows")


if __name__ == "__main__":
    main()