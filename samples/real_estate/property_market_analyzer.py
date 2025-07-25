#!/usr/bin/env python3
"""
Real Estate Market Analysis Sample

This sample demonstrates how to analyze real estate markets by extracting property
listings, comparing prices, and analyzing market trends across different areas.
"""

import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict

from nova_act import NovaAct


class PropertyListing(BaseModel):
    address: str
    price: Optional[float]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    square_feet: Optional[int]
    property_type: Optional[str]  # house, condo, townhouse, etc.
    listing_date: Optional[str]
    days_on_market: Optional[int]
    description: str
    amenities: List[str]
    neighborhood: Optional[str]
    source: str
    url: str
    extracted_at: str


class RealEstateAnalyzer:
    def __init__(self):
        self.properties = []
    
    def extract_properties_from_site(self, site_config: dict, search_criteria: dict, max_properties: int = 20) -> List[PropertyListing]:
        """Extract property listings from a real estate website"""
        properties = []
        
        try:
            with NovaAct(starting_page=site_config['url']) as nova:
                # Set up search criteria
                location = search_criteria.get('location', '')
                min_price = search_criteria.get('min_price', '')
                max_price = search_criteria.get('max_price', '')
                property_type = search_criteria.get('property_type', '')
                
                # Perform search
                search_query = f"search for properties in {location}"
                if min_price or max_price:
                    search_query += f" with price range {min_price} to {max_price}"
                if property_type:
                    search_query += f" property type {property_type}"
                
                nova.act(search_query)
                
                # Extract multiple property listings
                for i in range(max_properties):
                    try:
                        # Navigate to property listing
                        if i == 0:
                            nova.act("click on the first property listing")
                        else:
                            nova.act("go back to search results")
                            nova.act(f"click on the {i+1}th property listing")
                        
                        # Extract property details
                        property_schema = PropertyListing.model_json_schema()
                        result = nova.act(
                            f"""Extract comprehensive property information:
                            - Full property address
                            - Listing price (convert to number, remove $ and commas)
                            - Number of bedrooms
                            - Number of bathrooms
                            - Square footage
                            - Property type (house, condo, townhouse, etc.)
                            - When listed (if available)
                            - Days on market (if available)
                            - Property description (brief summary)
                            - Amenities and features (list format)
                            - Neighborhood name (if available)
                            
                            Use source: '{site_config['name']}' and current URL
                            """,
                            schema=property_schema
                        )
                        
                        if result.matches_schema:
                            property_listing = PropertyListing.model_validate(result.parsed_response)
                            property_listing.extracted_at = datetime.now().isoformat()
                            properties.append(property_listing)
                            print(f"✓ Extracted: {property_listing.address} - ${property_listing.price:,}" if property_listing.price else f"✓ Extracted: {property_listing.address}")
                        
                    except Exception as e:
                        print(f"Error extracting property {i+1} from {site_config['name']}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error accessing {site_config['name']}: {e}")
        
        return properties
    
    def analyze_market(self, search_criteria: dict, real_estate_sites: List[dict], max_workers: int = 2) -> List[PropertyListing]:
        """Analyze real estate market across multiple sites"""
        all_properties = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_site = {
                executor.submit(self.extract_properties_from_site, site, search_criteria): site 
                for site in real_estate_sites
            }
            
            for future in as_completed(future_to_site.keys()):
                site_config = future_to_site[future]
                try:
                    properties = future.result()
                    all_properties.extend(properties)
                    print(f"✓ {site_config['name']}: {len(properties)} properties")
                except Exception as e:
                    print(f"✗ Error with {site_config['name']}: {e}")
        
        self.properties.extend(all_properties)
        return all_properties
    
    def analyze_price_trends(self, properties: List[PropertyListing]) -> Dict:
        """Analyze price trends and statistics"""
        properties_with_price = [p for p in properties if p.price and p.price > 0]
        
        if not properties_with_price:
            return {"error": "No properties with valid prices found"}
        
        prices = [p.price for p in properties_with_price]
        prices.sort()
        
        # Price statistics
        price_stats = {
            "count": len(prices),
            "average": sum(prices) / len(prices),
            "median": prices[len(prices)//2],
            "min": min(prices),
            "max": max(prices),
            "range": max(prices) - min(prices)
        }
        
        # Price per square foot analysis
        price_per_sqft = []
        for prop in properties_with_price:
            if prop.square_feet and prop.square_feet > 0:
                price_per_sqft.append(prop.price / prop.square_feet)
        
        price_per_sqft_stats = {}
        if price_per_sqft:
            price_per_sqft.sort()
            price_per_sqft_stats = {
                "average": sum(price_per_sqft) / len(price_per_sqft),
                "median": price_per_sqft[len(price_per_sqft)//2],
                "min": min(price_per_sqft),
                "max": max(price_per_sqft)
            }
        
        # Price by property type
        price_by_type = {}
        for prop in properties_with_price:
            if prop.property_type:
                prop_type = prop.property_type.lower()
                if prop_type not in price_by_type:
                    price_by_type[prop_type] = []
                price_by_type[prop_type].append(prop.price)
        
        # Calculate averages by type
        avg_price_by_type = {}
        for prop_type, prices in price_by_type.items():
            avg_price_by_type[prop_type] = {
                "average": sum(prices) / len(prices),
                "count": len(prices),
                "min": min(prices),
                "max": max(prices)
            }
        
        return {
            "overall_price_stats": price_stats,
            "price_per_sqft_stats": price_per_sqft_stats,
            "price_by_property_type": avg_price_by_type
        }
    
    def analyze_market_inventory(self, properties: List[PropertyListing]) -> Dict:
        """Analyze market inventory and trends"""
        # Property type distribution
        property_types = {}
        for prop in properties:
            if prop.property_type:
                prop_type = prop.property_type.lower()
                property_types[prop_type] = property_types.get(prop_type, 0) + 1
        
        # Bedroom distribution
        bedroom_distribution = {}
        for prop in properties:
            if prop.bedrooms is not None:
                bedrooms = str(prop.bedrooms)
                bedroom_distribution[bedrooms] = bedroom_distribution.get(bedrooms, 0) + 1
        
        # Days on market analysis
        days_on_market = [p.days_on_market for p in properties if p.days_on_market is not None]
        dom_stats = {}
        if days_on_market:
            days_on_market.sort()
            dom_stats = {
                "average": sum(days_on_market) / len(days_on_market),
                "median": days_on_market[len(days_on_market)//2],
                "min": min(days_on_market),
                "max": max(days_on_market)
            }
        
        # Neighborhood analysis
        neighborhoods = {}
        for prop in properties:
            if prop.neighborhood:
                neighborhood = prop.neighborhood.lower()
                neighborhoods[neighborhood] = neighborhoods.get(neighborhood, 0) + 1
        
        top_neighborhoods = sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_properties": len(properties),
            "property_type_distribution": property_types,
            "bedroom_distribution": bedroom_distribution,
            "days_on_market_stats": dom_stats,
            "top_neighborhoods": [
                {"neighborhood": neighborhood.title(), "count": count}
                for neighborhood, count in top_neighborhoods
            ]
        }
    
    def find_best_value_properties(self, properties: List[PropertyListing], top_n: int = 10) -> List[Dict]:
        """Find properties with best value (price per square foot)"""
        value_properties = []
        
        for prop in properties:
            if prop.price and prop.square_feet and prop.price > 0 and prop.square_feet > 0:
                price_per_sqft = prop.price / prop.square_feet
                value_properties.append({
                    "property": prop,
                    "price_per_sqft": price_per_sqft,
                    "value_score": 1 / price_per_sqft  # Higher score = better value
                })
        
        # Sort by value score (descending)
        value_properties.sort(key=lambda x: x["value_score"], reverse=True)
        
        return [
            {
                "address": vp["property"].address,
                "price": vp["property"].price,
                "square_feet": vp["property"].square_feet,
                "price_per_sqft": round(vp["price_per_sqft"], 2),
                "bedrooms": vp["property"].bedrooms,
                "bathrooms": vp["property"].bathrooms,
                "property_type": vp["property"].property_type,
                "url": vp["property"].url
            }
            for vp in value_properties[:top_n]
        ]
    
    def generate_market_report(self, search_criteria: dict, properties: List[PropertyListing]) -> Dict:
        """Generate comprehensive real estate market report"""
        if not properties:
            return {"error": "No properties to analyze"}
        
        # Detailed analyses
        price_analysis = self.analyze_price_trends(properties)
        inventory_analysis = self.analyze_market_inventory(properties)
        best_value_properties = self.find_best_value_properties(properties)
        
        # Source distribution
        source_distribution = {}
        for prop in properties:
            source_distribution[prop.source] = source_distribution.get(prop.source, 0) + 1
        
        return {
            "search_criteria": search_criteria,
            "analysis_date": datetime.now().isoformat(),
            "summary": {
                "total_properties_analyzed": len(properties),
                "sources_searched": len(source_distribution),
                "properties_with_prices": len([p for p in properties if p.price])
            },
            "source_distribution": source_distribution,
            "price_analysis": price_analysis,
            "inventory_analysis": inventory_analysis,
            "best_value_properties": best_value_properties,
            "sample_properties": [
                {
                    "address": prop.address,
                    "price": prop.price,
                    "bedrooms": prop.bedrooms,
                    "bathrooms": prop.bathrooms,
                    "square_feet": prop.square_feet,
                    "property_type": prop.property_type
                }
                for prop in properties[:5]
            ],
            "detailed_properties": [prop.dict() for prop in properties]
        }
    
    def save_report(self, report: Dict, filename: str = None):
        """Save real estate market report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            location = report['search_criteria'].get('location', 'market').replace(' ', '_').lower()
            filename = f"real_estate_market_{location}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Real estate market report saved to {filename}")


def main():
    # Define real estate websites to search
    real_estate_sites = [
        {
            'name': 'Zillow',
            'url': 'https://www.zillow.com'
        },
        {
            'name': 'Realtor.com',
            'url': 'https://www.realtor.com'
        }
    ]
    
    # Search criteria
    search_criteria = {
        'location': 'Austin, TX',
        'min_price': '300000',
        'max_price': '600000',
        'property_type': 'house'
    }
    
    analyzer = RealEstateAnalyzer()
    
    print(f"🏠 Analyzing real estate market in {search_criteria['location']}...")
    
    # Analyze market
    properties = analyzer.analyze_market(search_criteria, real_estate_sites)
    
    if properties:
        print(f"\n📊 Successfully analyzed {len(properties)} properties")
        
        # Generate comprehensive report
        report = analyzer.generate_market_report(search_criteria, properties)
        
        # Display key insights
        print(f"\n📈 Market Summary:")
        print(f"  • Total Properties: {report['summary']['total_properties_analyzed']}")
        print(f"  • Properties with Prices: {report['summary']['properties_with_prices']}")
        
        if 'overall_price_stats' in report['price_analysis']:
            price_stats = report['price_analysis']['overall_price_stats']
            print(f"\n💰 Price Analysis:")
            print(f"  • Average Price: ${price_stats['average']:,.0f}")
            print(f"  • Median Price: ${price_stats['median']:,.0f}")
            print(f"  • Price Range: ${price_stats['min']:,.0f} - ${price_stats['max']:,.0f}")
        
        if 'price_per_sqft_stats' in report['price_analysis'] and report['price_analysis']['price_per_sqft_stats']:
            psf_stats = report['price_analysis']['price_per_sqft_stats']
            print(f"  • Avg Price/SqFt: ${psf_stats['average']:.0f}")
        
        print(f"\n🏘️ Top Neighborhoods:")
        for neighborhood in report['inventory_analysis']['top_neighborhoods'][:5]:
            print(f"  • {neighborhood['neighborhood']}: {neighborhood['count']} properties")
        
        print(f"\n💎 Best Value Properties:")
        for prop in report['best_value_properties'][:3]:
            print(f"  • {prop['address']}: ${prop['price']:,} (${prop['price_per_sqft']}/sqft)")
        
        # Save detailed report
        analyzer.save_report(report)
        
    else:
        print("❌ No properties found for analysis")


if __name__ == "__main__":
    main()
