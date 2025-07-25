#!/usr/bin/env python3
"""
Nova Act Demo: Real Estate Search and Analysis
==============================================

This demo shows how to search for properties, extract property details,
and perform analysis on real estate listings using Nova Act.

Based on the apartments_caltrain.py sample mentioned in the Nova Act README.
"""

import os
import sys
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from nova_act import NovaAct, ActError

class Property(BaseModel):
    address: str
    price: str
    bedrooms: Optional[str] = None
    bathrooms: Optional[str] = None
    square_feet: Optional[str] = None
    description: Optional[str] = None
    listing_url: Optional[str] = None

class PropertyList(BaseModel):
    properties: List[Property]
    search_location: str
    total_found: Optional[str] = None

class TransportationInfo(BaseModel):
    property_address: str
    nearest_station: Optional[str] = None
    distance_to_station: Optional[str] = None
    travel_time: Optional[str] = None

def search_properties_demo():
    """
    Demo for searching properties on a real estate website
    """
    print("🏠 Starting Property Search Demo")
    print("=" * 40)
    
    search_locations = ["San Francisco, CA", "Seattle, WA", "Austin, TX"]
    all_properties = []
    
    try:
        for location in search_locations:
            print(f"🔍 Searching properties in {location}...")
            
            with NovaAct(
                starting_page="https://www.zillow.com",
                logs_directory=f"./demo/logs/property_search_{location.replace(', ', '_').replace(' ', '_')}"
            ) as nova:
                # Search for properties in the location
                nova.act(f"search for homes for sale in {location}")
                
                # Apply some basic filters
                nova.act("set price range to $300,000 - $800,000 if filter options are available")
                nova.act("filter for 2+ bedrooms if filter options are available")
                
                # Extract property listings
                result = nova.act(
                    f"Extract the first 5 property listings with address, price, bedrooms, bathrooms, and square footage",
                    schema=PropertyList.model_json_schema()
                )
                
                if result.matches_schema:
                    property_list = PropertyList.model_validate(result.parsed_response)
                    property_list.search_location = location
                    
                    print(f"✅ Found {len(property_list.properties)} properties in {location}")
                    
                    for prop in property_list.properties:
                        all_properties.append(prop)
                        print(f"  📍 {prop.address} - {prop.price}")
                else:
                    print(f"❌ Failed to extract properties from {location}")
        
        return all_properties
        
    except Exception as e:
        print(f"❌ Error during property search demo: {e}")
        return []

def property_details_extraction_demo():
    """
    Demo for extracting detailed information from individual property listings
    """
    print("\n🔍 Starting Property Details Extraction Demo")
    print("=" * 55)
    
    try:
        with NovaAct(
            starting_page="https://www.zillow.com",
            logs_directory="./demo/logs/property_details"
        ) as nova:
            print("🏠 Searching for a specific property...")
            
            # Search for properties
            nova.act("search for homes for sale in San Francisco, CA")
            
            # Click on first property for detailed view
            nova.act("click on the first property listing to view details")
            
            # Extract comprehensive property details
            result = nova.act(
                """Extract detailed property information including:
                - Full address
                - Asking price
                - Number of bedrooms and bathrooms
                - Square footage
                - Lot size
                - Year built
                - Property type
                - Key features or amenities
                - Property description""",
                schema=Property.model_json_schema()
            )
            
            if result.matches_schema:
                property_details = Property.model_validate(result.parsed_response)
                
                print("✅ Successfully extracted property details:")
                print(f"📍 Address: {property_details.address}")
                print(f"💰 Price: {property_details.price}")
                if property_details.bedrooms:
                    print(f"🛏️ Bedrooms: {property_details.bedrooms}")
                if property_details.bathrooms:
                    print(f"🚿 Bathrooms: {property_details.bathrooms}")
                if property_details.square_feet:
                    print(f"📐 Square Feet: {property_details.square_feet}")
                if property_details.description:
                    print(f"📝 Description: {property_details.description[:100]}...")
                
                return property_details
            else:
                print("❌ Failed to extract property details")
                return None
                
    except Exception as e:
        print(f"❌ Error during property details extraction: {e}")
        return None

