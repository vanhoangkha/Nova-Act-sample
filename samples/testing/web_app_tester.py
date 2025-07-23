#!/usr/bin/env python3
"""
Web Application Testing Sample

This sample demonstrates how to use Nova Act for automated web application testing,
including functional testing, UI testing, and regression testing.
"""

import json
import time
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

from nova_act import NovaAct, BOOL_SCHEMA


class TestCase(BaseModel):
    test_id: str
    test_name: str
    description: str
    test_type: str  # functional, ui, integration, regression
    priority: str  # high, medium, low
    steps: List[str]
    expected_result: str
    preconditions: Optional[List[str]] = []


class TestResult(BaseModel):
    test_id: str
    test_name: str
    status: str  # passed, failed, skipped
    execution_time: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    actual_result: Optional[str] = None
    executed_at: str


class WebAppTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.test_results = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def execute_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case"""
        start_time = time.time()
        
        result = TestResult(
            test_id=test_case.test_id,
            test_name=test_case.test_name,
            status="failed",
            execution_time=0,
            executed_at=datetime.now().isoformat()
        )
        
        try:
            with NovaAct(starting_page=self.base_url) as nova:
                # Execute preconditions
                if test_case.preconditions:
                    for precondition in test_case.preconditions:
                        nova.act(precondition)
                        time.sleep(1)
                
                # Execute test steps
                for i, step in enumerate(test_case.steps):
                    try:
                        print(f"  Step {i+1}: {step}")
                        nova.act(step)
                        time.sleep(1)  # Small delay between steps
                    except Exception as e:
                        result.error_message = f"Failed at step {i+1}: {step}. Error: {str(e)}"
                        result.execution_time = time.time() - start_time
                        return result
                
                # Verify expected result
                verification_result = nova.act(
                    f"Verify that the following condition is met: {test_case.expected_result}",
                    schema=BOOL_SCHEMA
                )
                
                if verification_result.matches_schema and verification_result.parsed_response:
                    result.status = "passed"
                    result.actual_result = "Test passed - expected result verified"
                else:
                    result.status = "failed"
                    result.error_message = f"Expected result not met: {test_case.expected_result}"
                    
                    # Get actual result description
                    actual_result = nova.act(
                        "Describe what is currently visible on the page and the current state of the application"
                    )
                    result.actual_result = actual_result.response if actual_result.response else "Could not determine actual result"
                
                # Take screenshot for documentation
                try:
                    screenshot_path = f"test_screenshot_{test_case.test_id}_{self.session_id}.png"
                    nova.page.screenshot(path=screenshot_path)
                    result.screenshot_path = screenshot_path
                except Exception as e:
                    print(f"Could not take screenshot: {e}")
                
        except Exception as e:
            result.error_message = f"Test execution error: {str(e)}"
        
        result.execution_time = time.time() - start_time
        self.test_results.append(result)
        return result
    
    def execute_test_suite(self, test_cases: List[TestCase]) -> List[TestResult]:
        """Execute a complete test suite"""
        results = []
        
        print(f"🧪 Executing test suite with {len(test_cases)} test cases...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Running: {test_case.test_name}")
            
            result = self.execute_test_case(test_case)
            results.append(result)
            
            status_emoji = "✅" if result.status == "passed" else "❌"
            print(f"{status_emoji} {result.status.upper()} ({result.execution_time:.2f}s)")
            
            if result.error_message:
                print(f"   Error: {result.error_message}")
            
            # Small delay between tests
            time.sleep(2)
        
        return results
    
    def run_smoke_tests(self) -> List[TestResult]:
        """Run basic smoke tests for the web application"""
        smoke_tests = [
            TestCase(
                test_id="SMOKE_001",
                test_name="Page Load Test",
                description="Verify that the main page loads successfully",
                test_type="functional",
                priority="high",
                steps=["wait for the page to fully load"],
                expected_result="The page loads without errors and displays the main content"
            ),
            TestCase(
                test_id="SMOKE_002",
                test_name="Navigation Test",
                description="Verify that main navigation works",
                test_type="functional",
                priority="high",
                steps=[
                    "click on the main navigation menu",
                    "verify that navigation options are visible"
                ],
                expected_result="Navigation menu opens and displays menu items"
            ),
            TestCase(
                test_id="SMOKE_003",
                test_name="Search Functionality",
                description="Verify that search functionality works",
                test_type="functional",
                priority="medium",
                steps=[
                    "find the search box",
                    "enter 'test' in the search box",
                    "click the search button or press enter"
                ],
                expected_result="Search results are displayed or search is executed"
            )
        ]
        
        return self.execute_test_suite(smoke_tests)
    
    def run_form_tests(self, form_url: str) -> List[TestResult]:
        """Run tests specifically for form functionality"""
        form_tests = [
            TestCase(
                test_id="FORM_001",
                test_name="Form Validation - Required Fields",
                description="Test form validation for required fields",
                test_type="functional",
                priority="high",
                steps=[
                    f"navigate to {form_url}",
                    "try to submit the form without filling required fields",
                    "check for validation messages"
                ],
                expected_result="Form validation messages are displayed for required fields"
            ),
            TestCase(
                test_id="FORM_002",
                test_name="Form Submission - Valid Data",
                description="Test successful form submission with valid data",
                test_type="functional",
                priority="high",
                steps=[
                    f"navigate to {form_url}",
                    "fill in all required fields with valid data",
                    "submit the form"
                ],
                expected_result="Form is submitted successfully and confirmation is shown"
            ),
            TestCase(
                test_id="FORM_003",
                test_name="Form Reset Functionality",
                description="Test form reset button functionality",
                test_type="functional",
                priority="medium",
                steps=[
                    f"navigate to {form_url}",
                    "fill in some form fields",
                    "click the reset button if available"
                ],
                expected_result="Form fields are cleared when reset button is clicked"
            )
        ]
        
        return self.execute_test_suite(form_tests)
    
    def run_ui_tests(self) -> List[TestResult]:
        """Run UI-specific tests"""
        ui_tests = [
            TestCase(
                test_id="UI_001",
                test_name="Responsive Design Test",
                description="Test responsive design elements",
                test_type="ui",
                priority="medium",
                steps=[
                    "check if the page layout adapts to different screen sizes",
                    "verify that all elements are visible and accessible"
                ],
                expected_result="Page layout is responsive and elements are properly displayed"
            ),
            TestCase(
                test_id="UI_002",
                test_name="Button Interaction Test",
                description="Test button hover and click states",
                test_type="ui",
                priority="low",
                steps=[
                    "find interactive buttons on the page",
                    "hover over buttons to check hover effects",
                    "click buttons to verify they respond"
                ],
                expected_result="Buttons show appropriate hover effects and respond to clicks"
            ),
            TestCase(
                test_id="UI_003",
                test_name="Link Functionality Test",
                description="Test that links work correctly",
                test_type="ui",
                priority="medium",
                steps=[
                    "find links on the page",
                    "click on internal links",
                    "verify that links navigate to correct pages"
                ],
                expected_result="Links navigate to the correct destinations"
            )
        ]
        
        return self.execute_test_suite(ui_tests)
    
    def generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        if not self.test_results:
            return {"error": "No test results to report"}
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "passed"])
        failed_tests = len([r for r in self.test_results if r.status == "failed"])
        skipped_tests = len([r for r in self.test_results if r.status == "skipped"])
        
        # Calculate execution times
        execution_times = [r.execution_time for r in self.test_results]
        total_execution_time = sum(execution_times)
        avg_execution_time = total_execution_time / len(execution_times) if execution_times else 0
        
        # Group by test type
        test_types = {}
        for result in self.test_results:
            # Extract test type from test_id prefix
            test_type = result.test_id.split('_')[0].lower()
            if test_type not in test_types:
                test_types[test_type] = {"passed": 0, "failed": 0, "skipped": 0}
            test_types[test_type][result.status] += 1
        
        # Group by priority (if available in test cases)
        priority_stats = {"high": 0, "medium": 0, "low": 0}
        
        # Failed test analysis
        failed_test_details = [
            {
                "test_id": result.test_id,
                "test_name": result.test_name,
                "error_message": result.error_message,
                "execution_time": result.execution_time
            }
            for result in self.test_results if result.status == "failed"
        ]
        
        return {
            "test_session": {
                "session_id": self.session_id,
                "base_url": self.base_url,
                "execution_date": datetime.now().isoformat(),
                "total_execution_time": round(total_execution_time, 2)
            },
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "pass_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0,
                "average_execution_time": round(avg_execution_time, 2)
            },
            "test_type_breakdown": test_types,
            "failed_tests": failed_test_details,
            "performance_metrics": {
                "fastest_test": min(execution_times) if execution_times else 0,
                "slowest_test": max(execution_times) if execution_times else 0,
                "total_time": round(total_execution_time, 2)
            },
            "detailed_results": [result.dict() for result in self.test_results]
        }
    
    def save_test_report(self, filename: str = None):
        """Save test report to JSON file"""
        report = self.generate_test_report()
        
        if not filename:
            filename = f"test_report_{self.session_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Test report saved to {filename}")
    
    def create_custom_test_suite(self, test_definitions: List[Dict]) -> List[TestCase]:
        """Create custom test suite from test definitions"""
        test_cases = []
        
        for test_def in test_definitions:
            test_case = TestCase(
                test_id=test_def['test_id'],
                test_name=test_def['test_name'],
                description=test_def.get('description', ''),
                test_type=test_def.get('test_type', 'functional'),
                priority=test_def.get('priority', 'medium'),
                steps=test_def['steps'],
                expected_result=test_def['expected_result'],
                preconditions=test_def.get('preconditions', [])
            )
            test_cases.append(test_case)
        
        return test_cases


def main():
    # Configure the web application to test
    base_url = "https://example.com"  # Replace with actual URL
    
    tester = WebAppTester(base_url)
    
    print(f"🧪 Starting web application testing for: {base_url}")
    
    # Run different test suites
    print("\n🔥 Running Smoke Tests...")
    smoke_results = tester.run_smoke_tests()
    
    print("\n📝 Running Form Tests...")
    form_results = tester.run_form_tests(f"{base_url}/contact")  # Replace with actual form URL
    
    print("\n🎨 Running UI Tests...")
    ui_results = tester.run_ui_tests()
    
    # Custom test suite example
    print("\n⚙️ Running Custom Tests...")
    custom_test_definitions = [
        {
            "test_id": "CUSTOM_001",
            "test_name": "Login Functionality",
            "description": "Test user login functionality",
            "test_type": "functional",
            "priority": "high",
            "steps": [
                "click on the login button",
                "enter username 'testuser'",
                "enter password 'testpass'",
                "click submit"
            ],
            "expected_result": "User is logged in successfully",
            "preconditions": ["navigate to login page"]
        }
    ]
    
    custom_test_cases = tester.create_custom_test_suite(custom_test_definitions)
    custom_results = tester.execute_test_suite(custom_test_cases)
    
    # Generate and display report
    print("\n📊 Generating test report...")
    report = tester.generate_test_report()
    
    print(f"\n📈 Test Execution Summary:")
    print(f"  • Total Tests: {report['summary']['total_tests']}")
    print(f"  • Passed: {report['summary']['passed']} ({report['summary']['pass_rate']}%)")
    print(f"  • Failed: {report['summary']['failed']}")
    print(f"  • Total Time: {report['performance_metrics']['total_time']}s")
    print(f"  • Average Time: {report['summary']['average_execution_time']}s")
    
    if report['failed_tests']:
        print(f"\n❌ Failed Tests:")
        for failed_test in report['failed_tests']:
            print(f"  • {failed_test['test_name']}: {failed_test['error_message']}")
    
    print(f"\n🔧 Test Type Breakdown:")
    for test_type, stats in report['test_type_breakdown'].items():
        total_type = sum(stats.values())
        pass_rate = (stats['passed'] / total_type * 100) if total_type > 0 else 0
        print(f"  • {test_type.upper()}: {stats['passed']}/{total_type} passed ({pass_rate:.1f}%)")
    
    # Save detailed report
    tester.save_test_report()
    
    print(f"\n✅ Testing completed. Check test_report_{tester.session_id}.json for detailed results.")


if __name__ == "__main__":
    main()
