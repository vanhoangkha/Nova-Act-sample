#!/usr/bin/env python3
"""
Nova Act Demo: Search and Filter Operations
===========================================

This demo shows how to perform searches, apply filters, and navigate
search results using Nova Act.
"""

import os
import sys
from typing import List, Optional
from pydantic import BaseModel
from nova_act import NovaAct, BOOL_SCHEMA

class SearchResult(BaseModel):
    title: str
    price: Optional[str] = None
    rating: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

class SearchResults(BaseModel):
    results: List[SearchResult]
    total_count: Optional[str] = None

def basic_search_demo():
    """
    Demo for basic search functionality
    """
    print("🔍 Starting Basic Search Demo")
    print("=" * 35)
    
    search_terms = ["wireless headphones", "laptop", "coffee maker"]
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/basic_search"
        ) as nova:
            print("🌐 Navigating to Amazon...")
            
            for term in search_terms:
                print(f"🔍 Searching for: {term}")
                
                # Perform search
                nova.act(f"search for {term}")
                
                # Check if results are displayed
                result = nova.act("Are search results displayed on the page?", schema=BOOL_SCHEMA)
                
                if result.matches_schema and result.parsed_response:
                    print(f"✅ Search results found for '{term}'")
                    
                    # Get result count
                    count_result = nova.act("How many search results are shown or what's the total count?")
                    print(f"📊 Results: {count_result.response}")
                else:
                    print(f"❌ No results found for '{term}'")
                
                # Go back to home for next search
                if term != search_terms[-1]:  # Don't go back on last iteration
                    nova.act("click on the Amazon logo to go back to the home page")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during basic search demo: {e}")
        return False

def advanced_search_with_filters_demo():
    """
    Demo for advanced search with filters and sorting
    """
    print("\n🎛️ Starting Advanced Search with Filters Demo")
    print("=" * 55)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/advanced_search"
        ) as nova:
            print("🔍 Performing advanced search...")
            
            # Search for a broad category
            nova.act("search for smartphones")
            
            # Apply price filter
            print("💰 Applying price filter...")
            nova.act("click on price filter and select '$100 to $300' or similar price range")
            
            # Apply brand filter
            print("🏷️ Applying brand filter...")
            nova.act("find brand filters and select 'Samsung' or another popular brand")
            
            # Apply rating filter
            print("⭐ Applying rating filter...")
            nova.act("find customer rating filter and select '4 stars & up'")
            
            # Apply sorting
            print("📊 Applying sorting...")
            nova.act("sort results by 'Price: Low to High'")
            
            # Extract filtered results
            print("📋 Extracting filtered results...")
            result = nova.act(
                "Extract the first 5 search results with title, price, and rating",
                schema=SearchResults.model_json_schema()
            )
            
            if result.matches_schema:
                search_results = SearchResults.model_validate(result.parsed_response)
                print(f"✅ Successfully extracted {len(search_results.results)} filtered results:")
                
                for i, item in enumerate(search_results.results, 1):
                    print(f"  {i}. {item.title}")
                    if item.price:
                        print(f"     💰 Price: {item.price}")
                    if item.rating:
                        print(f"     ⭐ Rating: {item.rating}")
                
                return search_results
            else:
                print("❌ Failed to extract search results")
                return None
                
    except Exception as e:
        print(f"❌ Error during advanced search demo: {e}")
        return None

def category_navigation_demo():
    """
    Demo for navigating through categories and subcategories
    """
    print("\n📂 Starting Category Navigation Demo")
    print("=" * 45)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/category_navigation"
        ) as nova:
            print("🌐 Navigating through categories...")
            
            # Navigate to main category
            print("📂 Accessing main categories...")
            nova.act("click on 'All' or the hamburger menu to see all categories")
            
            # Select Electronics category
            print("💻 Selecting Electronics category...")
            nova.act("click on 'Electronics' category")
            
            # Navigate to subcategory
            print("📱 Navigating to subcategory...")
            nova.act("click on 'Cell Phones & Accessories' or similar subcategory")
            
            # Further narrow down
            print("🔍 Narrowing down selection...")
            nova.act("click on 'Unlocked Cell Phones' or similar specific category")
            
            # Check if we're in the right category
            result = nova.act("What category or section am I currently viewing?")
            print(f"📍 Current location: {result.response}")
            
            # Apply category-specific filters
            print("🎛️ Applying category-specific filters...")
            nova.act("look for and apply filters specific to this category like screen size or storage")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during category navigation demo: {e}")
        return False

def comparison_shopping_demo():
    """
    Demo for comparing products across different searches
    """
    print("\n⚖️ Starting Comparison Shopping Demo")
    print("=" * 45)
    
    products_to_compare = ["iPhone 15", "Samsung Galaxy S24", "Google Pixel 8"]
    comparison_results = []
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/comparison_shopping"
        ) as nova:
            
            for product in products_to_compare:
                print(f"🔍 Searching for {product}...")
                
                # Search for specific product
                nova.act(f"search for {product}")
                
                # Select first result
                nova.act("click on the first product result")
                
                # Extract product information
                result = nova.act(
                    f"Extract the product name, price, rating, and key specifications for this {product}",
                    schema=SearchResult.model_json_schema()
                )
                
                if result.matches_schema:
                    product_info = SearchResult.model_validate(result.parsed_response)
                    comparison_results.append(product_info)
                    print(f"✅ Extracted info for {product}")
                else:
                    print(f"❌ Failed to extract info for {product}")
                
                # Go back to search for next product
                if product != products_to_compare[-1]:
                    nova.act("go back to Amazon home page")
            
            # Display comparison
            print("\n📊 Product Comparison Results:")
            print("=" * 35)
            
            for i, product in enumerate(comparison_results, 1):
                print(f"{i}. {product.title}")
                if product.price:
                    print(f"   💰 Price: {product.price}")
                if product.rating:
                    print(f"   ⭐ Rating: {product.rating}")
                if product.description:
                    print(f"   📝 Description: {product.description[:100]}...")
                print()
            
            return comparison_results
            
    except Exception as e:
        print(f"❌ Error during comparison shopping demo: {e}")
        return []