def transportation_analysis_demo():
    """
    Demo for analyzing transportation options for properties
    """
    print("\n🚊 Starting Transportation Analysis Demo")
    print("=" * 50)
    
    # Sample properties for transportation analysis
    sample_properties = [
        "123 Market Street, San Francisco, CA",
        "456 Mission Street, San Francisco, CA",
        "789 Valencia Street, San Francisco, CA"
    ]
    
    transportation_results = []
    
    def analyze_property_transportation(property_address: str) -> Optional[TransportationInfo]:
        """Analyze transportation options for a single property"""
        try:
            with NovaAct(
                starting_page="https://www.google.com/maps",
                logs_directory=f"./demo/logs/transport_{property_address.replace(' ', '_').replace(',', '')[:20]}"
            ) as nova:
                print(f"🗺️ Analyzing transportation for {property_address}...")
                
                # Search for the property address
                nova.act(f"search for {property_address}")
                
                # Look for nearby transit options
                nova.act("look for nearby public transportation, specifically train or subway stations")
                
                # Extract transportation information
                result = nova.act(
                    f"What is the nearest train/subway station to {property_address} and how far is it?",
                    schema=TransportationInfo.model_json_schema()
                )
                
                if result.matches_schema:
                    transport_info = TransportationInfo.model_validate(result.parsed_response)
                    transport_info.property_address = property_address
                    
                    print(f"✅ Transportation analysis completed for {property_address}")
                    return transport_info
                else:
                    print(f"❌ Failed to analyze transportation for {property_address}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error analyzing transportation for {property_address}: {e}")
            return None
    
    # Analyze transportation for all properties in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_property = {
            executor.submit(analyze_property_transportation, prop): prop 
            for prop in sample_properties
        }
        
        for future in as_completed(future_to_property.keys()):
            property_address = future_to_property[future]
            try:
                transport_info = future.result()
                if transport_info:
                    transportation_results.append(transport_info)
            except Exception as e:
                print(f"❌ Error processing {property_address}: {e}")
    
    # Display transportation analysis results
    print("\n🚊 Transportation Analysis Results:")
    print("=" * 40)
    
    for info in transportation_results:
        print(f"📍 {info.property_address}")
        if info.nearest_station:
            print(f"   🚉 Nearest Station: {info.nearest_station}")
        if info.distance_to_station:
            print(f"   📏 Distance: {info.distance_to_station}")
        if info.travel_time:
            print(f"   ⏱️ Travel Time: {info.travel_time}")
        print()
    
    return transportation_results

def property_comparison_demo():
    """
    Demo for comparing multiple properties side by side
    """
    print("\n⚖️ Starting Property Comparison Demo")
    print("=" * 45)
    
    try:
        with NovaAct(
            starting_page="https://www.zillow.com",
            logs_directory="./demo/logs/property_comparison"
        ) as nova:
            print("🏠 Setting up property comparison...")
            
            # Search for properties
            nova.act("search for homes for sale in San Francisco, CA")
            
            # Apply filters for comparison
            nova.act("filter for properties between $500,000 - $700,000")
            nova.act("filter for 2-3 bedroom properties")
            
            # Extract multiple properties for comparison
            result = nova.act(
                """Extract the first 3 properties for comparison including:
                - Address
                - Price
                - Bedrooms/Bathrooms
                - Square footage
                - Key features""",
                schema=PropertyList.model_json_schema()
            )
            
            if result.matches_schema:
                properties = PropertyList.model_validate(result.parsed_response)
                
                print("✅ Property Comparison Results:")
                print("=" * 35)
                
                for i, prop in enumerate(properties.properties, 1):
                    print(f"\n🏠 Property {i}:")
                    print(f"   📍 Address: {prop.address}")
                    print(f"   💰 Price: {prop.price}")
                    if prop.bedrooms:
                        print(f"   🛏️ Bedrooms: {prop.bedrooms}")
                    if prop.bathrooms:
                        print(f"   🚿 Bathrooms: {prop.bathrooms}")
                    if prop.square_feet:
                        print(f"   📐 Square Feet: {prop.square_feet}")
                
                # Analyze which property offers best value
                print("\n📊 Value Analysis:")
                print("Comparing properties based on price per square foot and features...")
                
                return properties
            else:
                print("❌ Failed to extract properties for comparison")
                return None
                
    except Exception as e:
        print(f"❌ Error during property comparison demo: {e}")
        return None

