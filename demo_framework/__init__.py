"""
Nova Act Demo Framework

A robust framework for creating reliable, error-resilient demos that handle
geographic restrictions, website changes, and various failure scenarios.
"""

from .base_demo import BaseDemo, DemoResult, DemoError
from .error_handler import ErrorHandler, RecoveryAction
from .config_manager import ConfigManager, EnvironmentInfo
from .logger import Logger

__version__ = "1.0.0"
__all__ = [
    "BaseDemo",
    "DemoResult", 
    "DemoError",
    "ErrorHandler",
    "RecoveryAction",
    "ConfigManager",
    "EnvironmentInfo",
    "Logger"
]