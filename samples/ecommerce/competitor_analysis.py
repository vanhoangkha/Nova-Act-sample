#!/usr/bin/env python3
"""
E-commerce Competitor Analysis Sample

This sample demonstrates how to analyze competitor products, pricing, and features
across multiple e-commerce platforms.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from nova_act import NovaAct


class CompetitorProduct(BaseModel):
    site_name: str
    product_name: str
    price: float
    currency: str
    rating: Optional[float]
    review_count: Optional[int]
    key_features: List[str]
    availability: str
    url: str
    analyzed_at: str


class CompetitorAnalyzer:
    def __init__(self):
        self.results = []
    
    def analyze_product_on_site(self, search_term: str, site_config: dict) -> Optional[CompetitorProduct]:
        """Analyze a product on a specific e-commerce site"""
        try:
            with NovaAct(starting_page=site_config['base_url']) as nova:
                # Search for the product
                nova.act(f"search for '{search_term}'")
                
                # Select the first relevant result
                nova.act("click on the first product result that matches the search term")
                
                # Extract comprehensive product information
                product_schema = CompetitorProduct.model_json_schema()
                result = nova.act(
                    f"""Extract detailed product information from this page:
                    - Product name
                    - Price (convert to number)
                    - Currency
                    - Customer rating (if available)
                    - Number of reviews (if available)
                    - Key features or specifications (list format)
                    - Availability status
                    
                    Use site_name: '{site_config['name']}' and url: '{nova.page.url}'
                    """,
                    schema=product_schema
                )
                
                if result.matches_schema:
                    product = CompetitorProduct.model_validate(result.parsed_response)
                    product.analyzed_at = datetime.now().isoformat()
                    return product
                    
        except Exception as e:
            print(f"Error analyzing {search_term} on {site_config['name']}: {e}")
            return None
    
    def compare_across_sites(self, search_term: str, sites: List[dict], max_workers: int = 3) -> List[CompetitorProduct]:
        """Compare a product across multiple e-commerce sites"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_site = {
                executor.submit(self.analyze_product_on_site, search_term, site): site 
                for site in sites
            }
            
            for future in as_completed(future_to_site.keys()):
                site_config = future_to_site[future]
                try:
                    product_data = future.result()
                    if product_data:
                        results.append(product_data)
                        print(f"✓ {site_config['name']}: {product_data.product_name} - ${product_data.price}")
                    else:
                        print(f"✗ Failed to analyze on {site_config['name']}")
                except Exception as e:
                    print(f"✗ Error with {site_config['name']}: {e}")
        
        self.results.extend(results)
        return results
    
    def generate_comparison_report(self, products: List[CompetitorProduct]) -> Dict:
        """Generate a comprehensive comparison report"""
        if not products:
            return {"error": "No products to compare"}
        
        # Price analysis
        prices = [p.price for p in products if p.price > 0]
        price_analysis = {
            "lowest_price": min(prices) if prices else 0,
            "highest_price": max(prices) if prices else 0,
            "average_price": sum(prices) / len(prices) if prices else 0,
            "price_range": max(prices) - min(prices) if prices else 0
        }
        
        # Rating analysis
        ratings = [p.rating for p in products if p.rating is not None]
        rating_analysis = {
            "average_rating": sum(ratings) / len(ratings) if ratings else None,
            "highest_rated_site": max(products, key=lambda x: x.rating or 0).site_name if ratings else None
        }
        
        # Feature analysis
        all_features = []
        for product in products:
            all_features.extend(product.key_features)
        
        feature_frequency = {}
        for feature in all_features:
            feature_frequency[feature] = feature_frequency.get(feature, 0) + 1
        
        common_features = sorted(feature_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Best value analysis
        best_value = None
        if prices and ratings:
            value_scores = []
            for product in products:
                if product.price > 0 and product.rating:
                    value_score = product.rating / product.price * 100  # Rating per dollar
                    value_scores.append((product, value_score))
            
            if value_scores:
                best_value = max(value_scores, key=lambda x: x[1])[0]
        
        return {
            "search_term": products[0].product_name if products else "Unknown",
            "sites_analyzed": len(products),
            "analysis_date": datetime.now().isoformat(),
            "price_analysis": price_analysis,
            "rating_analysis": rating_analysis,
            "common_features": common_features,
            "best_value_product": {
                "site": best_value.site_name,
                "price": best_value.price,
                "rating": best_value.rating,
                "url": best_value.url
            } if best_value else None,
            "detailed_results": [product.dict() for product in products]
        }
    
    def save_report(self, report: Dict, filename: str = None):
        """Save comparison report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"competitor_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Competitor analysis report saved to {filename}")


def main():
    # Define e-commerce sites to analyze
    sites_to_analyze = [
        {
            'name': 'Amazon',
            'base_url': 'https://www.amazon.com'
        },
        {
            'name': 'Best Buy',
            'base_url': 'https://www.bestbuy.com'
        },
        {
            'name': 'Target',
            'base_url': 'https://www.target.com'
        }
    ]
    
    # Product to analyze
    search_term = "wireless bluetooth headphones"
    
    analyzer = CompetitorAnalyzer()
    
    print(f"🔍 Analyzing '{search_term}' across {len(sites_to_analyze)} sites...")
    
    # Compare across sites
    products = analyzer.compare_across_sites(search_term, sites_to_analyze)
    
    if products:
        print(f"\n📊 Successfully analyzed {len(products)} products")
        
        # Generate comparison report
        report = analyzer.generate_comparison_report(products)
        
        # Display key insights
        print(f"\n💰 Price Range: ${report['price_analysis']['lowest_price']:.2f} - ${report['price_analysis']['highest_price']:.2f}")
        print(f"📈 Average Price: ${report['price_analysis']['average_price']:.2f}")
        
        if report['rating_analysis']['average_rating']:
            print(f"⭐ Average Rating: {report['rating_analysis']['average_rating']:.1f}")
        
        if report['best_value_product']:
            best = report['best_value_product']
            print(f"🏆 Best Value: {best['site']} (${best['price']}, {best['rating']}⭐)")
        
        print(f"\n🔧 Most Common Features:")
        for feature, count in report['common_features'][:5]:
            print(f"  • {feature} ({count} sites)")
        
        # Save detailed report
        analyzer.save_report(report)
        
    else:
        print("❌ No products found for analysis")


if __name__ == "__main__":
    main()
