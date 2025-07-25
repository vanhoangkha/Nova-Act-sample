#!/usr/bin/env python3
"""
Vietnam E-commerce Competitor Analysis Sample

This sample demonstrates how to analyze competitor products across Vietnamese
e-commerce platforms like Shopee, Lazada, Tiki, and Sendo.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from nova_act import NovaAct


class VietnamCompetitorProduct(BaseModel):
    platform_name: str
    product_name: str
    price: float
    currency: str = "VND"
    discount_percent: Optional[float] = None
    original_price: Optional[float] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    sold_count: Optional[str] = None
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    shipping_info: Optional[str] = None
    key_features: List[str]
    availability: str
    url: str
    analyzed_at: str


class VietnamCompetitorAnalyzer:
    def __init__(self):
        self.results = []
    
    def analyze_product_on_platform(self, search_term: str, platform_config: dict) -> Optional[VietnamCompetitorProduct]:
        """Analyze a product on a specific Vietnamese e-commerce platform"""
        try:
            with NovaAct(starting_page=platform_config['base_url']) as nova:
                # Search for the product in Vietnamese
                nova.act(f"tìm kiếm '{search_term}'")
                
                # Select the first relevant result
                nova.act("nhấp vào sản phẩm đầu tiên phù hợp với từ khóa tìm kiếm")
                
                # Extract comprehensive product information
                product_schema = VietnamCompetitorProduct.model_json_schema()
                result = nova.act(
                    f"""Trích xuất thông tin chi tiết sản phẩm từ trang này:
                    - Tên sản phẩm
                    - Giá hiện tại (chỉ số, không ký tự)
                    - Phần trăm giảm giá (nếu có)
                    - Giá gốc (nếu có)
                    - Đánh giá sao của sản phẩm
                    - Số lượng đánh giá
                    - Số lượng đã bán
                    - Tên người bán/shop
                    - Đánh giá của shop (nếu có)
                    - Thông tin vận chuyển
                    - Các tính năng chính của sản phẩm (danh sách)
                    - Tình trạng còn hàng
                    
                    Sử dụng platform_name: '{platform_config['name']}' và URL hiện tại
                    """,
                    schema=product_schema
                )
                
                if result.matches_schema:
                    product = VietnamCompetitorProduct.model_validate(result.parsed_response)
                    product.analyzed_at = datetime.now().isoformat()
                    return product
                    
        except Exception as e:
            print(f"Lỗi phân tích {search_term} trên {platform_config['name']}: {e}")
            return None
    
    def compare_across_platforms(self, search_term: str, platforms: List[dict], max_workers: int = 2) -> List[VietnamCompetitorProduct]:
        """Compare a product across multiple Vietnamese e-commerce platforms"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_platform = {
                executor.submit(self.analyze_product_on_platform, search_term, platform): platform 
                for platform in platforms
            }
            
            for future in as_completed(future_to_platform.keys()):
                platform_config = future_to_platform[future]
                try:
                    product_data = future.result()
                    if product_data:
                        results.append(product_data)
                        price_display = f"{product_data.price:,.0f} {product_data.currency}"
                        if product_data.discount_percent:
                            price_display += f" (giảm {product_data.discount_percent}%)"
                        print(f"✓ {platform_config['name']}: {product_data.product_name} - {price_display}")
                    else:
                        print(f"✗ Không thể phân tích trên {platform_config['name']}")
                except Exception as e:
                    print(f"✗ Lỗi với {platform_config['name']}: {e}")
        
        self.results.extend(results)
        return results
    
    def generate_vietnam_comparison_report(self, search_term: str, products: List[VietnamCompetitorProduct]) -> Dict:
        """Generate comprehensive comparison report for Vietnamese market"""
        if not products:
            return {"error": "Không có sản phẩm để so sánh"}
        
        # Price analysis
        prices = [p.price for p in products if p.price > 0]
        price_analysis = {
            "lowest_price": min(prices) if prices else 0,
            "highest_price": max(prices) if prices else 0,
            "average_price": sum(prices) / len(prices) if prices else 0,
            "price_range": max(prices) - min(prices) if prices else 0,
            "currency": "VND"
        }
        
        # Discount analysis
        discounted_products = [p for p in products if p.discount_percent]
        discount_analysis = {
            "products_on_sale": len(discounted_products),
            "average_discount": sum(p.discount_percent for p in discounted_products) / len(discounted_products) if discounted_products else 0,
            "best_discount": max(discounted_products, key=lambda x: x.discount_percent or 0) if discounted_products else None
        }
        
        # Rating analysis
        rated_products = [p for p in products if p.rating is not None]
        rating_analysis = {
            "average_rating": sum(p.rating for p in rated_products) / len(rated_products) if rated_products else None,
            "highest_rated": max(rated_products, key=lambda x: x.rating or 0) if rated_products else None,
            "products_with_ratings": len(rated_products)
        }
        
        # Platform comparison
        platform_comparison = {}
        for product in products:
            platform = product.platform_name
            platform_comparison[platform] = {
                "product_name": product.product_name,
                "price": product.price,
                "discount_percent": product.discount_percent,
                "rating": product.rating,
                "review_count": product.review_count,
                "sold_count": product.sold_count,
                "seller_name": product.seller_name
            }
        
        # Best value analysis (considering price and rating)
        best_value = None
        if prices and rated_products:
            value_scores = []
            for product in products:
                if product.price > 0 and product.rating:
                    # Value score: rating per 100k VND
                    value_score = product.rating / (product.price / 100000)
                    value_scores.append((product, value_score))
            
            if value_scores:
                best_value = max(value_scores, key=lambda x: x[1])[0]
        
        # Feature analysis
        all_features = []
        for product in products:
            all_features.extend(product.key_features)
        
        feature_frequency = {}
        for feature in all_features:
            feature_frequency[feature] = feature_frequency.get(feature, 0) + 1
        
        common_features = sorted(feature_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "search_term": search_term,
            "platforms_analyzed": len(products),
            "analysis_date": datetime.now().isoformat(),
            "price_analysis": price_analysis,
            "discount_analysis": discount_analysis,
            "rating_analysis": rating_analysis,
            "platform_comparison": platform_comparison,
            "common_features": common_features,
            "best_value_product": {
                "platform": best_value.platform_name,
                "product_name": best_value.product_name,
                "price": best_value.price,
                "rating": best_value.rating,
                "url": best_value.url
            } if best_value else None,
            "recommendations": self._generate_recommendations(products),
            "detailed_results": [product.dict() for product in products]
        }
    
    def _generate_recommendations(self, products: List[VietnamCompetitorProduct]) -> List[str]:
        """Generate shopping recommendations for Vietnamese consumers"""
        recommendations = []
        
        if not products:
            return recommendations
        
        # Price recommendations
        cheapest = min(products, key=lambda x: x.price or float('inf'))
        if cheapest.price:
            recommendations.append(f"Giá rẻ nhất: {cheapest.product_name} trên {cheapest.platform_name} - {cheapest.price:,.0f} VND")
        
        # Discount recommendations
        best_discount = max(products, key=lambda x: x.discount_percent or 0)
        if best_discount.discount_percent and best_discount.discount_percent > 0:
            recommendations.append(f"Giảm giá tốt nhất: {best_discount.product_name} trên {best_discount.platform_name} - giảm {best_discount.discount_percent}%")
        
        # Rating recommendations
        highest_rated = max(products, key=lambda x: x.rating or 0)
        if highest_rated.rating:
            recommendations.append(f"Đánh giá cao nhất: {highest_rated.product_name} trên {highest_rated.platform_name} - {highest_rated.rating} sao")
        
        # Sales recommendations
        best_seller = max(products, key=lambda x: int(''.join(filter(str.isdigit, x.sold_count or '0'))) or 0)
        if best_seller.sold_count:
            recommendations.append(f"Bán chạy nhất: {best_seller.product_name} trên {best_seller.platform_name} - đã bán {best_seller.sold_count}")
        
        return recommendations
    
    def save_report(self, report: Dict, filename: str = None):
        """Save comparison report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            search_term = report.get('search_term', 'product').replace(' ', '_').lower()
            filename = f"vietnam_competitor_analysis_{search_term}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Báo cáo phân tích đã được lưu vào {filename}")


def main():
    # Vietnamese e-commerce platforms to analyze
    vietnam_platforms = [
        {
            'name': 'Shopee',
            'base_url': 'https://shopee.vn'
        },
        {
            'name': 'Lazada',
            'base_url': 'https://www.lazada.vn'
        },
        {
            'name': 'Tiki',
            'base_url': 'https://tiki.vn'
        },
        {
            'name': 'Sendo',
            'base_url': 'https://www.sendo.vn'
        }
    ]
    
    # Product to analyze
    search_term = "tai nghe bluetooth"
    
    analyzer = VietnamCompetitorAnalyzer()
    
    print(f"🔍 Phân tích '{search_term}' trên {len(vietnam_platforms)} sàn thương mại điện tử...")
    
    # Compare across platforms
    products = analyzer.compare_across_platforms(search_term, vietnam_platforms)
    
    if products:
        print(f"\n📊 Đã phân tích thành công {len(products)} sản phẩm")
        
        # Generate comparison report
        report = analyzer.generate_vietnam_comparison_report(search_term, products)
        
        # Display key insights
        if 'price_analysis' in report:
            price = report['price_analysis']
            print(f"\n💰 Phân tích giá:")
            print(f"  • Khoảng giá: {price['lowest_price']:,.0f} - {price['highest_price']:,.0f} {price['currency']}")
            print(f"  • Giá trung bình: {price['average_price']:,.0f} {price['currency']}")
        
        if 'rating_analysis' in report and report['rating_analysis']['average_rating']:
            rating = report['rating_analysis']
            print(f"\n⭐ Phân tích đánh giá:")
            print(f"  • Đánh giá trung bình: {rating['average_rating']:.1f} sao")
            print(f"  • Sản phẩm có đánh giá: {rating['products_with_ratings']}/{len(products)}")
        
        if 'discount_analysis' in report and report['discount_analysis']['products_on_sale'] > 0:
            discount = report['discount_analysis']
            print(f"\n🔥 Phân tích khuyến mãi:")
            print(f"  • Sản phẩm đang giảm giá: {discount['products_on_sale']}/{len(products)}")
            print(f"  • Giảm giá trung bình: {discount['average_discount']:.1f}%")
        
        if 'best_value_product' in report and report['best_value_product']:
            best = report['best_value_product']
            print(f"\n🏆 Sản phẩm đáng mua nhất:")
            print(f"  • {best['product_name']} trên {best['platform']}")
            print(f"  • Giá: {best['price']:,.0f} VND, Đánh giá: {best['rating']} sao")
        
        if 'recommendations' in report:
            print(f"\n💡 Khuyến nghị:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        # Save detailed report
        analyzer.save_report(report)
        
    else:
        print("❌ Không tìm thấy sản phẩm để phân tích")


if __name__ == "__main__":
    main()
