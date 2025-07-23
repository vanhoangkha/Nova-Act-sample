#!/usr/bin/env python3
"""
Form Automation Sample

This sample demonstrates how to automate form filling across different websites,
handle various input types, and manage form submissions with error handling.
"""

import json
import time
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

from nova_act import NovaAct, BOOL_SCHEMA


class FormField(BaseModel):
    field_name: str
    field_type: str  # text, email, select, checkbox, radio, textarea, etc.
    value: Any
    required: bool = False


class FormData(BaseModel):
    form_title: str
    fields: List[FormField]
    submit_button_text: Optional[str] = "Submit"


class FormSubmissionResult(BaseModel):
    success: bool
    form_url: str
    submission_time: str
    error_message: Optional[str] = None
    confirmation_message: Optional[str] = None


class FormAutomator:
    def __init__(self):
        self.submission_results = []
    
    def fill_form(self, form_url: str, form_data: FormData, wait_after_submit: int = 3) -> FormSubmissionResult:
        """Fill and submit a form on a website"""
        result = FormSubmissionResult(
            success=False,
            form_url=form_url,
            submission_time=datetime.now().isoformat()
        )
        
        try:
            with NovaAct(starting_page=form_url) as nova:
                # Wait for page to load
                time.sleep(2)
                
                # Check if form is present
                form_present = nova.act(
                    f"Is there a form on this page with title or heading '{form_data.form_title}'?",
                    schema=BOOL_SCHEMA
                )
                
                if not (form_present.matches_schema and form_present.parsed_response):
                    result.error_message = f"Form '{form_data.form_title}' not found on page"
                    return result
                
                # Fill each form field
                for field in form_data.fields:
                    try:
                        self._fill_field(nova, field)
                        print(f"✓ Filled field: {field.field_name}")
                    except Exception as e:
                        print(f"✗ Error filling field {field.field_name}: {e}")
                        if field.required:
                            result.error_message = f"Failed to fill required field: {field.field_name}"
                            return result
                
                # Submit the form
                submit_success = self._submit_form(nova, form_data.submit_button_text)
                
                if submit_success:
                    # Wait for submission to process
                    time.sleep(wait_after_submit)
                    
                    # Check for confirmation or error messages
                    confirmation_result = nova.act(
                        "Look for any confirmation message, success message, or error message after form submission. What does it say?",
                        schema={"type": "object", "properties": {"message": {"type": "string"}, "is_success": {"type": "boolean"}}}
                    )
                    
                    if confirmation_result.matches_schema:
                        confirmation_data = confirmation_result.parsed_response
                        result.confirmation_message = confirmation_data.get("message", "")
                        result.success = confirmation_data.get("is_success", True)
                    else:
                        result.success = True
                        result.confirmation_message = "Form submitted successfully"
                else:
                    result.error_message = "Failed to submit form"
                
        except Exception as e:
            result.error_message = f"Form automation error: {str(e)}"
        
        self.submission_results.append(result)
        return result
    
    def _fill_field(self, nova: NovaAct, field: FormField):
        """Fill a specific form field based on its type"""
        if field.field_type.lower() == "text" or field.field_type.lower() == "email":
            nova.act(f"find the {field.field_name} field and enter '{field.value}'")
        
        elif field.field_type.lower() == "textarea":
            nova.act(f"find the {field.field_name} textarea and enter the following text: {field.value}")
        
        elif field.field_type.lower() == "select" or field.field_type.lower() == "dropdown":
            nova.act(f"find the {field.field_name} dropdown and select '{field.value}'")
        
        elif field.field_type.lower() == "checkbox":
            if field.value:
                nova.act(f"find and check the {field.field_name} checkbox")
            else:
                nova.act(f"find and uncheck the {field.field_name} checkbox if it's checked")
        
        elif field.field_type.lower() == "radio":
            nova.act(f"find the {field.field_name} radio button group and select '{field.value}'")
        
        elif field.field_type.lower() == "date":
            nova.act(f"find the {field.field_name} date field and enter '{field.value}'")
        
        elif field.field_type.lower() == "number":
            nova.act(f"find the {field.field_name} number field and enter {field.value}")
        
        else:
            # Generic approach for unknown field types
            nova.act(f"find the {field.field_name} field and enter '{field.value}'")
    
    def _submit_form(self, nova: NovaAct, submit_button_text: str) -> bool:
        """Submit the form"""
        try:
            nova.act(f"click the '{submit_button_text}' button to submit the form")
            return True
        except Exception as e:
            print(f"Error submitting form: {e}")
            # Try alternative submit methods
            try:
                nova.act("click the submit button")
                return True
            except:
                try:
                    nova.act("press Enter to submit the form")
                    return True
                except:
                    return False
    
    def batch_form_submission(self, form_configs: List[Dict]) -> List[FormSubmissionResult]:
        """Submit multiple forms in batch"""
        results = []
        
        for config in form_configs:
            print(f"\n📝 Processing form: {config['form_data'].form_title}")
            print(f"🌐 URL: {config['url']}")
            
            result = self.fill_form(
                form_url=config['url'],
                form_data=config['form_data'],
                wait_after_submit=config.get('wait_time', 3)
            )
            
            if result.success:
                print(f"✅ Success: {result.confirmation_message}")
            else:
                print(f"❌ Failed: {result.error_message}")
            
            results.append(result)
            
            # Wait between form submissions to be respectful
            time.sleep(2)
        
        return results
    
    def generate_submission_report(self) -> Dict:
        """Generate a report of all form submissions"""
        if not self.submission_results:
            return {"error": "No form submissions to report"}
        
        successful_submissions = [r for r in self.submission_results if r.success]
        failed_submissions = [r for r in self.submission_results if not r.success]
        
        # Error analysis
        error_types = {}
        for result in failed_submissions:
            if result.error_message:
                error_types[result.error_message] = error_types.get(result.error_message, 0) + 1
        
        return {
            "report_generated": datetime.now().isoformat(),
            "summary": {
                "total_submissions": len(self.submission_results),
                "successful": len(successful_submissions),
                "failed": len(failed_submissions),
                "success_rate": (len(successful_submissions) / len(self.submission_results) * 100) if self.submission_results else 0
            },
            "error_analysis": error_types,
            "successful_submissions": [
                {
                    "url": result.form_url,
                    "submission_time": result.submission_time,
                    "confirmation": result.confirmation_message
                }
                for result in successful_submissions
            ],
            "failed_submissions": [
                {
                    "url": result.form_url,
                    "submission_time": result.submission_time,
                    "error": result.error_message
                }
                for result in failed_submissions
            ],
            "detailed_results": [result.dict() for result in self.submission_results]
        }
    
    def save_report(self, filename: str = None):
        """Save submission report to JSON file"""
        report = self.generate_submission_report()
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"form_automation_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Form automation report saved to {filename}")


