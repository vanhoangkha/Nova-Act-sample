#!/usr/bin/env python3
"""
Nova Act Demo: Form Filling and Data Entry
==========================================

This demo shows how to fill out various types of forms using Nova Act,
including text inputs, dropdowns, checkboxes, radio buttons, and date pickers.
"""

import os
import sys
from datetime import datetime, timedelta
from nova_act import NovaAct, BOOL_SCHEMA

def basic_contact_form_demo():
    """
    Demo for filling out a basic contact form
    """
    print("📝 Starting Basic Contact Form Demo")
    print("=" * 40)
    
    # Sample contact information
    contact_info = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "company": "Acme Corporation",
        "message": "This is a test message from Nova Act automation demo."
    }
    
    try:
        with NovaAct(
            starting_page="https://www.w3schools.com/html/html_forms.asp",
            logs_directory="./demo/logs/contact_form"
        ) as nova:
            print("🌐 Navigating to form page...")
            
            # Look for a contact form or create a test scenario
            nova.act("scroll down to find any form with input fields")
            
            # Fill out form fields step by step
            print("✍️ Filling out contact form...")
            
            # First name
            nova.act(f"find the first name field and enter '{contact_info['first_name']}'")
            
            # Last name
            nova.act(f"find the last name field and enter '{contact_info['last_name']}'")
            
            # Email
            nova.act(f"find the email field and enter '{contact_info['email']}'")
            
            # Phone (if available)
            nova.act(f"if there's a phone field, enter '{contact_info['phone']}'")
            
            # Message/Comments
            nova.act(f"find a message or comments field and enter '{contact_info['message']}'")
            
            # Verify form completion
            result = nova.act("Are all the form fields filled out correctly?", schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Contact form filled successfully!")
                
                # Submit form (but don't actually submit in demo)
                print("📤 Form ready for submission (not submitting in demo)")
                return True
            else:
                print("❌ Form filling incomplete or incorrect")
                return False
                
    except Exception as e:
        print(f"❌ Error during contact form demo: {e}")
        return False

def registration_form_demo():
    """
    Demo for filling out a user registration form
    """
    print("\n👤 Starting Registration Form Demo")
    print("=" * 40)
    
    # Sample registration data
    registration_data = {
        "username": "johndoe123",
        "email": "john.doe@example.com",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "first_name": "John",
        "last_name": "Doe",
        "birth_date": "01/15/1990",
        "gender": "Male",
        "country": "United States",
        "agree_terms": True
    }
    
    try:
        with NovaAct(
            starting_page="https://demo.testfire.net/register.jsp",
            logs_directory="./demo/logs/registration_form"
        ) as nova:
            print("🌐 Navigating to registration page...")
            
            # Fill registration form
            print("✍️ Filling registration form...")
            
            # Username
            nova.act(f"find the username field and enter '{registration_data['username']}'")
            
            # Email
            nova.act(f"find the email field and enter '{registration_data['email']}'")
            
            # Password
            nova.act("click on the password field")
            nova.page.keyboard.type(registration_data['password'])
            
            # Confirm password
            nova.act("click on the confirm password field")
            nova.page.keyboard.type(registration_data['confirm_password'])
            
            # Personal information
            nova.act(f"if there's a first name field, enter '{registration_data['first_name']}'")
            nova.act(f"if there's a last name field, enter '{registration_data['last_name']}'")
            
            # Date of birth (if available)
            nova.act(f"if there's a date of birth field, enter '{registration_data['birth_date']}'")
            
            # Gender dropdown (if available)
            nova.act(f"if there's a gender dropdown, select '{registration_data['gender']}'")
            
            # Country dropdown (if available)
            nova.act(f"if there's a country dropdown, select '{registration_data['country']}'")
            
            # Terms and conditions checkbox
            nova.act("if there's a terms and conditions checkbox, check it")
            
            # Verify form completion
            result = nova.act("Is the registration form completely filled out?", schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Registration form filled successfully!")
                return True
            else:
                print("❌ Registration form incomplete")
                return False
                
    except Exception as e:
        print(f"❌ Error during registration form demo: {e}")
        return False

def survey_form_demo():
    """
    Demo for filling out a survey with various input types
    """
    print("\n📊 Starting Survey Form Demo")
    print("=" * 35)
    
    # Sample survey responses
    survey_data = {
        "satisfaction": "Very Satisfied",
        "rating": "5",
        "feedback": "The service was excellent and exceeded my expectations.",
        "recommend": True,
        "improvements": ["Customer Service", "Website Design"],
        "contact_method": "Email"
    }
    
    try:
        with NovaAct(
            starting_page="https://forms.gle/sample-survey",  # Replace with actual survey
            logs_directory="./demo/logs/survey_form"
        ) as nova:
            print("🌐 Loading survey form...")
            
            # Handle different types of form elements
            print("✍️ Filling survey responses...")
            
            # Radio buttons for satisfaction
            nova.act(f"select '{survey_data['satisfaction']}' for the satisfaction question")
            
            # Rating scale
            nova.act(f"select rating '{survey_data['rating']}' out of 5 stars")
            
            # Text area for feedback
            nova.act(f"find the feedback text area and enter: '{survey_data['feedback']}'")
            
            # Yes/No question
            if survey_data['recommend']:
                nova.act("select 'Yes' for the recommendation question")
            else:
                nova.act("select 'No' for the recommendation question")
            
            # Multiple choice checkboxes
            for improvement in survey_data['improvements']:
                nova.act(f"check the checkbox for '{improvement}' in the improvements section")
            
            # Dropdown for contact method
            nova.act(f"select '{survey_data['contact_method']}' from the contact method dropdown")
            
            # Verify survey completion
            result = nova.act("Are all survey questions answered?", schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Survey completed successfully!")
                return True
            else:
                print("❌ Survey incomplete")
                return False
                
    except Exception as e:
        print(f"❌ Error during survey demo: {e}")
        return False

def date_picker_demo():
    """
    Demo for handling date picker controls
    """
    print("\n📅 Starting Date Picker Demo")
    print("=" * 35)
    
    # Calculate dates for demo
    today = datetime.now()
    start_date = today + timedelta(days=7)  # One week from now
    end_date = today + timedelta(days=14)   # Two weeks from now
    
    try:
        with NovaAct(
            starting_page="https://jqueryui.com/datepicker/",
            logs_directory="./demo/logs/date_picker"
        ) as nova:
            print("🌐 Navigating to date picker demo...")
            
            # Handle date picker
            print("📅 Working with date picker...")
            
            # Click on date input to open picker
            nova.act("click on the date input field to open the date picker")
            
            # Select start date
            nova.act(f"select {start_date.strftime('%B %d, %Y')} from the date picker")
            
            # If there's an end date field
            nova.act("if there's an end date field, click on it")
            nova.act(f"select {end_date.strftime('%B %d, %Y')} for the end date")
            
            # Verify dates are selected
            result = nova.act("Are the dates properly selected in the date fields?", schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Date picker demo completed successfully!")
                print(f"📅 Start date: {start_date.strftime('%B %d, %Y')}")
                print(f"📅 End date: {end_date.strftime('%B %d, %Y')}")
                return True
            else:
                print("❌ Date selection incomplete")
                return False
                
    except Exception as e:
        print(f"❌ Error during date picker demo: {e}")
        return False

def complex_form_demo():
    """
    Demo for handling a complex multi-step form
    """
    print("\n🔄 Starting Complex Multi-Step Form Demo")
    print("=" * 50)
    
    # Complex form data
    form_data = {
        "personal": {
            "title": "Mr.",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "date_of_birth": "01/15/1990"
        },
        "address": {
            "street": "123 Main Street",
            "city": "Anytown",
            "state": "California",
            "zip_code": "12345",
            "country": "United States"
        },
        "preferences": {
            "newsletter": True,
            "notifications": ["Email", "SMS"],
            "language": "English",
            "timezone": "Pacific Standard Time"
        }
    }
    
    try:
        with NovaAct(
            starting_page="https://example-complex-form.com",  # Replace with actual form
            logs_directory="./demo/logs/complex_form"
        ) as nova:
            print("🌐 Loading complex form...")
            
            # Step 1: Personal Information
            print("👤 Step 1: Personal Information")
            
            # Title dropdown
            nova.act(f"select '{form_data['personal']['title']}' from the title dropdown")
            
            # Name fields
            nova.act(f"enter '{form_data['personal']['first_name']}' in the first name field")
            nova.act(f"enter '{form_data['personal']['last_name']}' in the last name field")
            
            # Contact information
            nova.act(f"enter '{form_data['personal']['email']}' in the email field")
            nova.act(f"enter '{form_data['personal']['phone']}' in the phone field")
            
            # Date of birth
            nova.act(f"enter '{form_data['personal']['date_of_birth']}' in the date of birth field")
            
            # Proceed to next step
            nova.act("click 'Next' or 'Continue' to go to the next step")
            
            # Step 2: Address Information
            print("🏠 Step 2: Address Information")
            
            nova.act(f"enter '{form_data['address']['street']}' in the street address field")
            nova.act(f"enter '{form_data['address']['city']}' in the city field")
            nova.act(f"select '{form_data['address']['state']}' from the state dropdown")
            nova.act(f"enter '{form_data['address']['zip_code']}' in the zip code field")
            nova.act(f"select '{form_data['address']['country']}' from the country dropdown")
            
            # Proceed to next step
            nova.act("click 'Next' or 'Continue' to go to the next step")
            
            # Step 3: Preferences
            print("⚙️ Step 3: Preferences")
            
            # Newsletter subscription
            if form_data['preferences']['newsletter']:
                nova.act("check the newsletter subscription checkbox")
            
            # Notification preferences
            for notification in form_data['preferences']['notifications']:
                nova.act(f"check the '{notification}' notification option")
            
            # Language and timezone
            nova.act(f"select '{form_data['preferences']['language']}' from the language dropdown")
            nova.act(f"select '{form_data['preferences']['timezone']}' from the timezone dropdown")
            
            # Final verification
            result = nova.act("Is the entire form completed correctly across all steps?", schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Complex form completed successfully!")
                return True
            else:
                print("❌ Complex form incomplete")
                return False
                
    except Exception as e:
        print(f"❌ Error during complex form demo: {e}")
        return False

def form_validation_demo():
    """
    Demo for handling form validation and error messages
    """
    print("\n✅ Starting Form Validation Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://www.w3schools.com/html/html_form_validation.asp",
            logs_directory="./demo/logs/form_validation"
        ) as nova:
            print("🌐 Loading form validation demo...")
            
            # Test form validation by submitting incomplete form
            print("🧪 Testing form validation...")
            
            # Try to submit empty form
            nova.act("find a form and try to submit it without filling any fields")
            
            # Check for validation messages
            result = nova.act("Are there any validation error messages displayed?", schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                print("✅ Form validation working - error messages displayed")
                
                # Fill required fields to fix validation errors
                print("🔧 Fixing validation errors...")
                
                nova.act("fill in the required fields to resolve validation errors")
                
                # Try submitting again
                nova.act("submit the form again")
                
                # Check if validation passed
                result2 = nova.act("Did the form submit successfully without validation errors?", schema=BOOL_SCHEMA)
                
                if result2.matches_schema and result2.parsed_response:
                    print("✅ Form validation demo completed successfully!")
                    return True
                else:
                    print("⚠️ Form still has validation issues")
                    return False
            else:
                print("⚠️ No validation messages found")
                return False
                
    except Exception as e:
        print(f"❌ Error during form validation demo: {e}")
        return False

def main():
    """Main function to run all form filling demos"""
    print("Nova Act Form Filling Demo Suite")
    print("================================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    print("\n📝 Form Filling Demo Options:")
    print("1. Basic contact form")
    print("2. User registration form")
    print("3. Survey form with various inputs")
    print("4. Date picker handling")
    print("5. Complex multi-step form")
    print("6. Form validation handling")
    print("7. Run all demos")
    
    choice = input("\nSelect demo (1-7): ").strip()
    
    if choice == "1":
        basic_contact_form_demo()
    elif choice == "2":
        registration_form_demo()
    elif choice == "3":
        survey_form_demo()
    elif choice == "4":
        date_picker_demo()
    elif choice == "5":
        complex_form_demo()
    elif choice == "6":
        form_validation_demo()
    elif choice == "7":
        # Run all demos
        results = []
        results.append(basic_contact_form_demo())
        results.append(registration_form_demo())
        results.append(survey_form_demo())
        results.append(date_picker_demo())
        results.append(complex_form_demo())
        results.append(form_validation_demo())
        
        successful = sum(1 for result in results if result)
        total = len(results)
        
        print(f"\n📊 Form Filling Demo Summary: {successful}/{total} successful")
        
        if successful == total:
            print("🎉 All form filling demos completed successfully!")
        else:
            print("⚠️ Some demos encountered issues. Check the logs for details.")
    else:
        print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()
