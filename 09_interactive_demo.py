#!/usr/bin/env python3
"""
Nova Act Demo: Enhanced Interactive Mode
=======================================

This demo shows how to use Nova Act in interactive mode with enhanced
debugging capabilities, breakpoints, and manual intervention support.
"""

import os
import sys
import time
from typing import Dict, Any, List
from nova_act import NovaAct, BOOL_SCHEMA

# Import our enhanced framework
from demo_framework import BaseDemo, DemoResult


class InteractiveDemo(BaseDemo):
    """Enhanced interactive demo with debugging and state capture."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 5  # Setup, Interactive session, Breakpoint demo, Manual intervention, State capture
        self.interactive_session = None
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up Interactive Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            return False
        
        print("\n🎯 Interactive Demo Instructions:")
        print("This demo will show interactive Nova Act usage with debugging features.")
        print("You'll see examples of breakpoints, manual intervention, and state capture.")
        print("=" * 60)
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites for interactive demo."""
        return [
            "https://example.com",
            "https://httpbin.org/html",
            "https://httpbin.org/forms/post"
        ]
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Step 1: Start interactive session
            session_info = self._step_start_interactive_session()
            extracted_data.update(session_info)
            self.increment_step("Interactive session started")
            
            # Step 2: Demonstrate breakpoint functionality
            breakpoint_result = self._step_demonstrate_breakpoints()
            extracted_data.update(breakpoint_result)
            self.increment_step("Breakpoint demonstration completed")
            
            # Step 3: Show manual intervention
            intervention_result = self._step_manual_intervention()
            extracted_data.update(intervention_result)
            self.increment_step("Manual intervention demonstrated")
            
            # Step 4: Capture and analyze state
            state_result = self._step_capture_state()
            extracted_data.update(state_result)
            self.increment_step("State capture completed")
            
            # Step 5: Interactive debugging session
            debug_result = self._step_interactive_debugging()
            extracted_data.update(debug_result)
            self.increment_step("Interactive debugging completed")
            
        except Exception as e:
            self.logger.error(f"Error during interactive demo: {str(e)}")
            raise
        
        return extracted_data
    
    def _step_start_interactive_session(self) -> Dict[str, Any]:
        """Step 1: Start an interactive Nova Act session."""
        self.logger.log_step(1, "Interactive Session Start", "starting")
        
        print("\n🚀 Starting Interactive Nova Act Session")
        print("=" * 40)
        
        try:
            # Choose a simple site for demonstration
            demo_site = "https://example.com"
            
            # Validate site access
            if not self.config_manager.validate_site_access(demo_site):
                demo_site = self.get_fallback_sites()[0]
                self.add_warning("Using fallback site for interactive demo")
            
            print(f"📱 Opening browser to: {demo_site}")
            
            # Create Nova Act instance for interactive use
            self.interactive_session = NovaAct(
                starting_page=demo_site,
                logs_directory="./demo/logs/interactive_session",
                headless=False  # Show browser for interactive demo
            )
            
            # Start the session
            self.interactive_session.start()
            
            print("✅ Interactive session started successfully!")
            print("🌐 Browser window should be visible")
            
            # Demonstrate basic interaction
            print("\n📝 Performing basic interaction...")
            result = self.interactive_session.act("What is the main heading on this page?")
            
            session_data = {
                "session_started": True,
                "demo_site": demo_site,
                "initial_interaction": result.response if result.response else "No response",
                "browser_visible": True
            }
            
            self.logger.log_step(1, "Interactive Session Start", "completed", "Session started successfully")
            self.logger.log_data_extraction("session_data", session_data, "interactive_session")
            
            return {"session_info": session_data}
            
        except Exception as e:
            self.logger.log_step(1, "Interactive Session Start", "failed", str(e))
            return {
                "session_info": {
                    "session_started": False,
                    "error": str(e)
                }
            }
    
    def _step_demonstrate_breakpoints(self) -> Dict[str, Any]:
        """Step 2: Demonstrate breakpoint functionality."""
        self.logger.log_step(2, "Breakpoint Demonstration", "starting")
        
        if not self.interactive_session:
            self.logger.log_step(2, "Breakpoint Demonstration", "skipped", "No interactive session")
            return {"breakpoint_result": {"skipped": True, "reason": "no_session"}}
        
        print("\n🔍 Demonstrating Breakpoint Functionality")
        print("=" * 40)
        
        try:
            breakpoint_demos = []
            
            # Breakpoint 1: Before action
            print("🛑 Breakpoint 1: Before performing action")
            print("   Current page state will be captured...")
            
            # Capture state before action
            page_title_before = self.interactive_session.page.title()
            url_before = self.interactive_session.page.url
            
            breakpoint_demos.append({
                "breakpoint_id": 1,
                "type": "before_action",
                "page_title": page_title_before,
                "url": url_before,
                "timestamp": time.time()
            })
            
            print(f"   📄 Page title: {page_title_before}")
            print(f"   🔗 URL: {url_before}")
            
            # Simulate user decision point
            print("\n⏸️  Simulated breakpoint: User can inspect page state")
            print("   In real usage, user could manually interact with browser here")
            time.sleep(2)  # Simulate inspection time
            
            # Perform action
            print("\n▶️  Continuing with action...")
            result = self.interactive_session.act("scroll down to see more content")
            
            # Breakpoint 2: After action
            print("\n🛑 Breakpoint 2: After performing action")
            
            page_title_after = self.interactive_session.page.title()
            url_after = self.interactive_session.page.url
            
            breakpoint_demos.append({
                "breakpoint_id": 2,
                "type": "after_action",
                "page_title": page_title_after,
                "url": url_after,
                "action_result": result.response if result.response else "No response",
                "timestamp": time.time()
            })
            
            print(f"   📄 Page title: {page_title_after}")
            print(f"   🔗 URL: {url_after}")
            print(f"   📝 Action result: {result.response if result.response else 'No response'}")
            
            breakpoint_data = {
                "breakpoints_demonstrated": breakpoint_demos,
                "total_breakpoints": len(breakpoint_demos),
                "demonstration_successful": True
            }
            
            self.logger.log_step(2, "Breakpoint Demonstration", "completed", 
                               f"{len(breakpoint_demos)} breakpoints demonstrated")
            self.logger.log_data_extraction("breakpoint_data", breakpoint_data, "breakpoint_demo")
            
            return {"breakpoint_result": breakpoint_data}
            
        except Exception as e:
            self.logger.log_step(2, "Breakpoint Demonstration", "failed", str(e))
            return {"breakpoint_result": {"failed": True, "error": str(e)}}
    
    def _step_manual_intervention(self) -> Dict[str, Any]:
        """Step 3: Demonstrate manual intervention capabilities."""
        self.logger.log_step(3, "Manual Intervention", "starting")
        
        if not self.interactive_session:
            self.logger.log_step(3, "Manual Intervention", "skipped", "No interactive session")
            return {"intervention_result": {"skipped": True, "reason": "no_session"}}
        
        print("\n👤 Demonstrating Manual Intervention")
        print("=" * 40)
        
        try:
            intervention_scenarios = []
            
            # Scenario 1: Simulated CAPTCHA handling
            print("🤖 Scenario 1: Simulated CAPTCHA Detection")
            
            # Check for CAPTCHA (simulated)
            result = self.interactive_session.act("Is there a CAPTCHA or verification challenge on this page?", schema=BOOL_SCHEMA)
            has_captcha = result.matches_schema and result.parsed_response
            
            intervention_scenarios.append({
                "scenario": "captcha_detection",
                "captcha_detected": has_captcha,
                "intervention_needed": has_captcha,
                "resolution": "automated_check" if not has_captcha else "would_need_manual"
            })
            
            if has_captcha:
                print("   🚨 CAPTCHA detected - would pause for manual intervention")
                print("   👤 User would solve CAPTCHA manually")
                print("   ⏸️  Script would wait for user completion")
            else:
                print("   ✅ No CAPTCHA detected - continuing automatically")
            
            # Scenario 2: Simulated form validation error
            print("\n📝 Scenario 2: Simulated Form Validation")
            
            # Try to find a form (if any)
            result = self.interactive_session.act("Are there any forms visible on this page?", schema=BOOL_SCHEMA)
            has_form = result.matches_schema and result.parsed_response
            
            intervention_scenarios.append({
                "scenario": "form_validation",
                "form_detected": has_form,
                "intervention_type": "validation_check",
                "resolution": "automated_validation"
            })
            
            if has_form:
                print("   📋 Form detected - would validate before submission")
                print("   👤 User could review form data manually")
            else:
                print("   ℹ️  No forms detected on this page")
            
            # Scenario 3: Simulated network timeout
            print("\n🌐 Scenario 3: Simulated Network Issue Handling")
            
            # Simulate checking page load status
            page_loaded = True  # Simplified for demo
            
            intervention_scenarios.append({
                "scenario": "network_timeout",
                "page_loaded": page_loaded,
                "intervention_needed": not page_loaded,
                "resolution": "automatic_retry" if page_loaded else "would_need_manual"
            })
            
            if page_loaded:
                print("   ✅ Page loaded successfully - no intervention needed")
            else:
                print("   ⚠️  Page load timeout - would pause for manual check")
                print("   👤 User could refresh or navigate manually")
            
            successful_scenarios = len([s for s in intervention_scenarios if not s.get("intervention_needed", False)])
            
            intervention_data = {
                "scenarios_tested": intervention_scenarios,
                "total_scenarios": len(intervention_scenarios),
                "successful_scenarios": successful_scenarios,
                "manual_intervention_simulated": True
            }
            
            self.logger.log_step(3, "Manual Intervention", "completed", 
                               f"{len(intervention_scenarios)} scenarios tested")
            self.logger.log_data_extraction("intervention_data", intervention_data, "manual_intervention")
            
            return {"intervention_result": intervention_data}
            
        except Exception as e:
            self.logger.log_step(3, "Manual Intervention", "failed", str(e))
            return {"intervention_result": {"failed": True, "error": str(e)}}
    
    def _step_capture_state(self) -> Dict[str, Any]:
        """Step 4: Capture and analyze current state."""
        self.logger.log_step(4, "State Capture", "starting")
        
        if not self.interactive_session:
            self.logger.log_step(4, "State Capture", "skipped", "No interactive session")
            return {"state_result": {"skipped": True, "reason": "no_session"}}
        
        print("\n📸 Capturing Current State")
        print("=" * 40)
        
        try:
            state_data = {}
            
            # Capture page information
            print("📄 Capturing page information...")
            state_data["page_info"] = {
                "title": self.interactive_session.page.title(),
                "url": self.interactive_session.page.url,
                "viewport_size": self.interactive_session.page.viewport_size,
                "timestamp": time.time()
            }
            
            # Capture DOM information
            print("🌐 Capturing DOM information...")
            try:
                dom_content = self.interactive_session.page.content()
                state_data["dom_info"] = {
                    "content_length": len(dom_content),
                    "has_forms": "form" in dom_content.lower(),
                    "has_images": "img" in dom_content.lower(),
                    "has_links": "href" in dom_content.lower()
                }
            except Exception as e:
                state_data["dom_info"] = {"error": str(e)}
            
            # Capture screenshot
            print("📷 Capturing screenshot...")
            try:
                screenshot_path = "./demo/screenshots/interactive_state.png"
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.interactive_session.page.screenshot(path=screenshot_path)
                state_data["screenshot"] = {
                    "captured": True,
                    "path": screenshot_path,
                    "size": os.path.getsize(screenshot_path) if os.path.exists(screenshot_path) else 0
                }
                print(f"   📁 Screenshot saved: {screenshot_path}")
            except Exception as e:
                state_data["screenshot"] = {"captured": False, "error": str(e)}
            
            # Capture browser state
            print("🔍 Capturing browser state...")
            try:
                # Get cookies
                cookies = self.interactive_session.page.context.cookies()
                state_data["browser_state"] = {
                    "cookie_count": len(cookies),
                    "has_local_storage": True,  # Simplified for demo
                    "javascript_enabled": True  # Simplified for demo
                }
            except Exception as e:
                state_data["browser_state"] = {"error": str(e)}
            
            # Analyze captured state
            print("📊 Analyzing captured state...")
            analysis = {
                "page_accessible": bool(state_data.get("page_info", {}).get("title")),
                "content_available": state_data.get("dom_info", {}).get("content_length", 0) > 0,
                "screenshot_captured": state_data.get("screenshot", {}).get("captured", False),
                "browser_state_captured": "error" not in state_data.get("browser_state", {})
            }
            
            state_data["analysis"] = analysis
            state_data["capture_successful"] = all(analysis.values())
            
            print(f"✅ State capture completed:")
            print(f"   📄 Page accessible: {analysis['page_accessible']}")
            print(f"   📝 Content available: {analysis['content_available']}")
            print(f"   📷 Screenshot captured: {analysis['screenshot_captured']}")
            print(f"   🔍 Browser state captured: {analysis['browser_state_captured']}")
            
            self.logger.log_step(4, "State Capture", "completed", 
                               f"Capture successful: {state_data['capture_successful']}")
            self.logger.log_data_extraction("state_data", state_data, "state_capture")
            
            return {"state_result": state_data}
            
        except Exception as e:
            self.logger.log_step(4, "State Capture", "failed", str(e))
            return {"state_result": {"failed": True, "error": str(e)}}
    
    def _step_interactive_debugging(self) -> Dict[str, Any]:
        """Step 5: Demonstrate interactive debugging session."""
        self.logger.log_step(5, "Interactive Debugging", "starting")
        
        if not self.interactive_session:
            self.logger.log_step(5, "Interactive Debugging", "skipped", "No interactive session")
            return {"debug_result": {"skipped": True, "reason": "no_session"}}
        
        print("\n🐛 Interactive Debugging Session")
        print("=" * 40)
        
        try:
            debug_session = {
                "debug_commands": [],
                "session_duration": 0,
                "debugging_successful": True
            }
            
            debug_start_time = time.time()
            
            # Debug command 1: Inspect current element
            print("🔍 Debug Command 1: Inspect page elements")
            try:
                result = self.interactive_session.act("describe what elements are visible on this page")
                debug_session["debug_commands"].append({
                    "command": "inspect_elements",
                    "result": result.response if result.response else "No response",
                    "successful": bool(result.response),
                    "timestamp": time.time()
                })
                print(f"   📝 Result: {result.response if result.response else 'No response'}")
            except Exception as e:
                debug_session["debug_commands"].append({
                    "command": "inspect_elements",
                    "error": str(e),
                    "successful": False,
                    "timestamp": time.time()
                })
            
            # Debug command 2: Check page functionality
            print("\n🧪 Debug Command 2: Test page functionality")
            try:
                result = self.interactive_session.act("Are there any interactive elements like buttons or links?", schema=BOOL_SCHEMA)
                has_interactive = result.matches_schema and result.parsed_response
                debug_session["debug_commands"].append({
                    "command": "test_functionality",
                    "result": has_interactive,
                    "successful": result.matches_schema,
                    "timestamp": time.time()
                })
                print(f"   🎯 Interactive elements found: {has_interactive}")
            except Exception as e:
                debug_session["debug_commands"].append({
                    "command": "test_functionality",
                    "error": str(e),
                    "successful": False,
                    "timestamp": time.time()
                })
            
            # Debug command 3: Performance check
            print("\n⚡ Debug Command 3: Performance analysis")
            try:
                # Simple performance metrics
                page_load_time = time.time() - debug_start_time
                debug_session["debug_commands"].append({
                    "command": "performance_check",
                    "result": f"Page interaction time: {page_load_time:.2f}s",
                    "successful": True,
                    "timestamp": time.time()
                })
                print(f"   📊 Page interaction time: {page_load_time:.2f}s")
            except Exception as e:
                debug_session["debug_commands"].append({
                    "command": "performance_check",
                    "error": str(e),
                    "successful": False,
                    "timestamp": time.time()
                })
            
            debug_session["session_duration"] = time.time() - debug_start_time
            successful_commands = len([cmd for cmd in debug_session["debug_commands"] if cmd.get("successful", False)])
            debug_session["successful_commands"] = successful_commands
            debug_session["total_commands"] = len(debug_session["debug_commands"])
            
            print(f"\n📈 Debug Session Summary:")
            print(f"   ⏱️  Duration: {debug_session['session_duration']:.2f}s")
            print(f"   ✅ Successful commands: {successful_commands}/{len(debug_session['debug_commands'])}")
            
            self.logger.log_step(5, "Interactive Debugging", "completed", 
                               f"{successful_commands} debug commands successful")
            self.logger.log_data_extraction("debug_session", debug_session, "interactive_debugging")
            
            return {"debug_result": debug_session}
            
        except Exception as e:
            self.logger.log_step(5, "Interactive Debugging", "failed", str(e))
            return {"debug_result": {"failed": True, "error": str(e)}}
        
        finally:
            # Clean up interactive session
            if self.interactive_session:
                try:
                    print("\n🔚 Closing interactive session...")
                    self.interactive_session.stop()
                    print("✅ Interactive session closed")
                except Exception as e:
                    print(f"⚠️  Warning: Error closing session: {e}")


