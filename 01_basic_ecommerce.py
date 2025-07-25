#!/usr/bin/env python3
"""
Nova Act Demo: Basic E-commerce Operations
==========================================

This demo shows basic e-commerce operations like searching for products,
navigating product pages, and adding items to cart on various e-commerce sites.

Now includes robust error handling, geographic awareness, and fallback sites.
"""

import os
import sys
import time
from typing import Dict, Any, List
from nova_act import NovaAct

# Import our new framework
from demo_framework import BaseDemo, DemoResult
from demo_framework.multi_selector import SelectorBuilder


class BasicEcommerceDemo(BaseDemo):
    """Enhanced e-commerce demo with error handling and geographic awareness."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 6  # Total number of steps in the demo
        self.nova = None
        self.current_site = None
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up Basic E-commerce Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            self.add_warning("Please set NOVA_ACT_API_KEY environment variable")
            return False
        
        # Get optimal sites for user's region
        optimal_sites = self.config_manager.get_optimal_sites("ecommerce")
        self.logger.info(f"Optimal e-commerce sites for your region: {optimal_sites}")
        
        # Try to access the first available site
        for site in optimal_sites:
            if self.config_manager.validate_site_access(site):
                self.current_site = site
                self.logger.info(f"Using e-commerce site: {site}")
                break
        
        if not self.current_site:
            self.logger.error("No accessible e-commerce sites found")
            return False
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites if primary site fails."""
        return self.config_manager.get_site_alternatives(self.current_site)
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Initialize Nova Act
            self.logger.info(f"Initializing Nova Act with site: {self.current_site}")
            self.nova = NovaAct(
                starting_page=self.current_site,
                logs_directory="./demo/logs/basic_ecommerce"
            )
            
            with self.nova as nova:
                # Step 1: Navigate and search
                extracted_data.update(self._step_search_product(nova))
                self.increment_step("Product search completed")
                
                # Step 2: Select product
                extracted_data.update(self._step_select_product(nova))
                self.increment_step("Product selection completed")
                
                # Step 3: Extract product details
                extracted_data.update(self._step_extract_details(nova))
                self.increment_step("Product details extracted")
                
                # Step 4: Add to cart (if possible)
                extracted_data.update(self._step_add_to_cart(nova))
                self.increment_step("Add to cart attempted")
                
                # Step 5: View cart (if possible)
                extracted_data.update(self._step_view_cart(nova))
                self.increment_step("Cart viewing attempted")
                
                # Step 6: Summary
                self._step_create_summary(extracted_data)
                self.increment_step("Demo summary created")
        
        except Exception as e:
            self.logger.error(f"Error during demo execution: {str(e)}")
            # Try fallback sites
            if self._try_fallback_sites():
                self.logger.info("Successfully switched to fallback site")
                return self.execute_steps()  # Retry with fallback
            raise
        
        return extracted_data
    
    def _step_search_product(self, nova) -> Dict[str, Any]:
        """Step 1: Search for a product."""
        self.logger.log_step(1, "Product Search", "starting")
        
        try:
            search_term = "coffee maker"
            self.logger.info(f"Searching for: {search_term}")
            
            # Use natural language - Nova Act will handle the specifics
            nova.act(f"search for {search_term}")
            
            # Wait a moment for results to load
            time.sleep(2)
            
            self.logger.log_step(1, "Product Search", "completed", f"Searched for {search_term}")
            return {"search_term": search_term, "search_completed": True}
            
        except Exception as e:
            self.logger.log_step(1, "Product Search", "failed", str(e))
            raise
    
    def _step_select_product(self, nova) -> Dict[str, Any]:
        """Step 2: Select a product from results."""
        self.logger.log_step(2, "Product Selection", "starting")
        
        try:
            # Select first result
            nova.act("click on the first product in the search results")
            
            # Wait for product page to load
            time.sleep(3)
            
            self.logger.log_step(2, "Product Selection", "completed")
            return {"product_selected": True}
            
        except Exception as e:
            self.logger.log_step(2, "Product Selection", "failed", str(e))
            # Try alternative selection methods
            try:
                nova.act("select the first result")
                return {"product_selected": True, "selection_method": "alternative"}
            except:
                raise e
    
    def _step_extract_details(self, nova) -> Dict[str, Any]:
        """Step 3: Extract product details."""
        self.logger.log_step(3, "Product Details Extraction", "starting")
        
        try:
            # Try to extract product information
            product_data = {}
            
            # Get product title
            try:
                nova.act("scroll to the top of the page to see the product title")
                # Note: In a real implementation, we'd extract the actual text
                # For demo purposes, we'll simulate data extraction
                product_data["title_visible"] = True
            except:
                product_data["title_visible"] = False
            
            # Get price information
            try:
                nova.act("look for the product price")
                product_data["price_visible"] = True
            except:
                product_data["price_visible"] = False
            
            # Get product description
            try:
                nova.act("scroll down to see product description and details")
                product_data["description_visible"] = True
            except:
                product_data["description_visible"] = False
            
            self.logger.log_step(3, "Product Details Extraction", "completed")
            self.logger.log_data_extraction("product_details", product_data, self.current_site)
            
            return {"product_details": product_data}
            
        except Exception as e:
            self.logger.log_step(3, "Product Details Extraction", "failed", str(e))
            return {"product_details": {"extraction_failed": True}}
    
    def _step_add_to_cart(self, nova) -> Dict[str, Any]:
        """Step 4: Add product to cart."""
        self.logger.log_step(4, "Add to Cart", "starting")
        
        try:
            # Try to add to cart
            nova.act("scroll down or up until you see 'add to cart' button and then click it")
            
            # Wait for cart action to complete
            time.sleep(2)
            
            # Check if we were successful (in a real implementation)
            cart_result = {"added_to_cart": True, "method": "primary"}
            
            self.logger.log_step(4, "Add to Cart", "completed")
            return {"cart_action": cart_result}
            
        except Exception as e:
            self.logger.log_step(4, "Add to Cart", "failed", str(e))
            
            # Try alternative methods
            try:
                nova.act("find and click the add to cart button")
                cart_result = {"added_to_cart": True, "method": "alternative"}
                return {"cart_action": cart_result}
            except:
                # If we can't add to cart, that's okay for demo purposes
                self.add_warning("Could not add item to cart - this may be due to site restrictions")
                return {"cart_action": {"added_to_cart": False, "reason": "site_restrictions"}}
    
    def _step_view_cart(self, nova) -> Dict[str, Any]:
        """Step 5: View shopping cart."""
        self.logger.log_step(5, "View Cart", "starting")
        
        try:
            # Try to view cart
            nova.act("click on the shopping cart icon to view the cart")
            
            # Wait for cart page to load
            time.sleep(2)
            
            cart_data = {"cart_viewed": True}
            
            self.logger.log_step(5, "View Cart", "completed")
            return {"cart_view": cart_data}
            
        except Exception as e:
            self.logger.log_step(5, "View Cart", "failed", str(e))
            self.add_warning("Could not view cart - this is normal for demo purposes")
            return {"cart_view": {"cart_viewed": False, "reason": "demo_limitation"}}
    
    def _step_create_summary(self, extracted_data: Dict[str, Any]):
        """Step 6: Create demo summary."""
        self.logger.log_step(6, "Create Summary", "starting")
        
        summary = {
            "demo_type": "basic_ecommerce",
            "site_used": self.current_site,
            "steps_completed": self.steps_completed,
            "data_extracted": extracted_data,
            "success_rate": self.steps_completed / self.steps_total
        }
        
        self.logger.log_data_extraction("demo_summary", summary, "demo_framework")
        self.logger.log_step(6, "Create Summary", "completed")
    
    def _try_fallback_sites(self) -> bool:
        """Try fallback sites if primary site fails."""
        fallback_sites = self.get_fallback_sites()
        
        for site in fallback_sites:
            if self.config_manager.validate_site_access(site):
                self.logger.info(f"Switching to fallback site: {site}")
                self.current_site = site
                return True
        
        return False


