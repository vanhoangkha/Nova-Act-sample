#!/usr/bin/env python3
"""
Nova Act Demo: Information Extraction
=====================================

This demo shows how to extract structured information from web pages
using Pydantic schemas, as described in the Nova Act README.
"""

import os
import sys
from typing import List, Optional
from pydantic import BaseModel
from nova_act import NovaAct, BOOL_SCHEMA

# Define data models for extraction
class Book(BaseModel):
    title: str
    author: str
    price: Optional[str] = None
    rating: Optional[str] = None

class BookList(BaseModel):
    books: List[Book]

class NewsArticle(BaseModel):
    headline: str
    summary: str
    author: Optional[str] = None
    publish_date: Optional[str] = None

class NewsCollection(BaseModel):
    articles: List[NewsArticle]

class ProductInfo(BaseModel):
    name: str
    price: str
    rating: Optional[str] = None
    availability: str
    description: Optional[str] = None

def extract_books_demo():
    """
    Extract book information from a bookstore website
    """
    print("📚 Starting Book Extraction Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://books.toscrape.com/",
            logs_directory="./demo/logs/book_extraction"
        ) as nova:
            print("📖 Navigating to book catalog...")
            
            # Navigate to a specific category
            nova.act("click on 'Travel' category")
            
            # Extract book information
            print("🔍 Extracting book information...")
            result = nova.act(
                "Extract information about the first 5 books shown including title, author, and price",
                schema=BookList.model_json_schema()
            )
            
            if result.matches_schema:
                book_list = BookList.model_validate(result.parsed_response)
                print(f"✅ Successfully extracted {len(book_list.books)} books:")
                for i, book in enumerate(book_list.books, 1):
                    print(f"  {i}. {book.title} by {book.author} - {book.price}")
                return book_list
            else:
                print(f"❌ Failed to extract books: {result.response}")
                return None
                
    except Exception as e:
        print(f"❌ Error during book extraction: {e}")
        return None

def extract_news_demo():
    """
    Extract news articles from a news website
    """
    print("\n📰 Starting News Extraction Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://news.ycombinator.com/",
            logs_directory="./demo/logs/news_extraction"
        ) as nova:
            print("📰 Extracting news articles...")
            
            result = nova.act(
                "Extract the top 5 news articles with their headlines and any available summary or description",
                schema=NewsCollection.model_json_schema()
            )
            
            if result.matches_schema:
                news_collection = NewsCollection.model_validate(result.parsed_response)
                print(f"✅ Successfully extracted {len(news_collection.articles)} articles:")
                for i, article in enumerate(news_collection.articles, 1):
                    print(f"  {i}. {article.headline}")
                    if article.summary:
                        print(f"     Summary: {article.summary[:100]}...")
                return news_collection
            else:
                print(f"❌ Failed to extract news: {result.response}")
                return None
                
    except Exception as e:
        print(f"❌ Error during news extraction: {e}")
        return None

def extract_product_info_demo():
    """
    Extract detailed product information
    """
    print("\n🛍️ Starting Product Information Extraction Demo")
    print("=" * 50)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/product_extraction"
        ) as nova:
            # Search for a specific product
            print("🔍 Searching for laptop...")
            nova.act("search for laptop")
            
            # Select first result
            print("👆 Selecting first product...")
            nova.act("click on the first product result")
            
            # Extract product information
            print("📋 Extracting product details...")
            result = nova.act(
                "Extract the product name, price, rating, availability status, and a brief description",
                schema=ProductInfo.model_json_schema()
            )
            
            if result.matches_schema:
                product = ProductInfo.model_validate(result.parsed_response)
                print("✅ Successfully extracted product information:")
                print(f"  Name: {product.name}")
                print(f"  Price: {product.price}")
                print(f"  Rating: {product.rating}")
                print(f"  Availability: {product.availability}")
                if product.description:
                    print(f"  Description: {product.description[:100]}...")
                return product
            else:
                print(f"❌ Failed to extract product info: {result.response}")
                return None
                
    except Exception as e:
        print(f"❌ Error during product extraction: {e}")
        return None

def boolean_extraction_demo():
    """
    Demonstrate boolean extraction using BOOL_SCHEMA
    """
    print("\n✅ Starting Boolean Extraction Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            logs_directory="./demo/logs/boolean_extraction"
        ) as nova:
            # Check if user is logged in
            print("🔐 Checking login status...")
            result = nova.act("Am I logged in to Amazon?", schema=BOOL_SCHEMA)
            
            if result.matches_schema:
                is_logged_in = result.parsed_response
                if is_logged_in:
                    print("✅ User is logged in")
                else:
                    print("❌ User is not logged in")
                
                # Check if cart has items
                print("🛒 Checking if cart has items...")
                result2 = nova.act("Does the shopping cart have any items in it?", schema=BOOL_SCHEMA)
                
                if result2.matches_schema:
                    has_items = result2.parsed_response
                    if has_items:
                        print("✅ Cart has items")
                    else:
                        print("❌ Cart is empty")
                    
                    return {"logged_in": is_logged_in, "cart_has_items": has_items}
                else:
                    print(f"❌ Failed to check cart status: {result2.response}")
            else:
                print(f"❌ Failed to check login status: {result.response}")
                
    except Exception as e:
        print(f"❌ Error during boolean extraction: {e}")
        return None

def main():
    """Main function to run all extraction demos"""
    print("Nova Act Information Extraction Demo Suite")
    print("=========================================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    # Run all extraction demos
    results = {}
    
    results['books'] = extract_books_demo()
    results['news'] = extract_news_demo()
    results['product'] = extract_product_info_demo()
    results['boolean'] = boolean_extraction_demo()
    
    # Summary
    print("\n📊 Extraction Demo Summary")
    print("=" * 30)
    successful = sum(1 for result in results.values() if result is not None)
    total = len(results)
    print(f"✅ {successful}/{total} extraction demos completed successfully")
    
    if successful == total:
        print("🎉 All information extraction demos completed successfully!")
    else:
        print("⚠️ Some demos encountered issues. Check the logs for details.")

if __name__ == "__main__":
    main()