def market_analysis_demo():
    """
    Demo for analyzing real estate market trends
    """
    print("\n📈 Starting Market Analysis Demo")
    print("=" * 40)
    
    markets_to_analyze = ["San Francisco, CA", "Austin, TX", "Seattle, WA"]
    market_data = []
    
    try:
        for market in markets_to_analyze:
            print(f"📊 Analyzing market trends in {market}...")
            
            with NovaAct(
                starting_page="https://www.zillow.com",
                logs_directory=f"./demo/logs/market_analysis_{market.replace(', ', '_').replace(' ', '_')}"
            ) as nova:
                # Search for market information
                nova.act(f"search for homes for sale in {market}")
                
                # Look for market insights or trends
                nova.act("look for market insights, price trends, or market statistics on the page")
                
                # Extract market information
                market_info = nova.act(f"What are the current market trends, average prices, and market conditions in {market}?")
                
                market_data.append({
                    "location": market,
                    "analysis": market_info.response
                })
                
                print(f"✅ Market analysis completed for {market}")
        
        # Display market analysis
        print("\n📈 Market Analysis Results:")
        print("=" * 30)
        
        for data in market_data:
            print(f"\n🏙️ {data['location']}:")
            print(f"   📊 {data['analysis'][:200]}...")
        
        return market_data
        
    except Exception as e:
        print(f"❌ Error during market analysis demo: {e}")
        return []

def rental_vs_buy_analysis_demo():
    """
    Demo for analyzing rental vs buying options
    """
    print("\n🏠 Starting Rental vs Buy Analysis Demo")
    print("=" * 50)
    
    try:
        # Analyze buying options
        print("💰 Analyzing buying options...")
        with NovaAct(
            starting_page="https://www.zillow.com",
            logs_directory="./demo/logs/buy_analysis"
        ) as nova:
            nova.act("search for homes for sale in San Francisco, CA")
            nova.act("filter for 2 bedroom properties")
            
            buy_result = nova.act("What are the average prices for 2-bedroom homes for sale?")
            buy_info = buy_result.response
        
        # Analyze rental options
        print("🏠 Analyzing rental options...")
        with NovaAct(
            starting_page="https://www.apartments.com",
            logs_directory="./demo/logs/rental_analysis"
        ) as nova:
            nova.act("search for 2 bedroom apartments for rent in San Francisco, CA")
            
            rent_result = nova.act("What are the average rental prices for 2-bedroom apartments?")
            rent_info = rent_result.response
        
        # Display comparison
        print("\n📊 Rental vs Buy Analysis:")
        print("=" * 30)
        print(f"🏠 Buying: {buy_info[:150]}...")
        print(f"🏠 Renting: {rent_info[:150]}...")
        
        return {"buying": buy_info, "renting": rent_info}
        
    except Exception as e:
        print(f"❌ Error during rental vs buy analysis: {e}")
        return {}

def main():
    """Main function to run all real estate demos"""
    print("Nova Act Real Estate Demo Suite")
    print("===============================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("./demo/logs", exist_ok=True)
    
    print("\n🏠 Real Estate Demo Options:")
    print("1. Property search across multiple locations")
    print("2. Detailed property information extraction")
    print("3. Transportation analysis for properties")
    print("4. Property comparison")
    print("5. Market trend analysis")
    print("6. Rental vs buy analysis")
    print("7. Run all demos")
    
    choice = input("\nSelect demo (1-7): ").strip()
    
    if choice == "1":
        search_properties_demo()
    elif choice == "2":
        property_details_extraction_demo()
    elif choice == "3":
        transportation_analysis_demo()
    elif choice == "4":
        property_comparison_demo()
    elif choice == "5":
        market_analysis_demo()
    elif choice == "6":
        rental_vs_buy_analysis_demo()
    elif choice == "7":
        # Run all demos
        results = []
        results.append(search_properties_demo())
        results.append(property_details_extraction_demo())
        results.append(transportation_analysis_demo())
        results.append(property_comparison_demo())
        results.append(market_analysis_demo())
        results.append(rental_vs_buy_analysis_demo())
        
        successful = sum(1 for result in results if result)
        total = len(results)
        
        print(f"\n📊 Real Estate Demo Summary: {successful}/{total} successful")
        
        if successful == total:
            print("🎉 All real estate demos completed successfully!")
            print("💡 This demonstrates Nova Act's capability for complex data extraction and analysis workflows")
        else:
            print("⚠️ Some demos encountered issues. Check the logs for details.")
    else:
        print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()
