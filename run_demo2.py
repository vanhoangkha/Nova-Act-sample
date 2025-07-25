#!/usr/bin/env python3
"""
Run Demo 2 with detailed error reporting
"""

import os
import traceback
from typing import List, Optional
from pydantic import BaseModel
from nova_act import NovaAct

# Define data models for extraction
class Book(BaseModel):
    title: str
    author: str
    price: Optional[str] = None
    rating: Optional[str] = None

class BookList(BaseModel):
    books: List[Book]

def run_information_extraction_demo():
    """
    Extract book information from a bookstore website
    """
    print("📚 Starting Information Extraction Demo")
    print("=" * 50)
    
    try:
        # Create logs directory
        os.makedirs("./demo/logs/book_extraction", exist_ok=True)
        
        with NovaAct(
            starting_page="https://books.toscrape.com/",
            logs_directory="./demo/logs/book_extraction",
            headless=True
        ) as nova:
            print("📖 Navigating to book catalog...")
            
            # Navigate to a specific category
            print("🔍 Looking for Travel category...")
            nova.act("click on 'Travel' category")
            
            # Extract book information
            print("📊 Extracting book information...")
            result = nova.act(
                "Extract information about the first 5 books shown including title, author, and price",
                schema=BookList.model_json_schema()
            )
            
            if result.matches_schema:
                book_list = BookList.model_validate(result.parsed_response)
                print(f"✅ Successfully extracted {len(book_list.books)} books:")
                for i, book in enumerate(book_list.books, 1):
                    print(f"  {i}. {book.title} by {book.author} - {book.price}")
                return True
            else:
                print("❌ Failed to extract books in expected format")
                print(f"Raw response: {result.response}")
                return False
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = run_information_extraction_demo()
    print(f"Final result: {'SUCCESS' if result else 'FAILED'}")
