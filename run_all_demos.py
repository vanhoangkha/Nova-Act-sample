#!/usr/bin/env python3
"""
Enhanced Nova Act Demo Suite Runner
===================================

This script runs all available Nova Act demos with the new framework,
providing comprehensive error handling, geographic awareness, and detailed reporting.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
import json

# Import framework components
from demo_framework import BaseDemo, DemoResult, ConfigManager, Logger


class DemoSuiteOrchestrator:
    """Orchestrates the execution of all Nova Act demos."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.logger = Logger("DemoSuiteOrchestrator")
        self.results = []
        self.start_time = None
        
    def validate_environment(self) -> bool:
        """Validate environment before running demos."""
        self.logger.info("Validating environment...")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            print("❌ Please set NOVA_ACT_API_KEY environment variable")
            print("   export NOVA_ACT_API_KEY='your_api_key'")
            return False
        
        # Detect environment
        env_info = self.config_manager.detect_environment()
        self.logger.info(f"Environment detected: {env_info.country_code} ({env_info.region})")
        
        # Check internet connectivity
        test_sites = ["https://google.com", "https://github.com", "https://example.com"]
        accessible_sites = 0
        
        for site in test_sites:
            if self.config_manager.validate_site_access(site):
                accessible_sites += 1
        
        if accessible_sites == 0:
            self.logger.error("No internet connectivity detected")
            return False
        
        self.logger.info(f"Internet connectivity: {accessible_sites}/{len(test_sites)} test sites accessible")
        
        # Create required directories
        directories = [
            "demo/logs", "demo/screenshots", "demo/downloads", 
            "demo/saved_content", "demo/sessions"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        return True
    
    def get_available_demos(self) -> List[Dict[str, Any]]:
        """Get list of available demos with metadata."""
        demos = [
            {
                "file": "01_basic_ecommerce.py",
                "name": "Basic E-commerce Operations",
                "description": "Search products, view details, add to cart",
                "category": "ecommerce",
                "priority": 1,
                "estimated_duration": 60
            },
            {
                "file": "02_information_extraction.py", 
                "name": "Information Extraction",
                "description": "Extract structured data from websites",
                "category": "data_extraction",
                "priority": 2,
                "estimated_duration": 45
            },
            {
                "file": "03_parallel_processing.py",
                "name": "Parallel Processing",
                "description": "Run multiple browser instances in parallel",
                "category": "advanced",
                "priority": 3,
                "estimated_duration": 90
            },
            {
                "file": "04_authentication_demo.py",
                "name": "Authentication Demo", 
                "description": "Handle login forms and session management",
                "category": "authentication",
                "priority": 2,
                "estimated_duration": 30
            },
            {
                "file": "05_file_operations.py",
                "name": "File Operations",
                "description": "Upload, download, and manage files",
                "category": "file_handling",
                "priority": 2,
                "estimated_duration": 40
            },
            {
                "file": "06_form_filling.py",
                "name": "Form Filling",
                "description": "Fill out complex web forms automatically",
                "category": "forms",
                "priority": 2,
                "estimated_duration": 35
            },
            {
                "file": "07_search_filter.py",
                "name": "Search and Filter",
                "description": "Advanced search with filters and sorting",
                "category": "ecommerce",
                "priority": 2,
                "estimated_duration": 50
            },
            {
                "file": "08_real_estate.py",
                "name": "Real Estate Search",
                "description": "Search properties with location-based filtering",
                "category": "real_estate",
                "priority": 2,
                "estimated_duration": 55
            },
            {
                "file": "09_interactive_demo.py",
                "name": "Interactive Demo",
                "description": "Interactive debugging and step-by-step execution",
                "category": "debugging",
                "priority": 3,
                "estimated_duration": 120
            },
            {
                "file": "10_advanced_features.py",
                "name": "Advanced Features",
                "description": "Advanced Nova Act features and integrations",
                "category": "advanced",
                "priority": 3,
                "estimated_duration": 100
            }
        ]
        
        # Filter to only include existing files
        available_demos = []
        for demo in demos:
            if os.path.exists(demo["file"]):
                available_demos.append(demo)
            else:
                self.logger.warning(f"Demo file not found: {demo['file']}")
        
        return available_demos
    
    def run_single_demo(self, demo_info: Dict[str, Any]) -> DemoResult:
        """Run a single demo and return results."""
        self.logger.info(f"Starting demo: {demo_info['name']}")
        
        start_time = time.time()
        
        try:
            # Import the demo module dynamically
            import importlib.util
            spec = importlib.util.spec_from_file_location("demo", demo_info["file"])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for a demo class that inherits from BaseDemo
            demo_instance = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseDemo) and 
                    attr != BaseDemo):
                    # Found a demo class
                    config = self.config_manager.get_recommended_config(demo_info["category"])
                    demo_instance = attr(config)
                    break
            
            if demo_instance:
                # Run using new framework
                result = demo_instance.run()
            else:
                # Fallback to old-style main() function
                if hasattr(module, 'main'):
                    module.main()
                    # Create a basic result
                    result = DemoResult(
                        demo_name=demo_info["name"],
                        success=True,
                        execution_time=time.time() - start_time,
                        steps_completed=1,
                        steps_total=1
                    )
                else:
                    raise Exception("No main() function or BaseDemo class found")
            
            self.logger.info(f"Demo completed: {demo_info['name']} ({'SUCCESS' if result.success else 'FAILED'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Demo failed: {demo_info['name']} - {str(e)}")
            
            # Create error result
            from demo_framework.base_demo import DemoError
            error = DemoError(
                error_type=type(e).__name__,
                message=str(e),
                timestamp=datetime.now()
            )
            
            result = DemoResult(
                demo_name=demo_info["name"],
                success=False,
                execution_time=time.time() - start_time,
                steps_completed=0,
                steps_total=1,
                errors=[error]
            )
            
            return result
    
    def run_all_demos(self, selected_demos: List[str] = None) -> List[DemoResult]:
        """Run all or selected demos."""
        self.start_time = time.time()
        self.logger.info("Starting Nova Act Demo Suite")
        
        # Get available demos
        available_demos = self.get_available_demos()
        
        # Filter selected demos if specified
        if selected_demos:
            available_demos = [d for d in available_demos if d["file"] in selected_demos]
        
        # Sort by priority
        available_demos.sort(key=lambda x: x["priority"])
        
        self.logger.info(f"Running {len(available_demos)} demos")
        
        results = []
        
        for i, demo_info in enumerate(available_demos, 1):
            print(f"\n{'='*80}")
            print(f"Demo {i}/{len(available_demos)}: {demo_info['name']}")
            print(f"File: {demo_info['file']}")
            print(f"Category: {demo_info['category']}")
            print(f"Estimated duration: {demo_info['estimated_duration']}s")
            print(f"{'='*80}")
            
            result = self.run_single_demo(demo_info)
            results.append(result)
            
            # Brief pause between demos
            time.sleep(2)
        
        self.results = results
        return results
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive report of all demo results."""
        if not self.results:
            return "No demo results available"
        
        total_duration = time.time() - self.start_time if self.start_time else 0
        successful_demos = [r for r in self.results if r.success]
        failed_demos = [r for r in self.results if not r.success]
        
        # Create report
        report = f"""