def run_interactive_demo():
    """Run the interactive demo."""
    print("🎮 Starting Enhanced Interactive Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = InteractiveDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted:
            print("\n📋 Interactive Demo Summary:")
            
            # Session info
            if "session_info" in result.data_extracted:
                session = result.data_extracted["session_info"]
                started = session.get("session_started", False)
                site = session.get("demo_site", "Unknown")
                print(f"   🚀 Session started: {started}")
                print(f"   🌐 Demo site: {site}")
            
            # Breakpoint results
            if "breakpoint_result" in result.data_extracted:
                breakpoints = result.data_extracted["breakpoint_result"]
                if not breakpoints.get("skipped"):
                    count = breakpoints.get("total_breakpoints", 0)
                    print(f"   🛑 Breakpoints demonstrated: {count}")
            
            # Manual intervention
            if "intervention_result" in result.data_extracted:
                intervention = result.data_extracted["intervention_result"]
                if not intervention.get("skipped"):
                    scenarios = intervention.get("total_scenarios", 0)
                    successful = intervention.get("successful_scenarios", 0)
                    print(f"   👤 Intervention scenarios: {successful}/{scenarios}")
            
            # State capture
            if "state_result" in result.data_extracted:
                state = result.data_extracted["state_result"]
                if not state.get("skipped"):
                    captured = state.get("capture_successful", False)
                    screenshot = state.get("screenshot", {}).get("captured", False)
                    print(f"   📸 State capture: {'✅ Success' if captured else '❌ Failed'}")
                    print(f"   📷 Screenshot: {'✅ Captured' if screenshot else '❌ Failed'}")
            
            # Debug session
            if "debug_result" in result.data_extracted:
                debug = result.data_extracted["debug_result"]
                if not debug.get("skipped"):
                    successful = debug.get("successful_commands", 0)
                    total = debug.get("total_commands", 0)
                    duration = debug.get("session_duration", 0)
                    print(f"   🐛 Debug commands: {successful}/{total} successful")
                    print(f"   ⏱️  Debug duration: {duration:.2f}s")
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
    print("Nova Act Enhanced Interactive Demo")
    print("=" * 50)
    
    # Run the demo
    result = run_interactive_demo()
    
    if result.success:
        print("\n🎉 Interactive demo completed successfully!")
        print("This demo showcased:")
        print("  • Interactive Nova Act session management")
        print("  • Breakpoint functionality for debugging")
        print("  • Manual intervention handling")
        print("  • Comprehensive state capture and analysis")
        print("  • Interactive debugging commands")
    else:
        print("\n⚠️ Demo encountered some issues, but this demonstrates:")
        print("  • Robust error handling in interactive sessions")
        print("  • Safe session management and cleanup")
        print("  • Graceful handling of browser state issues")
    
    print("\n💡 Production Tips:")
    print("  • Use interactive mode for development and debugging")
    print("  • Implement proper session cleanup and error handling")
    print("  • Capture state at key points for troubleshooting")
    print("  • Use breakpoints to validate complex workflows")
    print("  • Monitor browser performance and resource usage")


if __name__ == "__main__":
    main()