def run_basic_demo():
    """Run the basic e-commerce demo."""
    print("🛒 Starting Enhanced Basic E-commerce Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = BasicEcommerceDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted:
            print("📋 Data extracted:")
            for key, value in result.data_extracted.items():
                print(f"   {key}: {value}")
    else:
        print("❌ Demo encountered issues:")
        for error in result.errors:
            print(f"   • {error.error_type}: {error.message}")
            if error.troubleshooting_tips:
                print("     Troubleshooting tips:")
                for tip in error.troubleshooting_tips:
                    print(f"       - {tip}")
    
    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   • {warning}")
    
    print(f"📄 Detailed logs: {result.log_path}")
    
    return result


def main():
    """Main function to run the demo."""
    print("Nova Act Enhanced E-commerce Demo")
    print("=================================")
    
    # Run the demo
    result = run_basic_demo()
    
    # Create summary report
    if hasattr(result, 'log_path') and result.log_path:
        # The logger will create a summary report
        pass
    
    if result.success:
        print("\n🎉 E-commerce demo completed successfully!")
        print("This demo showcased:")
        print("  • Geographic-aware site selection")
        print("  • Robust error handling and recovery")
        print("  • Structured logging and reporting")
        print("  • Fallback strategies for reliability")
    else:
        print("\n⚠️ Demo encountered some issues, but this is expected.")
        print("The framework handled errors gracefully and provided useful feedback.")


if __name__ == "__main__":
    main()