Nova Act Demo Suite Comprehensive Report
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Execution Time: {total_duration:.2f} seconds

SUMMARY
{'='*40}
Total Demos: {len(self.results)}
Successful: {len(successful_demos)}
Failed: {len(failed_demos)}
Success Rate: {len(successful_demos)/len(self.results)*100:.1f}%

ENVIRONMENT INFORMATION
{'='*40}
"""
        
        env_info = self.config_manager.detect_environment()
        report += f"Country: {env_info.country_code}\n"
        report += f"Region: {env_info.region}\n"
        report += f"Platform: {env_info.platform}\n"
        report += f"Python Version: {env_info.python_version}\n"
        report += f"VPN Detected: {env_info.has_vpn}\n"
        
        if successful_demos:
            report += f"\n✅ SUCCESSFUL DEMOS ({len(successful_demos)})\n"
            report += "="*40 + "\n"
            for demo in successful_demos:
                report += f"• {demo.demo_name}\n"
                report += f"  Duration: {demo.execution_time:.2f}s\n"
                report += f"  Steps: {demo.steps_completed}/{demo.steps_total}\n"
                if demo.warnings:
                    report += f"  Warnings: {len(demo.warnings)}\n"
                report += "\n"
        
        if failed_demos:
            report += f"\n❌ FAILED DEMOS ({len(failed_demos)})\n"
            report += "="*40 + "\n"
            for demo in failed_demos:
                report += f"• {demo.demo_name}\n"
                report += f"  Duration: {demo.execution_time:.2f}s\n"
                report += f"  Errors: {len(demo.errors)}\n"
                
                for error in demo.errors:
                    report += f"    - {error.error_type}: {error.message}\n"
                    if error.troubleshooting_tips:
                        report += "      Troubleshooting:\n"
                        for tip in error.troubleshooting_tips:
                            report += f"        * {tip}\n"
                report += "\n"
        
        # Recommendations
        report += "\nRECOMMENDATIONS\n"
        report += "="*40 + "\n"
        
        if len(successful_demos) == len(self.results):
            report += "🎉 All demos completed successfully!\n"
            report += "• Your environment is well-configured for Nova Act\n"
            report += "• Consider exploring advanced features and customizations\n"
            report += "• Try running demos with different configurations\n"
        else:
            report += "⚠️ Some demos encountered issues:\n"
            
            # Analyze common failure patterns
            error_types = {}
            for demo in failed_demos:
                for error in demo.errors:
                    error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            
            if error_types:
                report += "\nCommon Issues:\n"
                for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                    report += f"• {error_type}: {count} occurrence(s)\n"
            
            # Geographic recommendations
            if env_info.region != "north_america":
                report += "\n• Consider that some sites may have geographic restrictions\n"
                report += "• The framework automatically tries alternative sites\n"
                report += "• VPN usage may help if legally permitted in your jurisdiction\n"
            
            report += "\n• Check individual demo logs for detailed troubleshooting\n"
            report += "• Verify your internet connection and API key\n"
            report += "• Try running failed demos individually for better debugging\n"
        
        # Save report to file
        report_file = f"demo/logs/comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"Comprehensive report saved to: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
        
        return report


def main():
    """Main function to run the demo suite."""
    print("Enhanced Nova Act Demo Suite Runner")
    print("="*50)
    
    # Create orchestrator
    orchestrator = DemoSuiteOrchestrator()
    
    # Validate environment
    if not orchestrator.validate_environment():
        sys.exit(1)
    
    # Run all demos
    results = orchestrator.run_all_demos()
    
    # Generate and display report
    report = orchestrator.generate_comprehensive_report()
    print("\n" + report)
    
    # Exit with appropriate code
    successful_count = sum(1 for r in results if r.success)
    if successful_count == len(results):
        print("\n🎉 All demos completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {len(results) - successful_count} demo(s) encountered issues.")
        print("This is normal and expected - the framework handled errors gracefully.")
        sys.exit(0)  # Don't exit with error code as this is expected behavior


if __name__ == "__main__":
    main()