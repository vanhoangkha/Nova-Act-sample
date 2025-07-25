#!/usr/bin/env python3
"""
Nova Act Demo: Enhanced Information Extraction
==============================================

This demo shows how to extract structured information from web pages
using Pydantic schemas with robust error handling and geographic awareness.
"""

import os
import sys
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from nova_act import NovaAct, BOOL_SCHEMA

# Import our new framework
from demo_framework import BaseDemo, DemoResult


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


class InformationExtractionDemo(BaseDemo):
    """Enhanced information extraction demo with error handling and fallbacks."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 4  # Book, News, Product, Boolean extraction
        self.nova = None
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up Information Extraction Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            return False
        
        # Get optimal sites for user's region
        news_sites = self.config_manager.get_optimal_sites("news")
        self.logger.info(f"Available news sites for your region: {news_sites}")
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites for information extraction."""
        return [
            "https://example.com",
            "https://httpbin.org/html",
            "https://quotes.toscrape.com"
        ]
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Step 1: Extract books
            extracted_data.update(self._step_extract_books())
            self.increment_step("Book extraction completed")
            
            # Step 2: Extract news
            extracted_data.update(self._step_extract_news())
            self.increment_step("News extraction completed")
            
            # Step 3: Extract product info
            extracted_data.update(self._step_extract_product())
            self.increment_step("Product extraction completed")
            
            # Step 4: Boolean extraction
            extracted_data.update(self._step_boolean_extraction())
            self.increment_step("Boolean extraction completed")
            
        except Exception as e:
            self.logger.error(f"Error during extraction: {str(e)}")
            raise
        
        return extracted_data
    
    def _step_extract_books(self) -> Dict[str, Any]:
        """Step 1: Extract book information."""
        self.logger.log_step(1, "Book Extraction", "starting")
        
        try:
            with NovaAct(
                starting_page="https://books.toscrape.com/",
                logs_directory="./demo/logs/book_extraction"
            ) as nova:
                self.logger.info("Navigating to book catalog...")
                
                # Try to navigate to a category
                try:
                    nova.act("click on 'Travel' category")
                except:
                    # If Travel category doesn't exist, try another approach
                    self.add_warning("Travel category not found, using main catalog")
                
                # Extract book information
                self.logger.info("Extracting book information...")
                result = nova.act(
                    "Extract information about the first 5 books shown including title, author, and price",
                    schema=BookList.model_json_schema()
                )
                
                if result.matches_schema:
                    book_list = BookList.model_validate(result.parsed_response)
                    self.logger.log_step(1, "Book Extraction", "completed", f"Extracted {len(book_list.books)} books")
                    self.logger.log_data_extraction("books", book_list.dict(), "books.toscrape.com")
                    return {"books": book_list.dict(), "book_count": len(book_list.books)}
                else:
                    self.logger.log_step(1, "Book Extraction", "failed", "Schema validation failed")
                    return {"books": None, "book_extraction_error": result.response}
                    
        except Exception as e:
            self.logger.log_step(1, "Book Extraction", "failed", str(e))
            self.add_warning("Book extraction failed - site may be unavailable")
            return {"books": None, "book_extraction_error": str(e)}
    
    def _step_extract_news(self) -> Dict[str, Any]:
        """Step 2: Extract news articles."""
        self.logger.log_step(2, "News Extraction", "starting")
        
        # Get region-appropriate news sites
        news_sites = self.config_manager.get_optimal_sites("news")
        
        for site in news_sites:
            try:
                self.logger.info(f"Trying news site: {site}")
                
                with NovaAct(
                    starting_page=site,
                    logs_directory="./demo/logs/news_extraction"
                ) as nova:
                    
                    # Different extraction strategies for different sites
                    if "ycombinator" in site:
                        extraction_prompt = "Extract the top 5 news articles with their headlines and any available summary"
                    elif "bbc" in site:
                        extraction_prompt = "Extract the main news headlines and their brief descriptions"
                    else:
                        extraction_prompt = "Extract news headlines and summaries from the main page"
                    
                    result = nova.act(extraction_prompt, schema=NewsCollection.model_json_schema())
                    
                    if result.matches_schema:
                        news_collection = NewsCollection.model_validate(result.parsed_response)
                        self.logger.log_step(2, "News Extraction", "completed", f"Extracted {len(news_collection.articles)} articles from {site}")
                        self.logger.log_data_extraction("news", news_collection.dict(), site)
                        return {"news": news_collection.dict(), "news_source": site, "article_count": len(news_collection.articles)}
                    else:
                        self.logger.warning(f"Schema validation failed for {site}")
                        continue
                        
            except Exception as e:
                self.logger.warning(f"Failed to extract from {site}: {str(e)}")
                continue
        
        # If all sites failed
        self.logger.log_step(2, "News Extraction", "failed", "All news sites failed")
        self.add_warning("News extraction failed - all sites may be restricted in your region")
        return {"news": None, "news_extraction_error": "All sites failed"}
    
    def _step_extract_product(self) -> Dict[str, Any]:
        """Step 3: Extract product information."""
        self.logger.log_step(3, "Product Extraction", "starting")
        
        # Get region-appropriate e-commerce sites
        ecommerce_sites = self.config_manager.get_optimal_sites("ecommerce")
        
        for site in ecommerce_sites:
            try:
                self.logger.info(f"Trying e-commerce site: {site}")
                
                with NovaAct(
                    starting_page=site,
                    logs_directory="./demo/logs/product_extraction"
                ) as nova:
                    
                    # Search for a product
                    search_term = "laptop"
                    nova.act(f"search for {search_term}")
                    
                    # Select first result
                    nova.act("click on the first product result")
                    
                    # Extract product information
                    result = nova.act(
                        "Extract the product name, price, rating, availability status, and a brief description",
                        schema=ProductInfo.model_json_schema()
                    )
                    
                    if result.matches_schema:
                        product = ProductInfo.model_validate(result.parsed_response)
                        self.logger.log_step(3, "Product Extraction", "completed", f"Extracted product from {site}")
                        self.logger.log_data_extraction("product", product.dict(), site)
                        return {"product": product.dict(), "product_source": site}
                    else:
                        self.logger.warning(f"Product schema validation failed for {site}")
                        continue
                        
            except Exception as e:
                self.logger.warning(f"Failed to extract product from {site}: {str(e)}")
                continue
        
        # If all sites failed
        self.logger.log_step(3, "Product Extraction", "failed", "All e-commerce sites failed")
        self.add_warning("Product extraction failed - sites may be restricted or unavailable")
        return {"product": None, "product_extraction_error": "All sites failed"}
    
    def _step_boolean_extraction(self) -> Dict[str, Any]:
        """Step 4: Boolean extraction demo."""
        self.logger.log_step(4, "Boolean Extraction", "starting")
        
        try:
            # Use a simple, reliable site for boolean extraction
            with NovaAct(
                starting_page="https://example.com",
                logs_directory="./demo/logs/boolean_extraction"
            ) as nova:
                
                # Simple boolean questions
                questions = [
                    "Is there a heading on this page?",
                    "Does this page contain the word 'Example'?",
                    "Is this page longer than 100 words?"
                ]
                
                boolean_results = {}
                
                for i, question in enumerate(questions):
                    try:
                        result = nova.act(question, schema=BOOL_SCHEMA)
                        if result.matches_schema:
                            boolean_results[f"question_{i+1}"] = {
                                "question": question,
                                "answer": result.parsed_response
                            }
                        else:
                            boolean_results[f"question_{i+1}"] = {
                                "question": question,
                                "answer": None,
                                "error": "Schema validation failed"
                            }
                    except Exception as e:
                        boolean_results[f"question_{i+1}"] = {
                            "question": question,
                            "answer": None,
                            "error": str(e)
                        }
                
                self.logger.log_step(4, "Boolean Extraction", "completed", f"Processed {len(questions)} boolean questions")
                self.logger.log_data_extraction("boolean_results", boolean_results, "example.com")
                return {"boolean_extraction": boolean_results}
                
        except Exception as e:
            self.logger.log_step(4, "Boolean Extraction", "failed", str(e))
            return {"boolean_extraction": None, "boolean_error": str(e)}


