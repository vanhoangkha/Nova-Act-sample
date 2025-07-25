#!/usr/bin/env python3
"""
Nova Act Demo: Enhanced Form Filling
====================================

This demo shows how to handle complex form filling operations with Nova Act,
including adaptive field detection, validation, and error recovery.
"""

import os
import sys
import time
from typing import Dict, Any, List
from nova_act import NovaAct, BOOL_SCHEMA

# Import our enhanced framework
from demo_framework import BaseDemo, DemoResult
from demo_framework.multi_selector import SelectorBuilder


class FormFillingDemo(BaseDemo):
    """Enhanced form filling demo with adaptive field detection."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 5  # Setup, Form site selection, Field detection, Form filling, Validation
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up Form Filling Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            return False
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites for form filling."""
        return [
            "https://httpbin.org/forms/post",
            "https://example.com",
            "https://httpbin.org/html"
        ]
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Step 1: Choose form site
            site_info = self._step_choose_form_site()
            extracted_data.update(site_info)
            self.increment_step("Form site selection completed")
            
            # Step 2: Analyze form structure
            form_analysis = self._step_analyze_form(site_info["target_site"])
            extracted_data.update(form_analysis)
            self.increment_step("Form analysis completed")
            
            # Step 3: Fill form fields
            filling_result = self._step_fill_form(site_info["target_site"], form_analysis.get("form_fields", []))
            extracted_data.update(filling_result)
            self.increment_step("Form filling completed")
            
            # Step 4: Validate form data
            validation_result = self._step_validate_form(site_info["target_site"])
            extracted_data.update(validation_result)
            self.increment_step("Form validation completed")
            
            # Step 5: Handle form submission (demo mode)
            submission_result = self._step_handle_submission(site_info["target_site"])
            extracted_data.update(submission_result)
            self.increment_step("Form submission handling completed")
            
        except Exception as e:
            self.logger.error(f"Error during form filling: {str(e)}")
            raise
        
        return extracted_data
    
    def _step_choose_form_site(self) -> Dict[str, Any]:
        """Step 1: Choose appropriate site for form filling demo."""
        self.logger.log_step(1, "Form Site Selection", "starting")
        
        # Sites with forms for testing
        form_sites = [
            {
                "url": "https://httpbin.org/forms/post",
                "name": "HTTPBin Form",
                "type": "test_form",
                "has_multiple_fields": True
            },
            {
                "url": "https://httpbin.org/html",
                "name": "HTTPBin HTML",
                "type": "simple_html",
                "has_multiple_fields": False
            }
        ]
        
        # Choose first accessible site
        target_site = None
        for site in form_sites:
            if self.config_manager.validate_site_access(site["url"]):
                target_site = site
                break
        
        if not target_site:
            # Use fallback
            fallback_sites = self.get_fallback_sites()
            target_site = {
                "url": fallback_sites[0],
                "name": "Fallback Form Site",
                "type": "fallback",
                "has_multiple_fields": True
            }
            self.add_warning("Using fallback site for form filling demo")
        
        self.logger.log_step(1, "Form Site Selection", "completed", f"Selected {target_site['name']}")
        self.logger.log_data_extraction("target_site", target_site, "site_selection")
        
        return {"target_site": target_site}
    
    def _step_analyze_form(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Analyze form structure and detect fields."""
        self.logger.log_step(2, "Form Analysis", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/form_analysis"
            ) as nova:
                
                # Detect form fields using multiple strategies
                form_fields = []
                
                # Strategy 1: Look for common form elements
                common_fields = self._detect_common_fields(nova)
                form_fields.extend(common_fields)
                
                # Strategy 2: Use Playwright to inspect form elements
                playwright_fields = self._detect_playwright_fields(nova)
                form_fields.extend(playwright_fields)
                
                # Strategy 3: Use Nova Act to describe the form
                description_fields = self._detect_description_fields(nova)
                form_fields.extend(description_fields)
                
                # Remove duplicates and organize
                unique_fields = self._deduplicate_fields(form_fields)
                
                form_analysis = {
                    "total_fields_detected": len(unique_fields),
                    "form_fields": unique_fields,
                    "detection_methods": ["common_patterns", "playwright_inspection", "ai_description"],
                    "form_type": site_info.get("type", "unknown")
                }
                
                self.logger.log_step(2, "Form Analysis", "completed", 
                                   f"Detected {len(unique_fields)} form fields")
                self.logger.log_data_extraction("form_analysis", form_analysis, "form_detection")
                
                return form_analysis
                
        except Exception as e:
            self.logger.log_step(2, "Form Analysis", "failed", str(e))
            return {
                "form_fields": [],
                "analysis_error": str(e),
                "total_fields_detected": 0
            }
    
    def _detect_common_fields(self, nova) -> List[Dict[str, Any]]:
        """Detect common form fields using predefined patterns."""
        common_fields = []
        
        # Common field patterns
        field_patterns = [
            {"name": "name", "selectors": ["input[name*='name']", "#name", ".name-field"]},
            {"name": "email", "selectors": ["input[type='email']", "input[name*='email']", "#email"]},
            {"name": "phone", "selectors": ["input[type='tel']", "input[name*='phone']", "#phone"]},
            {"name": "message", "selectors": ["textarea", "input[name*='message']", "#message"]},
            {"name": "subject", "selectors": ["input[name*='subject']", "#subject"]},
            {"name": "company", "selectors": ["input[name*='company']", "#company"]},
        ]
        
        for pattern in field_patterns:
            for selector in pattern["selectors"]:
                try:
                    elements = nova.page.query_selector_all(selector)
                    if elements:
                        common_fields.append({
                            "name": pattern["name"],
                            "selector": selector,
                            "type": "common_pattern",
                            "found": True,
                            "count": len(elements)
                        })
                        break
                except:
                    continue
        
        return common_fields
    
    def _detect_playwright_fields(self, nova) -> List[Dict[str, Any]]:
        """Detect form fields using Playwright inspection."""
        playwright_fields = []
        
        try:
            # Find all input elements
            inputs = nova.page.query_selector_all("input")
            for i, input_elem in enumerate(inputs):
                try:
                    input_type = input_elem.get_attribute("type") or "text"
                    input_name = input_elem.get_attribute("name") or f"input_{i}"
                    input_placeholder = input_elem.get_attribute("placeholder") or ""
                    
                    playwright_fields.append({
                        "name": input_name,
                        "type": "playwright_input",
                        "input_type": input_type,
                        "placeholder": input_placeholder,
                        "index": i
                    })
                except:
                    continue
            
            # Find all textarea elements
            textareas = nova.page.query_selector_all("textarea")
            for i, textarea in enumerate(textareas):
                try:
                    textarea_name = textarea.get_attribute("name") or f"textarea_{i}"
                    textarea_placeholder = textarea.get_attribute("placeholder") or ""
                    
                    playwright_fields.append({
                        "name": textarea_name,
                        "type": "playwright_textarea",
                        "placeholder": textarea_placeholder,
                        "index": i
                    })
                except:
                    continue
            
            # Find all select elements
            selects = nova.page.query_selector_all("select")
            for i, select in enumerate(selects):
                try:
                    select_name = select.get_attribute("name") or f"select_{i}"
                    
                    playwright_fields.append({
                        "name": select_name,
                        "type": "playwright_select",
                        "index": i
                    })
                except:
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Playwright field detection failed: {e}")
        
        return playwright_fields
    
    def _detect_description_fields(self, nova) -> List[Dict[str, Any]]:
        """Detect form fields using AI description."""
        description_fields = []
        
        try:
            # Ask Nova Act to describe the form
            result = nova.act("What form fields are visible on this page? List them briefly.")
            
            if result.response:
                # Parse the response to extract field information
                # This is a simplified approach - in production you'd use more sophisticated parsing
                response_lower = result.response.lower()
                
                field_keywords = ["name", "email", "phone", "message", "subject", "company", "address"]
                for keyword in field_keywords:
                    if keyword in response_lower:
                        description_fields.append({
                            "name": keyword,
                            "type": "ai_description",
                            "mentioned_in_response": True,
                            "confidence": "medium"
                        })
                        
        except Exception as e:
            self.logger.warning(f"AI description field detection failed: {e}")
        
        return description_fields
    
    def _deduplicate_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate fields and merge information."""
        unique_fields = {}
        
        for field in fields:
            field_name = field.get("name", "unknown")
            
            if field_name not in unique_fields:
                unique_fields[field_name] = field
            else:
                # Merge information from multiple detection methods
                existing = unique_fields[field_name]
                existing["detection_methods"] = existing.get("detection_methods", [])
                existing["detection_methods"].append(field.get("type", "unknown"))
                
                # Prefer more specific information
                if field.get("selector") and not existing.get("selector"):
                    existing["selector"] = field["selector"]
                if field.get("input_type") and not existing.get("input_type"):
                    existing["input_type"] = field["input_type"]
        
        return list(unique_fields.values())
    
    def _step_fill_form(self, site_info: Dict[str, Any], form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 3: Fill form fields with test data."""
        self.logger.log_step(3, "Form Filling", "starting")
        
        if not form_fields:
            self.logger.log_step(3, "Form Filling", "skipped", "No form fields detected")
            return {"form_filling": {"skipped": True, "reason": "no_fields"}}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/form_filling"
            ) as nova:
                
                filling_results = []
                
                # Test data for different field types
                test_data = {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-0123",
                    "message": "This is a test message from Nova Act demo.",
                    "subject": "Nova Act Form Filling Demo",
                    "company": "Demo Company Inc.",
                    "address": "123 Demo Street, Test City, TC 12345"
                }
                
                for field in form_fields:
                    field_name = field.get("name", "unknown")
                    field_result = self._fill_single_field(nova, field, test_data.get(field_name, f"Test {field_name}"))
                    filling_results.append(field_result)
                    
                    # Brief pause between field fills
                    time.sleep(0.5)
                
                successful_fills = len([r for r in filling_results if r.get("success", False)])
                
                self.logger.log_step(3, "Form Filling", "completed", 
                                   f"{successful_fills}/{len(filling_results)} fields filled")
                
                return {
                    "form_filling": {
                        "results": filling_results,
                        "successful_count": successful_fills,
                        "total_fields": len(filling_results)
                    }
                }
                
        except Exception as e:
            self.logger.log_step(3, "Form Filling", "failed", str(e))
            return {"form_filling": {"failed": True, "error": str(e)}}
    
    def _fill_single_field(self, nova, field: Dict[str, Any], value: str) -> Dict[str, Any]:
        """Fill a single form field using multiple strategies."""
        field_name = field.get("name", "unknown")
        
        try:
            # Strategy 1: Use specific selector if available
            if field.get("selector"):
                try:
                    element = nova.page.query_selector(field["selector"])
                    if element:
                        element.fill(value)
                        return {
                            "field": field_name,
                            "success": True,
                            "method": "direct_selector",
                            "value": value
                        }
                except:
                    pass
            
            # Strategy 2: Use Nova Act natural language
            try:
                if field.get("input_type") == "email":
                    nova.act(f"fill in the email field with {value}")
                elif field.get("input_type") == "tel":
                    nova.act(f"fill in the phone number field with {value}")
                elif field_name == "message" or field.get("type") == "playwright_textarea":
                    nova.act(f"fill in the message or comment field with: {value}")
                else:
                    nova.act(f"fill in the {field_name} field with {value}")
                
                return {
                    "field": field_name,
                    "success": True,
                    "method": "natural_language",
                    "value": value
                }
                
            except Exception as e:
                # Strategy 3: Generic field filling
                try:
                    nova.act(f"find and fill any field related to {field_name} with {value}")
                    return {
                        "field": field_name,
                        "success": True,
                        "method": "generic_fill",
                        "value": value
                    }
                except:
                    return {
                        "field": field_name,
                        "success": False,
                        "method": "all_failed",
                        "error": str(e)
                    }
                    
        except Exception as e:
            return {
                "field": field_name,
                "success": False,
                "method": "exception",
                "error": str(e)
            }
    
    def _step_validate_form(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Validate form data after filling."""
        self.logger.log_step(4, "Form Validation", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/form_validation"
            ) as nova:
                
                validation_results = []
                
                # Check if form appears to be filled
                result = nova.act("Are the form fields filled with data?", schema=BOOL_SCHEMA)
                form_filled = result.matches_schema and result.parsed_response
                
                validation_results.append({
                    "check": "form_filled",
                    "result": form_filled,
                    "method": "ai_validation"
                })
                
                # Check for validation errors
                result = nova.act("Are there any validation errors or error messages visible?", schema=BOOL_SCHEMA)
                has_errors = result.matches_schema and result.parsed_response
                
                validation_results.append({
                    "check": "validation_errors",
                    "result": not has_errors,  # Success if no errors
                    "method": "error_detection"
                })
                
                # Check if submit button is enabled
                result = nova.act("Is the submit button enabled and clickable?", schema=BOOL_SCHEMA)
                submit_enabled = result.matches_schema and result.parsed_response
                
                validation_results.append({
                    "check": "submit_enabled",
                    "result": submit_enabled,
                    "method": "button_state"
                })
                
                successful_validations = len([r for r in validation_results if r.get("result", False)])
                
                self.logger.log_step(4, "Form Validation", "completed", 
                                   f"{successful_validations}/{len(validation_results)} validations passed")
                
                return {
                    "form_validation": {
                        "results": validation_results,
                        "successful_count": successful_validations,
                        "total_checks": len(validation_results)
                    }
                }
                
        except Exception as e:
            self.logger.log_step(4, "Form Validation", "failed", str(e))
            return {"form_validation": {"failed": True, "error": str(e)}}
    
    def _step_handle_submission(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Handle form submission (demo mode - don't actually submit)."""
        self.logger.log_step(5, "Form Submission", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/form_submission"
            ) as nova:
                
                # Look for submit button
                result = nova.act("Can you see a submit button or send button?", schema=BOOL_SCHEMA)
                submit_button_found = result.matches_schema and result.parsed_response
                
                submission_result = {
                    "submit_button_found": submit_button_found,
                    "actually_submitted": False,
                    "demo_mode": True,
                    "reason": "Demo safety - form not actually submitted"
                }
                
                if submit_button_found:
                    # For demo purposes, just identify the button but don't click it
                    nova.act("locate the submit button but do not click it")
                    self.add_warning("Submit button found but not clicked for demo safety")
                else:
                    self.add_warning("No submit button found on the form")
                
                self.logger.log_step(5, "Form Submission", "completed", "Demo submission handling completed")
                
                return {"form_submission": submission_result}
                
        except Exception as e:
            self.logger.log_step(5, "Form Submission", "failed", str(e))
            return {"form_submission": {"failed": True, "error": str(e)}}


def run_form_filling_demo():
    """Run the form filling demo."""
    print("📝 Starting Enhanced Form Filling Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = FormFillingDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted:
            print("\n📋 Form Filling Summary:")
            
            # Form analysis
            if "total_fields_detected" in result.data_extracted:
                fields_count = result.data_extracted["total_fields_detected"]
                print(f"   🔍 Form fields detected: {fields_count}")
            
            # Form filling results
            if "form_filling" in result.data_extracted:
                filling = result.data_extracted["form_filling"]
                if not filling.get("skipped"):
                    successful = filling.get("successful_count", 0)
                    total = filling.get("total_fields", 0)
                    print(f"   ✏️  Fields filled: {successful}/{total}")
            
            # Validation results
            if "form_validation" in result.data_extracted:
                validation = result.data_extracted["form_validation"]
                if not validation.get("failed"):
                    successful = validation.get("successful_count", 0)
                    total = validation.get("total_checks", 0)
                    print(f"   ✅ Validation checks: {successful}/{total} passed")
            
            # Submission status
            if "form_submission" in result.data_extracted:
                submission = result.data_extracted["form_submission"]
                button_found = submission.get("submit_button_found", False)
                print(f"   🚀 Submit button found: {button_found}")
                print(f"   🛡️  Demo mode: Form not actually submitted")
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
    print("Nova Act Enhanced Form Filling Demo")
    print("=" * 50)
    
    # Run the demo
    result = run_form_filling_demo()
    
    if result.success:
        print("\n🎉 Form filling demo completed successfully!")
        print("This demo showcased:")
        print("  • Multi-strategy form field detection")
        print("  • Adaptive form filling with fallback methods")
        print("  • Form validation and error checking")
        print("  • Safe demo mode without actual submission")
        print("  • Comprehensive logging of form interactions")
    else:
        print("\n⚠️ Demo encountered some issues, but this demonstrates:")
        print("  • Robust error handling in form operations")
        print("  • Graceful degradation when fields can't be detected")
        print("  • Safe handling of form submission scenarios")
    
    print("\n💡 Production Tips:")
    print("  • Always validate form data before submission")
    print("  • Implement proper error handling for form validation")
    print("  • Use secure methods for handling sensitive form data")
    print("  • Test forms across different browsers and devices")
    print("  • Implement CAPTCHA handling for production forms")


if __name__ == "__main__":
    main()