def search_refinement_demo():
    """
    Demo for refining search results iteratively
    """
    print("\n🔄 Starting Search Refinement Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/search_refinement"
        ) as nova:
            print("🔍 Starting with broad search...")
            
            # Start with broad search
            nova.act("search for laptops")
            
            # Check number of results
            initial_count = nova.act("How many search results are displayed?")
            print(f"📊 Initial results: {initial_count.response}")
            
            # Refine by brand
            print("🏷️ Refining by brand...")
            nova.act("add 'Dell' to the search or filter by Dell brand")
            
            refined_count1 = nova.act("How many results are shown now?")
            print(f"📊 After brand filter: {refined_count1.response}")
            
            # Refine by screen size
            print("📏 Refining by screen size...")
            nova.act("further refine by adding '15 inch' or selecting 15-inch screen size filter")
            
            refined_count2 = nova.act("How many results are shown now?")
            print(f"📊 After screen size filter: {refined_count2.response}")
            
            # Refine by price range
            print("💰 Refining by price range...")
            nova.act("apply a price filter for laptops under $1000")
            
            final_count = nova.act("How many results are shown in the final refined search?")
            print(f"📊 Final refined results: {final_count.response}")
            
            # Extract final refined results
            result = nova.act(
                "Extract the top 3 results from this refined search with title, price, and key features",
                schema=SearchResults.model_json_schema()
            )
            
            if result.matches_schema:
                final_results = SearchResults.model_validate(result.parsed_response)
                print(f"✅ Successfully refined search to {len(final_results.results)} targeted results")
                return final_results
            else:
                print("❌ Failed to extract refined results")
                return None
                
    except Exception as e:
        print(f"❌ Error during search refinement demo: {e}")
        return None

def multi_site_search_demo():
    """
    Demo for searching across multiple websites
    """
    print("\n🌐 Starting Multi-Site Search Demo")
    print("=" * 40)
    
    search_sites = [
        {"name": "Amazon", "url": "https://www.amazon.com"},
        {"name": "Best Buy", "url": "https://www.bestbuy.com"},
        {"name": "Target", "url": "https://www.target.com"}
    ]
    
    search_term = "wireless mouse"
    all_results = []
    
    try:
        for site in search_sites:
            print(f"🔍 Searching {site['name']} for '{search_term}'...")
            
            with NovaAct(
                starting_page=site['url'],
                logs_directory=f"./demo/logs/multi_search_{site['name'].lower()}"
            ) as nova:
                # Perform search on each site
                nova.act(f"search for {search_term}")
                
                # Extract top results
                result = nova.act(
                    f"Extract the top 3 search results for {search_term} with title and price",
                    schema=SearchResults.model_json_schema()
                )
                
                if result.matches_schema:
                    site_results = SearchResults.model_validate(result.parsed_response)
                    
                    # Add site information to results
                    for item in site_results.results:
                        item.url = site['name']  # Using URL field to store site name
                    
                    all_results.extend(site_results.results)
                    print(f"✅ Found {len(site_results.results)} results on {site['name']}")
                else:
                    print(f"❌ Failed to extract results from {site['name']}")
        
        # Display consolidated results
        print(f"\n📊 Multi-Site Search Results for '{search_term}':")
        print("=" * 50)
        
        for result in all_results:
            print(f"🏪 {result.url}: {result.title}")
            if result.price:
                print(f"   💰 {result.price}")
            print()
        
        print(f"✅ Total results found: {len(all_results)} across {len(search_sites)} sites")
        return all_results
        
    except Exception as e:
        print(f"❌ Error during multi-site search demo: {e}")
        return []

def main():
    """Main function to run all search and filter demos"""
    print("Nova Act Search & Filter Demo Suite")
    print("===================================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    print("\n🔍 Search & Filter Demo Options:")
    print("1. Basic search functionality")
    print("2. Advanced search with filters")
    print("3. Category navigation")
    print("4. Comparison shopping")
    print("5. Search refinement")
    print("6. Multi-site search")
    print("7. Run all demos")
    
    choice = input("\nSelect demo (1-7): ").strip()
    
    if choice == "1":
        basic_search_demo()
    elif choice == "2":
        advanced_search_with_filters_demo()
    elif choice == "3":
        category_navigation_demo()
    elif choice == "4":
        comparison_shopping_demo()
    elif choice == "5":
        search_refinement_demo()
    elif choice == "6":
        multi_site_search_demo()
    elif choice == "7":
        # Run all demos
        results = []
        results.append(basic_search_demo())
        results.append(advanced_search_with_filters_demo())
        results.append(category_navigation_demo())
        results.append(comparison_shopping_demo())
        results.append(search_refinement_demo())
        results.append(multi_site_search_demo())
        
        successful = sum(1 for result in results if result)
        total = len(results)
        
        print(f"\n📊 Search & Filter Demo Summary: {successful}/{total} successful")
        
        if successful == total:
            print("🎉 All search and filter demos completed successfully!")
        else:
            print("⚠️ Some demos encountered issues. Check the logs for details.")
    else:
        print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()