def create_sample_form_configs() -> List[Dict]:
    """Create sample form configurations for testing"""
    
    # Contact form example
    contact_form = FormData(
        form_title="Contact Us",
        fields=[
            FormField(field_name="name", field_type="text", value="John Doe", required=True),
            FormField(field_name="email", field_type="email", value="john.doe@example.com", required=True),
            FormField(field_name="subject", field_type="text", value="Inquiry about services"),
            FormField(field_name="message", field_type="textarea", value="I would like to learn more about your services and pricing.", required=True)
        ],
        submit_button_text="Send Message"
    )
    
    # Newsletter signup example
    newsletter_form = FormData(
        form_title="Newsletter Signup",
        fields=[
            FormField(field_name="email", field_type="email", value="john.doe@example.com", required=True),
            FormField(field_name="first name", field_type="text", value="John"),
            FormField(field_name="subscribe", field_type="checkbox", value=True, required=True)
        ],
        submit_button_text="Subscribe"
    )
    
    # Job application example
    job_application_form = FormData(
        form_title="Job Application",
        fields=[
            FormField(field_name="full name", field_type="text", value="John Doe", required=True),
            FormField(field_name="email", field_type="email", value="john.doe@example.com", required=True),
            FormField(field_name="phone", field_type="text", value="(555) 123-4567"),
            FormField(field_name="position", field_type="select", value="Software Engineer"),
            FormField(field_name="experience", field_type="select", value="3-5 years"),
            FormField(field_name="cover letter", field_type="textarea", value="I am excited to apply for this position and believe my skills would be a great fit.")
        ],
        submit_button_text="Submit Application"
    )
    
    return [
        {
            "url": "https://example.com/contact",  # Replace with actual URLs
            "form_data": contact_form,
            "wait_time": 3
        },
        {
            "url": "https://example.com/newsletter",  # Replace with actual URLs
            "form_data": newsletter_form,
            "wait_time": 2
        },
        {
            "url": "https://example.com/careers/apply",  # Replace with actual URLs
            "form_data": job_application_form,
            "wait_time": 5
        }
    ]


def main():
    automator = FormAutomator()
    
    # Example 1: Single form submission
    print("📝 Example 1: Single Form Submission")
    
    single_form_data = FormData(
        form_title="Contact Form",
        fields=[
            FormField(field_name="name", field_type="text", value="Jane Smith", required=True),
            FormField(field_name="email", field_type="email", value="jane.smith@example.com", required=True),
            FormField(field_name="message", field_type="textarea", value="Hello, I'm interested in your services.", required=True)
        ]
    )
    
    # Replace with actual form URL
    form_url = "https://example.com/contact"
    
    print(f"Filling form at: {form_url}")
    result = automator.fill_form(form_url, single_form_data)
    
    if result.success:
        print(f"✅ Form submitted successfully: {result.confirmation_message}")
    else:
        print(f"❌ Form submission failed: {result.error_message}")
    
    # Example 2: Batch form submission
    print("\n📝 Example 2: Batch Form Submission")
    
    form_configs = create_sample_form_configs()
    
    print(f"Processing {len(form_configs)} forms...")
    batch_results = automator.batch_form_submission(form_configs)
    
    # Generate and display report
    print("\n📊 Generating submission report...")
    report = automator.generate_submission_report()
    
    print(f"\n📈 Submission Summary:")
    print(f"  • Total Forms: {report['summary']['total_submissions']}")
    print(f"  • Successful: {report['summary']['successful']}")
    print(f"  • Failed: {report['summary']['failed']}")
    print(f"  • Success Rate: {report['summary']['success_rate']:.1f}%")
    
    if report['summary']['failed'] > 0:
        print(f"\n❌ Common Errors:")
        for error, count in report['error_analysis'].items():
            print(f"  • {error}: {count} occurrences")
    
    # Save detailed report
    automator.save_report()


if __name__ == "__main__":
    main()
