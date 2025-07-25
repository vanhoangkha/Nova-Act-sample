"""
Multi-selector system with fallback strategies for robust element detection.
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Callable
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class SelectorStrategy:
    """Represents a selector strategy with metadata."""
    name: str
    selector_type: str  # 'css', 'xpath', 'id', 'class', 'text', 'partial_text'
    selector_value: str
    priority: int = 1  # Lower number = higher priority
    timeout: int = 10
    description: str = ""


class MultiSelector:
    """Handles multiple selector strategies with automatic fallbacks."""
    
    def __init__(self, strategies: List[SelectorStrategy]):
        self.strategies = sorted(strategies, key=lambda x: x.priority)
        self.last_successful_strategy = None
    
    def find_element(self, driver, description: str = "") -> Optional[Any]:
        """
        Try multiple selector strategies until one succeeds.
        
        Args:
            driver: Selenium WebDriver instance
            description: Human-readable description of what we're looking for
            
        Returns:
            WebElement if found, None otherwise
        """
        for strategy in self.strategies:
            try:
                element = self._try_strategy(driver, strategy)
                if element:
                    self.last_successful_strategy = strategy
                    return element
            except Exception as e:
                # Log the failure but continue to next strategy
                print(f"Strategy '{strategy.name}' failed: {str(e)}")
                continue
        
        return None
    
    def wait_for_element(self, driver, description: str = "", max_timeout: int = 30) -> Optional[Any]:
        """
        Wait for element with exponential backoff across strategies.
        
        Args:
            driver: Selenium WebDriver instance
            description: Human-readable description
            max_timeout: Maximum total time to wait
            
        Returns:
            WebElement if found, None otherwise
        """
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < max_timeout:
            # Try all strategies once
            element = self.find_element(driver, description)
            if element:
                return element
            
            # Wait with exponential backoff
            wait_time = min(2 ** attempt, 8) + random.uniform(0, 1)
            time.sleep(wait_time)
            attempt += 1
        
        return None
    
    def _try_strategy(self, driver, strategy: SelectorStrategy) -> Optional[Any]:
        """Try a specific selector strategy."""
        try:
            if strategy.selector_type == 'id':
                return driver.find_element(By.ID, strategy.selector_value)
            
            elif strategy.selector_type == 'css':
                return driver.find_element(By.CSS_SELECTOR, strategy.selector_value)
            
            elif strategy.selector_type == 'xpath':
                return driver.find_element(By.XPATH, strategy.selector_value)
            
            elif strategy.selector_type == 'class':
                return driver.find_element(By.CLASS_NAME, strategy.selector_value)
            
            elif strategy.selector_type == 'text':
                return driver.find_element(By.XPATH, f"//*[text()='{strategy.selector_value}']")
            
            elif strategy.selector_type == 'partial_text':
                return driver.find_element(By.XPATH, f"//*[contains(text(), '{strategy.selector_value}')]")
            
            elif strategy.selector_type == 'tag':
                return driver.find_element(By.TAG_NAME, strategy.selector_value)
            
            else:
                raise ValueError(f"Unknown selector type: {strategy.selector_type}")
                
        except (NoSuchElementException, TimeoutException):
            return None
    
    def find_elements(self, driver, description: str = "") -> List[Any]:
        """Find multiple elements using the first successful strategy."""
        for strategy in self.strategies:
            try:
                elements = self._try_strategy_multiple(driver, strategy)
                if elements:
                    return elements
            except Exception:
                continue
        
        return []
    
    def _try_strategy_multiple(self, driver, strategy: SelectorStrategy) -> List[Any]:
        """Try a strategy to find multiple elements."""
        try:
            if strategy.selector_type == 'id':
                return driver.find_elements(By.ID, strategy.selector_value)
            
            elif strategy.selector_type == 'css':
                return driver.find_elements(By.CSS_SELECTOR, strategy.selector_value)
            
            elif strategy.selector_type == 'xpath':
                return driver.find_elements(By.XPATH, strategy.selector_value)
            
            elif strategy.selector_type == 'class':
                return driver.find_elements(By.CLASS_NAME, strategy.selector_value)
            
            elif strategy.selector_type == 'text':
                return driver.find_elements(By.XPATH, f"//*[text()='{strategy.selector_value}']")
            
            elif strategy.selector_type == 'partial_text':
                return driver.find_elements(By.XPATH, f"//*[contains(text(), '{strategy.selector_value}')]")
            
            elif strategy.selector_type == 'tag':
                return driver.find_elements(By.TAG_NAME, strategy.selector_value)
            
            else:
                return []
                
        except Exception:
            return []


class SelectorBuilder:
    """Helper class to build common selector strategies."""
    
    @staticmethod
    def for_button(text: str, additional_selectors: List[str] = None) -> List[SelectorStrategy]:
        """Build selector strategies for buttons."""
        strategies = [
            SelectorStrategy("button_text", "text", text, 1, description=f"Button with text '{text}'"),
            SelectorStrategy("button_partial_text", "partial_text", text, 2, description=f"Button containing '{text}'"),
            SelectorStrategy("button_tag", "xpath", f"//button[contains(text(), '{text}')]", 3),
            SelectorStrategy("input_submit", "xpath", f"//input[@type='submit' and @value='{text}']", 4),
            SelectorStrategy("input_button", "xpath", f"//input[@type='button' and @value='{text}']", 5),
        ]
        
        if additional_selectors:
            for i, selector in enumerate(additional_selectors):
                strategies.append(
                    SelectorStrategy(f"custom_{i}", "css", selector, 10 + i)
                )
        
        return strategies
    
    @staticmethod
    def for_input(name: str = None, placeholder: str = None, input_type: str = None) -> List[SelectorStrategy]:
        """Build selector strategies for input fields."""
        strategies = []
        
        if name:
            strategies.extend([
                SelectorStrategy("input_name", "xpath", f"//input[@name='{name}']", 1),
                SelectorStrategy("input_id", "id", name, 2),
            ])
        
        if placeholder:
            strategies.append(
                SelectorStrategy("input_placeholder", "xpath", f"//input[@placeholder='{placeholder}']", 3)
            )
        
        if input_type:
            strategies.append(
                SelectorStrategy("input_type", "xpath", f"//input[@type='{input_type}']", 4)
            )
        
        # Generic fallbacks
        strategies.extend([
            SelectorStrategy("generic_input", "tag", "input", 10),
            SelectorStrategy("generic_textarea", "tag", "textarea", 11),
        ])
        
        return strategies
    
    @staticmethod
    def for_link(text: str, href: str = None) -> List[SelectorStrategy]:
        """Build selector strategies for links."""
        strategies = [
            SelectorStrategy("link_text", "text", text, 1),
            SelectorStrategy("link_partial_text", "partial_text", text, 2),
            SelectorStrategy("link_xpath", "xpath", f"//a[contains(text(), '{text}')]", 3),
        ]
        
        if href:
            strategies.append(
                SelectorStrategy("link_href", "xpath", f"//a[@href='{href}']", 4)
            )
        
        return strategies
    
    @staticmethod
    def for_product_elements() -> dict:
        """Build common e-commerce product element selectors."""
        return {
            "product_title": [
                SelectorStrategy("title_h1", "tag", "h1", 1),
                SelectorStrategy("title_class", "css", ".product-title, .product-name, .title", 2),
                SelectorStrategy("title_id", "css", "#product-title, #title", 3),
                SelectorStrategy("title_xpath", "xpath", "//h1 | //h2[contains(@class, 'title')]", 4),
            ],
            "product_price": [
                SelectorStrategy("price_class", "css", ".price, .product-price, .cost", 1),
                SelectorStrategy("price_span", "xpath", "//span[contains(@class, 'price')]", 2),
                SelectorStrategy("price_dollar", "xpath", "//*[contains(text(), '$')]", 3),
            ],
            "add_to_cart": [
                SelectorStrategy("cart_button", "partial_text", "Add to Cart", 1),
                SelectorStrategy("cart_button_alt", "partial_text", "Add to Basket", 2),
                SelectorStrategy("cart_id", "id", "add-to-cart", 3),
                SelectorStrategy("cart_class", "css", ".add-to-cart, .btn-cart", 4),
            ],
            "search_box": [
                SelectorStrategy("search_name", "xpath", "//input[@name='q' or @name='search']", 1),
                SelectorStrategy("search_placeholder", "xpath", "//input[@placeholder='Search']", 2),
                SelectorStrategy("search_id", "css", "#search, #search-box", 3),
                SelectorStrategy("search_class", "css", ".search-input, .search-box", 4),
            ]
        }


class ElementWaiter:
    """Advanced element waiting with multiple strategies."""
    
    def __init__(self, driver, timeout: int = 30):
        self.driver = driver
        self.timeout = timeout
    
    def wait_for_clickable(self, multi_selector: MultiSelector, description: str = "") -> Optional[Any]:
        """Wait for element to be clickable."""
        end_time = time.time() + self.timeout
        
        while time.time() < end_time:
            element = multi_selector.find_element(self.driver, description)
            if element and element.is_enabled() and element.is_displayed():
                return element
            time.sleep(0.5)
        
        return None
    
    def wait_for_visible(self, multi_selector: MultiSelector, description: str = "") -> Optional[Any]:
        """Wait for element to be visible."""
        end_time = time.time() + self.timeout
        
        while time.time() < end_time:
            element = multi_selector.find_element(self.driver, description)
            if element and element.is_displayed():
                return element
            time.sleep(0.5)
        
        return None
    
    def wait_for_text_present(self, multi_selector: MultiSelector, expected_text: str) -> bool:
        """Wait for specific text to be present in element."""
        end_time = time.time() + self.timeout
        
        while time.time() < end_time:
            element = multi_selector.find_element(self.driver)
            if element and expected_text.lower() in element.text.lower():
                return True
            time.sleep(0.5)
        
        return False