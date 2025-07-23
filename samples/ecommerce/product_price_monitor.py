#!/usr/bin/env python3
"""
E-commerce Price Monitoring Sample

This sample demonstrates how to monitor product prices across multiple e-commerce sites
and track price changes over time.
"""

import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional

from nova_act import NovaAct, BOOL_SCHEMA


class ProductPrice(BaseModel):
    product_name: str
    price: float
    currency: str
    availability: str
    url: str
    timestamp: str


class PriceMonitor:
    def __init__(self, products_to_monitor: List[dict]):
        self.products = products_to_monitor
        self.price_history = []
    
    def check_single_product(self, product_info: dict) -> Optional[ProductPrice]:
        """Check price for a single product"""
        try:
            with NovaAct(starting_page=product_info['url']) as nova:
                # Wait for page to load
                time.sleep(2)
                
                # Check if product is available
                availability_result = nova.act(
                    "Is this product available for purchase? Look for 'Add to Cart', 'Buy Now', or 'In Stock' indicators",
                    schema=BOOL_SCHEMA
                )
                
                availability = "Available" if (availability_result.matches_schema and availability_result.parsed_response) else "Out of Stock"
                
                # Extract product details
                product_schema = ProductPrice.model_json_schema()
                result = nova.act(
                    f"Extract the product name and current price from this page. Use URL: {product_info['url']} and availability: {availability}",
                    schema=product_schema
                )
                
                if result.matches_schema:
                    product_price = ProductPrice.model_validate(result.parsed_response)
                    product_price.timestamp = datetime.now().isoformat()
                    return product_price
                    
        except Exception as e:
            print(f"Error checking product {product_info['url']}: {e}")
            return None
    
    def monitor_prices(self, max_workers: int = 3) -> List[ProductPrice]:
        """Monitor prices for all products in parallel"""
        current_prices = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_product = {
                executor.submit(self.check_single_product, product): product 
                for product in self.products
            }
            
            for future in as_completed(future_to_product.keys()):
                product_info = future_to_product[future]
                try:
                    price_data = future.result()
                    if price_data:
                        current_prices.append(price_data)
                        print(f"✓ {price_data.product_name}: ${price_data.price} ({price_data.availability})")
                    else:
                        print(f"✗ Failed to get price for {product_info['url']}")
                except Exception as e:
                    print(f"✗ Error processing {product_info['url']}: {e}")
        
        self.price_history.extend(current_prices)
        return current_prices
    
    def save_results(self, filename: str = "price_history.json"):
        """Save price history to JSON file"""
        with open(filename, 'w') as f:
            json.dump([price.dict() for price in self.price_history], f, indent=2)
        print(f"Price history saved to {filename}")
    
    def find_price_drops(self, threshold_percent: float = 10.0) -> List[dict]:
        """Find products with significant price drops"""
        # Group by product name
        product_prices = {}
        for price in self.price_history:
            if price.product_name not in product_prices:
                product_prices[price.product_name] = []
            product_prices[price.product_name].append(price)
        
        price_drops = []
        for product_name, prices in product_prices.items():
            if len(prices) >= 2:
                # Sort by timestamp
                prices.sort(key=lambda x: x.timestamp)
                latest = prices[-1]
                previous = prices[-2]
                
                if previous.price > 0:
                    drop_percent = ((previous.price - latest.price) / previous.price) * 100
                    if drop_percent >= threshold_percent:
                        price_drops.append({
                            'product': product_name,
                            'previous_price': previous.price,
                            'current_price': latest.price,
                            'drop_percent': round(drop_percent, 2),
                            'url': latest.url
                        })
        
        return price_drops


def main():
    # Example products to monitor
    products_to_monitor = [
        {
            'url': 'https://www.amazon.com/dp/B08N5WRWNW',  # Echo Dot
            'expected_name': 'Echo Dot'
        },
        {
            'url': 'https://www.amazon.com/dp/B0BSHF7WHW',  # Fire TV Stick
            'expected_name': 'Fire TV Stick'
        }
    ]
    
    monitor = PriceMonitor(products_to_monitor)
    
    print("🔍 Starting price monitoring...")
    current_prices = monitor.monitor_prices()
    
    print(f"\n📊 Monitored {len(current_prices)} products")
    
    # Save results
    monitor.save_results()
    
    # Check for price drops (if we have historical data)
    price_drops = monitor.find_price_drops()
    if price_drops:
        print("\n🔥 Price drops found:")
        for drop in price_drops:
            print(f"  {drop['product']}: ${drop['previous_price']} → ${drop['current_price']} ({drop['drop_percent']}% off)")
    
    return current_prices


if __name__ == "__main__":
    main()
