"""
Centralized error handling and recovery system for Nova Act demos.
"""

from dataclasses import dataclass
from typing import Optional, Callable, List, Any
import time
import random


@dataclass
class RecoveryAction:
    """Represents a recovery action for handling errors."""
    should_retry: bool
    max_retries: int = 3
    delay_seconds: float = 1.0
    alternative_action: Optional[Callable] = None
    fallback_sites: List[str] = None
    troubleshooting_tips: List[str] = None


class ErrorHandler:
    """Handles various types of errors that can occur during demo execution."""
    
    def __init__(self):
        self.retry_counts = {}
    
    def handle_error(self, error: Exception, demo_instance) -> Optional[RecoveryAction]:
        """
        Handle an error and return appropriate recovery action.
        
        Args:
            error: The exception that occurred
            demo_instance: The demo instance that encountered the error
            
        Returns:
            RecoveryAction or None if no recovery possible
        """
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Authentication errors
        if self._is_auth_error(error_message):
            return self.handle_auth_error(error, demo_instance)
        
        # Geographic restriction errors
        elif self._is_geo_restriction(error_message):
            return self.handle_geo_restriction(error, demo_instance)
        
        # Element not found errors
        elif self._is_element_error(error_message):
            return self.handle_element_not_found(error, demo_instance)
        
        # Timeout errors
        elif self._is_timeout_error(error_message):
            return self.handle_timeout(error, demo_instance)
        
        # Network errors
        elif self._is_network_error(error_message):
            return self.handle_network_error(error, demo_instance)
        
        # Default handling
        return self.handle_generic_error(error, demo_instance)
    
    def handle_auth_error(self, error: Exception, demo_instance) -> RecoveryAction:
        """Handle authentication-related errors."""
        tips = [
            "Check if your API key is set correctly",
            "Verify your account has sufficient credits",
            "Try running from a different geographic location",
            "Check if the service is temporarily unavailable"
        ]
        
        return RecoveryAction(
            should_retry=False,  # Auth errors usually need manual intervention
            troubleshooting_tips=tips
        )
    
    def handle_geo_restriction(self, error: Exception, demo_instance) -> RecoveryAction:
        """Handle geographic restriction errors."""
        fallback_sites = demo_instance.get_fallback_sites() if demo_instance else []
        
        tips = [
            "This site may be restricted in your region",
            "Trying alternative sites with similar functionality",
            "Consider using a VPN if legally permitted in your jurisdiction",
            "Some demos may have limited functionality outside the US"
        ]
        
        return RecoveryAction(
            should_retry=True,
            max_retries=1,
            fallback_sites=fallback_sites,
            troubleshooting_tips=tips
        )
    
    def handle_element_not_found(self, error: Exception, demo_instance) -> RecoveryAction:
        """Handle element not found errors."""
        tips = [
            "The website may have changed its layout",
            "Trying alternative element selectors",
            "Page may still be loading - increasing wait time",
            "Check if the website is accessible in your browser"
        ]
        
        return RecoveryAction(
            should_retry=True,
            max_retries=3,
            delay_seconds=2.0,
            troubleshooting_tips=tips
        )
    
    def handle_timeout(self, error: Exception, demo_instance) -> RecoveryAction:
        """Handle timeout errors."""
        tips = [
            "The page is taking longer than expected to load",
            "Your internet connection may be slow",
            "The website may be experiencing high traffic",
            "Retrying with increased timeout"
        ]
        
        return RecoveryAction(
            should_retry=True,
            max_retries=2,
            delay_seconds=5.0,
            troubleshooting_tips=tips
        )
    
    def handle_network_error(self, error: Exception, demo_instance) -> RecoveryAction:
        """Handle network-related errors."""
        tips = [
            "Check your internet connection",
            "The website may be temporarily unavailable",
            "Try again in a few moments",
            "Consider using alternative sites"
        ]
        
        return RecoveryAction(
            should_retry=True,
            max_retries=3,
            delay_seconds=3.0,
            troubleshooting_tips=tips
        )
    
    def handle_generic_error(self, error: Exception, demo_instance) -> RecoveryAction:
        """Handle generic errors."""
        tips = [
            f"Unexpected error: {type(error).__name__}",
            "Check the logs for more details",
            "Try running the demo again",
            "Report this issue if it persists"
        ]
        
        return RecoveryAction(
            should_retry=False,
            troubleshooting_tips=tips
        )
    
    def should_retry(self, error: Exception, demo_name: str, attempt: int) -> bool:
        """Determine if an error should trigger a retry."""
        key = f"{demo_name}_{type(error).__name__}"
        current_count = self.retry_counts.get(key, 0)
        
        if current_count >= 3:  # Max 3 retries per error type per demo
            return False
        
        self.retry_counts[key] = current_count + 1
        return True
    
    def wait_with_backoff(self, attempt: int, base_delay: float = 1.0):
        """Wait with exponential backoff."""
        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
        time.sleep(min(delay, 30))  # Cap at 30 seconds
    
    def _is_auth_error(self, error_message: str) -> bool:
        """Check if error is authentication-related."""
        auth_keywords = [
            "authentication", "unauthorized", "api key", "invalid key",
            "access denied", "forbidden", "401", "403"
        ]
        return any(keyword in error_message for keyword in auth_keywords)
    
    def _is_geo_restriction(self, error_message: str) -> bool:
        """Check if error is due to geographic restrictions."""
        geo_keywords = [
            "not available in your country", "geographic", "region",
            "location", "blocked", "restricted", "unavailable in your area"
        ]
        return any(keyword in error_message for keyword in geo_keywords)
    
    def _is_element_error(self, error_message: str) -> bool:
        """Check if error is element-related."""
        element_keywords = [
            "element not found", "no such element", "element not visible",
            "element not interactable", "stale element", "selector"
        ]
        return any(keyword in error_message for keyword in element_keywords)
    
    def _is_timeout_error(self, error_message: str) -> bool:
        """Check if error is timeout-related."""
        timeout_keywords = [
            "timeout", "timed out", "time limit", "took too long"
        ]
        return any(keyword in error_message for keyword in timeout_keywords)
    
    def _is_network_error(self, error_message: str) -> bool:
        """Check if error is network-related."""
        network_keywords = [
            "connection", "network", "dns", "unreachable", "connection refused",
            "connection reset", "connection timeout"
        ]
        return any(keyword in error_message for keyword in network_keywords)