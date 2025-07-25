"""
Base demo class providing common functionality for all Nova Act demos.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import traceback
import os

from .error_handler import ErrorHandler
from .logger import Logger
from .config_manager import ConfigManager


@dataclass
class DemoError:
    """Represents an error that occurred during demo execution."""
    error_type: str
    message: str
    timestamp: datetime
    recovery_attempted: bool = False
    recovery_successful: bool = False
    troubleshooting_tips: List[str] = field(default_factory=list)
    stack_trace: Optional[str] = None


@dataclass
class DemoResult:
    """Result of demo execution with detailed information."""
    demo_name: str
    success: bool
    execution_time: float
    steps_completed: int
    steps_total: int
    errors: List[DemoError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data_extracted: Optional[Dict[str, Any]] = None
    log_path: str = ""
    screenshots: List[str] = field(default_factory=list)


class BaseDemo(ABC):
    """Abstract base class for all Nova Act demos."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.demo_name = self.__class__.__name__
        self.logger = Logger(self.demo_name)
        self.error_handler = ErrorHandler()
        self.config_manager = ConfigManager()
        
        # Demo state
        self.start_time = None
        self.steps_completed = 0
        self.steps_total = 0
        self.errors = []
        self.warnings = []
        self.data_extracted = {}
        
        # Ensure required directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create required directories for logs, screenshots, etc."""
        directories = [
            "demo/logs",
            "demo/screenshots", 
            "demo/downloads",
            "demo/saved_content",
            "demo/sessions"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @abstractmethod
    def setup(self) -> bool:
        """
        Setup demo environment and validate prerequisites.
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        pass
    
    @abstractmethod
    def execute_steps(self) -> Dict[str, Any]:
        """
        Execute the main demo steps.
        
        Returns:
            Dict[str, Any]: Data extracted during demo execution
        """
        pass
    
    @abstractmethod
    def get_fallback_sites(self) -> List[str]:
        """
        Get list of alternative sites if primary site fails.
        
        Returns:
            List[str]: List of fallback site URLs
        """
        pass
    
    def cleanup(self) -> None:
        """Cleanup resources after demo execution."""
        self.logger.info("Demo cleanup completed")
    
    def run(self) -> DemoResult:
        """
        Run the complete demo with error handling and logging.
        
        Returns:
            DemoResult: Comprehensive result of demo execution
        """
        self.start_time = datetime.now()
        self.logger.info(f"Starting demo: {self.demo_name}")
        
        try:
            # Setup phase
            if not self.setup():
                return self._create_result(False, "Setup failed")
            
            # Execute main steps
            self.data_extracted = self.execute_steps()
            
            # Success
            self.logger.info(f"Demo {self.demo_name} completed successfully")
            return self._create_result(True, "Demo completed successfully")
            
        except Exception as e:
            self.logger.error(f"Demo failed with exception: {str(e)}")
            error = DemoError(
                error_type=type(e).__name__,
                message=str(e),
                timestamp=datetime.now(),
                stack_trace=traceback.format_exc()
            )
            self.errors.append(error)
            
            # Attempt recovery
            recovery_action = self.error_handler.handle_error(e, self)
            if recovery_action and recovery_action.should_retry:
                self.logger.info("Attempting error recovery...")
                error.recovery_attempted = True
                try:
                    # Retry with recovery action
                    if recovery_action.alternative_action:
                        recovery_action.alternative_action()
                    error.recovery_successful = True
                    return self._create_result(True, "Demo completed after recovery")
                except Exception as recovery_error:
                    self.logger.error(f"Recovery failed: {str(recovery_error)}")
                    error.recovery_successful = False
            
            return self._create_result(False, f"Demo failed: {str(e)}")
            
        finally:
            self.cleanup()
    
    def _create_result(self, success: bool, message: str) -> DemoResult:
        """Create a DemoResult object with current state."""
        execution_time = 0.0
        if self.start_time:
            execution_time = (datetime.now() - self.start_time).total_seconds()
        
        return DemoResult(
            demo_name=self.demo_name,
            success=success,
            execution_time=execution_time,
            steps_completed=self.steps_completed,
            steps_total=self.steps_total,
            errors=self.errors,
            warnings=self.warnings,
            data_extracted=self.data_extracted,
            log_path=self.logger.log_file,
            screenshots=[]  # Will be populated by specific demos
        )
    
    def add_warning(self, message: str):
        """Add a warning message to the demo results."""
        self.warnings.append(message)
        self.logger.warning(message)
    
    def increment_step(self, description: str = ""):
        """Increment completed steps counter."""
        self.steps_completed += 1
        if description:
            self.logger.info(f"Step {self.steps_completed}: {description}")