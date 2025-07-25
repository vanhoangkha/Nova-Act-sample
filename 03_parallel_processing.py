#!/usr/bin/env python3
"""
Nova Act Demo: Parallel Processing
==================================

This demo shows how to run multiple Nova Act instances in parallel
to collect data from multiple sources simultaneously.

Based on the parallel processing example from the Nova Act README.
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from pydantic import BaseModel
from nova_act import NovaAct, ActError

# Data models for parallel extraction
class PriceComparison(BaseModel):
    product_name: str
    price: str
    website: str
    availability: str
    rating: Optional[str] = None

class SearchResult(BaseModel):
    title: str
    url: str
    description: Optional[str] = None

class SearchResults(BaseModel):
    results: List[SearchResult]

def search_product_on_site(site_info: dict, product: str) -> Optional[PriceComparison]:
    """
    Search for a product on a specific website
    """
    site_name = site_info['name']
    site_url = site_info['url']
    
    print(f"🔍 Searching for '{product}' on {site_name}...")
    
    try:
        with NovaAct(
            starting_page=site_url,
            logs_directory=f"./demo/logs/parallel_{site_name.lower().replace(' ', '_')}"
        ) as nova:
            # Search for the product
            nova.act(f"search for {product}")
            
            # Select first result
            nova.act("click on the first product result")
            
            # Extract price information
            result = nova.act(
                f"Extract the product name, price, availability status, and rating if available for this {product}",
                schema=PriceComparison.model_json_schema()
            )
            
            if result.matches_schema:
                price_info = PriceComparison.model_validate(result.parsed_response)
                price_info.website = site_name
                print(f"✅ Found {product} on {site_name}: {price_info.price}")
                return price_info
            else:
                print(f"❌ Failed to extract price from {site_name}")
                return None
                
    except ActError as e:
        print(f"❌ Error searching {site_name}: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error with {site_name}: {e}")
        return None

def parallel_price_comparison_demo():
    """
    Compare prices for a product across multiple websites in parallel
    """
    print("💰 Starting Parallel Price Comparison Demo")
    print("=" * 50)
    
    # Define websites to search
    websites = [
        {"name": "Amazon", "url": "https://www.amazon.com"},
        {"name": "Best Buy", "url": "https://www.bestbuy.com"},
        {"name": "Target", "url": "https://www.target.com"},
    ]
    
    product = "wireless headphones"
    all_prices = []
    
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all search tasks
        future_to_site = {
            executor.submit(search_product_on_site, site, product): site['name'] 
            for site in websites
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_site.keys()):
            site_name = future_to_site[future]
            try:
                price_info = future.result()
                if price_info:
                    all_prices.append(price_info)
            except Exception as e:
                print(f"❌ Error processing {site_name}: {e}")
    
    # Display results
    print(f"\n📊 Price Comparison Results for '{product}':")
    print("=" * 50)
    
    if all_prices:
        for price in all_prices:
            print(f"🏪 {price.website}: {price.price} - {price.availability}")
            if price.rating:
                print(f"   ⭐ Rating: {price.rating}")
        
        print(f"\n✅ Successfully compared prices across {len(all_prices)} websites")
    else:
        print("❌ No price information could be extracted")
    
    return all_prices

def parallel_search_demo():
    """
    Perform searches on multiple search engines in parallel
    """
    print("\n🔍 Starting Parallel Search Demo")
    print("=" * 40)
    
    search_engines = [
        {"name": "Google", "url": "https://www.google.com"},
        {"name": "Bing", "url": "https://www.bing.com"},
        {"name": "DuckDuckGo", "url": "https://duckduckgo.com"},
    ]
    
    search_query = "artificial intelligence news"
    all_results = []
    
    def search_on_engine(engine_info: dict, query: str) -> Optional[SearchResults]:
        """Search on a specific search engine"""
        engine_name = engine_info['name']
        engine_url = engine_info['url']
        
        print(f"🔍 Searching '{query}' on {engine_name}...")
        
        try:
            with NovaAct(
                starting_page=engine_url,
                logs_directory=f"./demo/logs/search_{engine_name.lower()}"
            ) as nova:
                # Perform search
                nova.act(f"search for {query}")
                
                # Extract top results
                result = nova.act(
                    "Extract the top 3 search results with their titles, URLs, and descriptions",
                    schema=SearchResults.model_json_schema()
                )
                
                if result.matches_schema:
                    search_results = SearchResults.model_validate(result.parsed_response)
                    print(f"✅ Found {len(search_results.results)} results on {engine_name}")
                    return search_results
                else:
                    print(f"❌ Failed to extract results from {engine_name}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error searching {engine_name}: {e}")
            return None
    
    # Execute searches in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_engine = {
            executor.submit(search_on_engine, engine, search_query): engine['name']
            for engine in search_engines
        }
        
        for future in as_completed(future_to_engine.keys()):
            engine_name = future_to_engine[future]
            try:
                results = future.result()
                if results:
                    all_results.extend([(engine_name, result) for result in results.results])
            except Exception as e:
                print(f"❌ Error processing {engine_name}: {e}")
    
    # Display consolidated results
    print(f"\n📊 Search Results for '{search_query}':")
    print("=" * 50)
    
    if all_results:
        for engine_name, result in all_results:
            print(f"🔍 {engine_name}: {result.title}")
            if result.description:
                print(f"   📝 {result.description[:100]}...")
            print(f"   🔗 {result.url}")
            print()
        
        print(f"✅ Successfully collected {len(all_results)} results from multiple search engines")
    else:
        print("❌ No search results could be extracted")
    
    return all_results

def parallel_data_collection_demo():
    """
    Collect different types of data from multiple sources in parallel
    """
    print("\n📊 Starting Parallel Data Collection Demo")
    print("=" * 50)
    
    def collect_weather_data():
        """Collect weather information"""
        try:
            with NovaAct(
                starting_page="https://weather.com",
                logs_directory="./demo/logs/weather_data"
            ) as nova:
                nova.act("search for weather in New York")
                result = nova.act("What is the current temperature and weather condition?")
                return {"type": "weather", "data": result.response}
        except Exception as e:
            return {"type": "weather", "error": str(e)}
    
    def collect_stock_data():
        """Collect stock market information"""
        try:
            with NovaAct(
                starting_page="https://finance.yahoo.com",
                logs_directory="./demo/logs/stock_data"
            ) as nova:
                nova.act("search for AAPL stock")
                result = nova.act("What is the current stock price and today's change?")
                return {"type": "stock", "data": result.response}
        except Exception as e:
            return {"type": "stock", "error": str(e)}
    
    def collect_news_data():
        """Collect latest news"""
        try:
            with NovaAct(
                starting_page="https://news.ycombinator.com",
                logs_directory="./demo/logs/news_data"
            ) as nova:
                result = nova.act("What are the top 3 trending news headlines?")
                return {"type": "news", "data": result.response}
        except Exception as e:
            return {"type": "news", "error": str(e)}
    
    # Collect all data in parallel
    all_data = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(collect_weather_data),
            executor.submit(collect_stock_data),
            executor.submit(collect_news_data)
        ]
        
        for future in as_completed(futures):
            try:
                data = future.result()
                all_data.append(data)
                if 'error' in data:
                    print(f"❌ Error collecting {data['type']} data: {data['error']}")
                else:
                    print(f"✅ Successfully collected {data['type']} data")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    # Display results
    print("\n📊 Collected Data Summary:")
    print("=" * 30)
    
    for data in all_data:
        if 'error' not in data:
            print(f"📈 {data['type'].title()}: {data['data'][:100]}...")
    
    return all_data

def main():
    """Main function to run all parallel processing demos"""
    print("Nova Act Parallel Processing Demo Suite")
    print("======================================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    # Run all parallel demos
    results = {}
    
    results['price_comparison'] = parallel_price_comparison_demo()
    results['search'] = parallel_search_demo()
    results['data_collection'] = parallel_data_collection_demo()
    
    # Summary
    print("\n📊 Parallel Processing Demo Summary")
    print("=" * 40)
    
    successful = sum(1 for result in results.values() if result)
    total = len(results)
    print(f"✅ {successful}/{total} parallel demos completed successfully")
    
    if successful == total:
        print("🎉 All parallel processing demos completed successfully!")
        print("💡 This demonstrates Nova Act's ability to scale with multiple concurrent browser sessions")
    else:
        print("⚠️ Some demos encountered issues. Check the logs for details.")

if __name__ == "__main__":
    main()
