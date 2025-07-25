"""
Enhanced logging system for Nova Act demos.
"""

import logging
import os
from datetime import datetime
from typing import Optional
import json


class Logger:
    """Enhanced logger with structured output and file management."""
    
    def __init__(self, demo_name: str, log_level: str = "INFO"):
        self.demo_name = demo_name
        self.log_level = getattr(logging, log_level.upper())
        
        # Create log directory
        self.log_dir = "demo/logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"{demo_name}_{timestamp}.log")
        
        # Setup logger
        self.logger = logging.getLogger(f"nova_demo_{demo_name}")
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log session start
        self.info(f"=== Starting {demo_name} Demo Session ===")
        self.info(f"Log file: {self.log_file}")
    
    def info(self, message: str, extra_data: Optional[dict] = None):
        """Log info message with optional structured data."""
        self.logger.info(message)
        if extra_data:
            self._log_structured_data("INFO", message, extra_data)
    
    def warning(self, message: str, extra_data: Optional[dict] = None):
        """Log warning message with optional structured data."""
        self.logger.warning(message)
        if extra_data:
            self._log_structured_data("WARNING", message, extra_data)
    
    def error(self, message: str, extra_data: Optional[dict] = None):
        """Log error message with optional structured data."""
        self.logger.error(message)
        if extra_data:
            self._log_structured_data("ERROR", message, extra_data)
    
    def debug(self, message: str, extra_data: Optional[dict] = None):
        """Log debug message with optional structured data."""
        self.logger.debug(message)
        if extra_data:
            self._log_structured_data("DEBUG", message, extra_data)
    
    def log_action(self, action: str, target: str, result: str, duration: float = 0):
        """Log a specific action with structured format."""
        action_data = {
            "action": action,
            "target": target,
            "result": result,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        message = f"Action: {action} on {target} -> {result}"
        if duration > 0:
            message += f" ({duration:.2f}s)"
        
        self.info(message, action_data)
    
    def log_step(self, step_number: int, step_name: str, status: str, details: Optional[str] = None):
        """Log a demo step with structured format."""
        step_data = {
            "step_number": step_number,
            "step_name": step_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        message = f"Step {step_number}: {step_name} - {status}"
        if details:
            message += f" ({details})"
        
        self.info(message, step_data)
    
    def log_error_with_context(self, error: Exception, context: dict):
        """Log error with additional context information."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.error(f"Error: {type(error).__name__}: {str(error)}", error_data)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "seconds"):
        """Log performance metrics."""
        metric_data = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info(f"Performance: {metric_name} = {value} {unit}", metric_data)
    
    def log_data_extraction(self, data_type: str, data: dict, source: str):
        """Log extracted data with metadata."""
        extraction_data = {
            "data_type": data_type,
            "source": source,
            "extracted_data": data,
            "record_count": len(data) if isinstance(data, (list, dict)) else 1,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info(f"Data extracted: {data_type} from {source}", extraction_data)
    
    def _log_structured_data(self, level: str, message: str, data: dict):
        """Log structured data to a separate JSON log file."""
        json_log_file = self.log_file.replace('.log', '_structured.json')
        
        structured_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "demo_name": self.demo_name,
            "message": message,
            "data": data
        }
        
        try:
            with open(json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(structured_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write structured log: {e}")
    
    def create_summary_report(self, demo_result) -> str:
        """Create a summary report of the demo execution."""
        summary_file = self.log_file.replace('.log', '_summary.txt')
        
        summary_content = f"""
=== DEMO EXECUTION SUMMARY ===
Demo Name: {demo_result.demo_name}
Status: {'SUCCESS' if demo_result.success else 'FAILED'}
Execution Time: {demo_result.execution_time:.2f} seconds
Steps Completed: {demo_result.steps_completed}/{demo_result.steps_total}

=== ERRORS ({len(demo_result.errors)}) ===
"""
        
        for i, error in enumerate(demo_result.errors, 1):
            summary_content += f"""
Error {i}:
  Type: {error.error_type}
  Message: {error.message}
  Recovery Attempted: {error.recovery_attempted}
  Recovery Successful: {error.recovery_successful}
  Troubleshooting Tips:
"""
            for tip in error.troubleshooting_tips:
                summary_content += f"    - {tip}\n"
        
        summary_content += f"""
=== WARNINGS ({len(demo_result.warnings)}) ===
"""
        for i, warning in enumerate(demo_result.warnings, 1):
            summary_content += f"  {i}. {warning}\n"
        
        if demo_result.data_extracted:
            summary_content += f"""
=== DATA EXTRACTED ===
{json.dumps(demo_result.data_extracted, indent=2)}
"""
        
        summary_content += f"""
=== LOG FILES ===
Main Log: {self.log_file}
Structured Log: {self.log_file.replace('.log', '_structured.json')}
Summary: {summary_file}

=== RECOMMENDATIONS ===
"""
        
        if not demo_result.success:
            summary_content += "- Review the error messages above for specific issues\n"
            summary_content += "- Check your internet connection and geographic location\n"
            summary_content += "- Verify API keys and authentication settings\n"
            summary_content += "- Try running individual demo steps to isolate problems\n"
        else:
            summary_content += "- Demo completed successfully!\n"
            summary_content += "- Review extracted data for accuracy\n"
            summary_content += "- Consider running additional demos to explore more features\n"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            self.info(f"Summary report created: {summary_file}")
            return summary_file
            
        except Exception as e:
            self.error(f"Failed to create summary report: {e}")
            return ""
    
    def close(self):
        """Close logger and cleanup handlers."""
        self.info(f"=== Ending {self.demo_name} Demo Session ===")
        
        # Close all handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)