def run_extraction_demo():
    """Run the information extraction demo."""
    print("📊 Starting Enhanced Information Extraction Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = InformationExtractionDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted:
            print("\n📋 Extraction Summary:")
            
            # Books
            if result.data_extracted.get("books"):
                book_count = result.data_extracted.get("book_count", 0)
                print(f"   📚 Books extracted: {book_count}")
            
            # News
            if result.data_extracted.get("news"):
                article_count = result.data_extracted.get("article_count", 0)
                news_source = result.data_extracted.get("news_source", "unknown")
                print(f"   📰 News articles extracted: {article_count} from {news_source}")
            
            # Product
            if result.data_extracted.get("product"):
                product_source = result.data_extracted.get("product_source", "unknown")
                print(f"   🛍️  Product extracted from: {product_source}")
            
            # Boolean
            if result.data_extracted.get("boolean_extraction"):
                boolean_count = len(result.data_extracted["boolean_extraction"])
                print(f"   ✅ Boolean questions processed: {boolean_count}")
    else:
        print("❌ Demo encountered issues:")
        for error in result.errors:
            print(f"   • {error.error_type}: {error.message}")
    
    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   • {warning}")
    
    print(f"📄 Detailed logs: {result.log_path}")
    
    return result


def main():
    """Main function to run the demo."""
    print("Nova Act Enhanced Information Extraction Demo")
    print("=" * 50)
    
    # Run the demo
    result = run_extraction_demo()
    
    if result.success:
        print("\n🎉 Information extraction demo completed successfully!")
        print("This demo showcased:")
        print("  • Structured data extraction with Pydantic schemas")
        print("  • Geographic-aware site selection")
        print("  • Robust error handling with fallbacks")
        print("  • Multiple extraction strategies")
    else:
        print("\n⚠️ Demo encountered some issues, but this is expected.")
        print("The framework handled errors gracefully and provided useful feedback.")


if __name__ == "__main__":
    main()
