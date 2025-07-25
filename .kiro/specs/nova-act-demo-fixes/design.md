# Design Document

## Overview

This design document outlines the architecture and implementation approach for fixing critical issues in the Nova Act Demo Suite. The solution focuses on creating a robust, error-resilient demo framework that can handle geographic restrictions, website changes, and various failure scenarios while providing meaningful feedback to users.

The design emphasizes modularity, configurability, and graceful degradation to ensure demos remain functional even when individual components fail.

## Architecture

### Core Components

1. **Demo Framework Core** (`demo_framework/`)
   - `base_demo.py` - Abstract base class for all demos
   - `error_handler.py` - Centralized error handling and recovery
   - `config_manager.py` - Environment detection and configuration management
   - `logger.py` - Enhanced logging with structured output

2. **Website Adapters** (`adapters/`)
   - `ecommerce_adapter.py` - Handles multiple e-commerce sites (Amazon, eBay, etc.)
   - `news_adapter.py` - Manages news sites with fallbacks
   - `form_adapter.py` - Generic form handling across different sites

3. **Selector Engine** (`selectors/`)
   - `multi_selector.py` - Multiple selector strategy implementation
   - `fallback_manager.py` - Automatic fallback when selectors fail
   - `element_waiter.py` - Smart waiting with exponential backoff

4. **Geographic Handler** (`geo/`)
   - `region_detector.py` - Detects user's geographic location
   - `site_mapper.py` - Maps functionality to region-appropriate sites
   - `restriction_handler.py` - Handles geographic access restrictions

## Components and Interfaces

### BaseDemo Class

```python
class BaseDemo:
    def __init__(self, config: DemoConfig):
        self.config = config
        self.logger = Logger(self.__class__.__name__)
        self.error_handler = ErrorHandler()
        
    def setup(self) -> bool:
        """Setup demo environment, return success status"""
        
    def execute(self) -> DemoResult:
        """Execute demo with error handling"""
        
    def cleanup(self) -> None:
        """Cleanup resources"""
        
    def get_fallback_sites(self) -> List[str]:
        """Get alternative sites if primary fails"""
```

### ErrorHandler Class

```python
class ErrorHandler:
    def handle_auth_error(self, error: AuthError) -> RecoveryAction
    def handle_geo_restriction(self, error: GeoError) -> RecoveryAction  
    def handle_element_not_found(self, error: ElementError) -> RecoveryAction
    def handle_timeout(self, error: TimeoutError) -> RecoveryAction
    def should_retry(self, error: Exception, attempt: int) -> bool
```

### MultiSelector Class

```python
class MultiSelector:
    def __init__(self, selectors: List[SelectorStrategy]):
        self.strategies = selectors
        
    def find_element(self, nova: NovaAct, description: str) -> Optional[Element]:
        """Try multiple selector strategies until one succeeds"""
        
    def wait_for_element(self, nova: NovaAct, description: str, timeout: int) -> Element:
        """Wait for element with exponential backoff"""
```

### ConfigManager Class

```python
class ConfigManager:
    def detect_environment(self) -> EnvironmentInfo
    def get_optimal_sites(self, demo_type: str) -> List[str]
    def save_successful_config(self, demo_name: str, config: dict)
    def load_config(self, demo_name: str) -> Optional[dict]
```

## Data Models

### DemoResult

```python
@dataclass
class DemoResult:
    demo_name: str
    success: bool
    execution_time: float
    steps_completed: int
    steps_total: int
    errors: List[DemoError]
    warnings: List[str]
    data_extracted: Optional[dict]
    log_path: str
    screenshots: List[str]
```

### DemoError

```python
@dataclass  
class DemoError:
    error_type: str
    message: str
    timestamp: datetime
    recovery_attempted: bool
    recovery_successful: bool
    troubleshooting_tips: List[str]
```

### SelectorStrategy

```python
@dataclass
class SelectorStrategy:
    name: str
    selector_type: str  # 'css', 'xpath', 'text', 'id'
    selector_value: str
    priority: int
    timeout: int
```

## Error Handling

### Error Recovery Strategies

1. **Authentication Errors**
   - Detect API key issues vs geographic restrictions
   - Provide specific guidance for each error type
   - Suggest alternative demo configurations

2. **Element Not Found Errors**
   - Try alternative selectors automatically
   - Wait with exponential backoff (1s, 2s, 4s, 8s)
   - Capture page source and screenshot for debugging
   - Attempt to continue with remaining demo steps

3. **Geographic Restriction Errors**
   - Detect user's region automatically
   - Switch to region-appropriate alternative sites
   - Maintain demo functionality with different backends

4. **Timeout Errors**
   - Implement smart retry logic based on error type
   - Increase timeouts for slow networks
   - Skip non-critical steps to continue demo flow

### Graceful Degradation

```python
class GracefulDegradation:
    def skip_step_if_failed(self, step_name: str, error: Exception) -> bool:
        """Determine if step can be skipped"""
        
    def find_alternative_action(self, failed_action: str) -> Optional[str]:
        """Find alternative way to achieve same goal"""
        
    def continue_with_partial_data(self, partial_data: dict) -> bool:
        """Determine if demo can continue with incomplete data"""
```

## Testing Strategy

### Unit Tests
- Test error handling logic with mock failures
- Verify selector fallback mechanisms
- Test configuration detection and management
- Validate data extraction with various page structures

### Integration Tests  
- Test complete demo flows with simulated failures
- Verify geographic restriction handling
- Test alternative site switching
- Validate log generation and organization

### End-to-End Tests
- Run demos against live sites with failure injection
- Test recovery from various error scenarios
- Verify user experience with different configurations
- Test demo suite orchestration and reporting

### Mock Testing
- Create mock websites with known element structures
- Test selector strategies against controlled environments
- Simulate various failure conditions
- Validate error messages and recovery suggestions

## Implementation Phases

### Phase 1: Core Framework
- Implement BaseDemo class and error handling
- Create MultiSelector with fallback strategies
- Build ConfigManager for environment detection
- Set up enhanced logging system

### Phase 2: Website Adapters
- Create adapters for major e-commerce sites
- Implement geographic site mapping
- Build form handling abstractions
- Add news site adapters with fallbacks

### Phase 3: Demo Refactoring
- Refactor existing demos to use new framework
- Add comprehensive error handling to each demo
- Implement alternative site support
- Add configuration-based site selection

### Phase 4: Testing and Validation
- Create comprehensive test suite
- Validate demos across different regions
- Test failure scenarios and recovery
- Performance testing and optimization