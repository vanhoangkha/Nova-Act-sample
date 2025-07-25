#!/usr/bin/env python3
"""
Vietnam E-commerce Price Monitoring Sample

This sample demonstrates how to monitor product prices across Vietnamese e-commerce sites
like Shopee, Lazada, Tiki, and Sendo.
"""

import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional

from nova_act import NovaAct, BOOL_SCHEMA


class VietnamProductPrice(BaseModel):
    product_name: str
    price: float
    currency: str = "VND"
    discount_percent: Optional[float] = None
    original_price: Optional[float] = None
    availability: str
    seller: Optional[str] = None
    rating: Optional[float] = None
    sold_count: Optional[str] = None
    url: str
    timestamp: str


class VietnamPriceMonitor:
    def __init__(self, products_to_monitor: List[dict]):
        self.products = products_to_monitor
        self.price_history = []
    
    def check_single_product(self, product_info: dict) -> Optional[VietnamProductPrice]:
        """Check price for a single product on Vietnamese e-commerce sites"""
        try:
            with NovaAct(starting_page=product_info['url']) as nova:
                # Wait for page to load
                time.sleep(3)
                
                # Check if product is available
                availability_result = nova.act(
                    "Sản phẩm này có còn hàng không? Tìm nút 'Mua ngay', 'Thêm vào giỏ hàng', hoặc 'Còn hàng'",
                    schema=BOOL_SCHEMA
                )
                
                availability = "Còn hàng" if (availability_result.matches_schema and availability_result.parsed_response) else "Hết hàng"
                
                # Extract product details
                product_schema = VietnamProductPrice.model_json_schema()
                result = nova.act(
                    f"""Trích xuất thông tin sản phẩm từ trang này:
                    - Tên sản phẩm
                    - Giá hiện tại (chỉ số, không có ký tự)
                    - Phần trăm giảm giá (nếu có)
                    - Giá gốc trước khi giảm (nếu có)
                    - Tên người bán hoặc shop
                    - Đánh giá sao (nếu có)
                    - Số lượng đã bán (nếu có)
                    
                    Sử dụng URL: {product_info['url']} và trạng thái: {availability}
                    """,
                    schema=product_schema
                )
                
                if result.matches_schema:
                    product_price = VietnamProductPrice.model_validate(result.parsed_response)
                    product_price.timestamp = datetime.now().isoformat()
                    return product_price
                    
        except Exception as e:
            print(f"Lỗi khi kiểm tra sản phẩm {product_info['url']}: {e}")
            return None
    
    def monitor_prices(self, max_workers: int = 3) -> List[VietnamProductPrice]:
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
                        price_display = f"{price_data.price:,.0f} {price_data.currency}"
                        if price_data.discount_percent:
                            price_display += f" (giảm {price_data.discount_percent}%)"
                        print(f"✓ {price_data.product_name}: {price_display} ({price_data.availability})")
                    else:
                        print(f"✗ Không thể lấy giá cho {product_info['url']}")
                except Exception as e:
                    print(f"✗ Lỗi xử lý {product_info['url']}: {e}")
        
        self.price_history.extend(current_prices)
        return current_prices
    
    def save_results(self, filename: str = "vietnam_price_history.json"):
        """Save price history to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([price.dict() for price in self.price_history], f, indent=2, ensure_ascii=False)
        print(f"Lịch sử giá đã được lưu vào {filename}")
    
    def find_best_deals(self, min_discount: float = 20.0) -> List[dict]:
        """Find products with significant discounts"""
        best_deals = []
        
        for price in self.price_history:
            if price.discount_percent and price.discount_percent >= min_discount:
                deal_info = {
                    'product': price.product_name,
                    'current_price': price.price,
                    'original_price': price.original_price,
                    'discount_percent': price.discount_percent,
                    'savings': price.original_price - price.price if price.original_price else 0,
                    'seller': price.seller,
                    'url': price.url
                }
                best_deals.append(deal_info)
        
        # Sort by discount percentage
        best_deals.sort(key=lambda x: x['discount_percent'], reverse=True)
        return best_deals
    
    def generate_vietnam_report(self) -> dict:
        """Generate Vietnam-specific market report"""
        if not self.price_history:
            return {"error": "Không có dữ liệu để phân tích"}
        
        # Price statistics
        prices = [p.price for p in self.price_history if p.price > 0]
        price_stats = {
            "total_products": len(self.price_history),
            "average_price": sum(prices) / len(prices) if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "currency": "VND"
        }
        
        # Discount analysis
        discounted_products = [p for p in self.price_history if p.discount_percent]
        discount_stats = {
            "products_on_sale": len(discounted_products),
            "average_discount": sum(p.discount_percent for p in discounted_products) / len(discounted_products) if discounted_products else 0,
            "max_discount": max(p.discount_percent for p in discounted_products) if discounted_products else 0
        }
        
        # Platform analysis
        platform_stats = {}
        for price in self.price_history:
            if 'shopee' in price.url.lower():
                platform = 'Shopee'
            elif 'lazada' in price.url.lower():
                platform = 'Lazada'
            elif 'tiki' in price.url.lower():
                platform = 'Tiki'
            elif 'sendo' in price.url.lower():
                platform = 'Sendo'
            else:
                platform = 'Khác'
            
            platform_stats[platform] = platform_stats.get(platform, 0) + 1
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "price_statistics": price_stats,
            "discount_analysis": discount_stats,
            "platform_distribution": platform_stats,
            "best_deals": self.find_best_deals(),
            "detailed_results": [price.dict() for price in self.price_history]
        }


def main():
    # Vietnamese e-commerce products to monitor
    vietnam_products = [
        {
            'url': 'https://shopee.vn/Điện-thoại-iPhone-15-128GB-i.4.123456789',  # Example URL
            'expected_name': 'iPhone 15'
        },
        {
            'url': 'https://www.lazada.vn/products/laptop-asus-vivobook-i.123456789.html',  # Example URL
            'expected_name': 'Laptop Asus Vivobook'
        },
        {
            'url': 'https://tiki.vn/may-loc-nuoc-kangaroo-p123456789.html',  # Example URL
            'expected_name': 'Máy lọc nước Kangaroo'
        }
    ]
    
    monitor = VietnamPriceMonitor(vietnam_products)
    
    print("🔍 Bắt đầu theo dõi giá sản phẩm tại Việt Nam...")
    current_prices = monitor.monitor_prices()
    
    print(f"\n📊 Đã theo dõi {len(current_prices)} sản phẩm")
    
    # Save results
    monitor.save_results()
    
    # Generate Vietnam-specific report
    report = monitor.generate_vietnam_report()
    
    # Display key insights
    if 'price_statistics' in report:
        stats = report['price_statistics']
        print(f"\n💰 Thống kê giá:")
        print(f"  • Giá trung bình: {stats['average_price']:,.0f} {stats['currency']}")
        print(f"  • Khoảng giá: {stats['min_price']:,.0f} - {stats['max_price']:,.0f} {stats['currency']}")
    
    if 'discount_analysis' in report:
        discount = report['discount_analysis']
        print(f"\n🔥 Phân tích khuyến mãi:")
        print(f"  • Sản phẩm đang giảm giá: {discount['products_on_sale']}")
        print(f"  • Giảm giá trung bình: {discount['average_discount']:.1f}%")
        print(f"  • Giảm giá cao nhất: {discount['max_discount']:.1f}%")
    
    if 'platform_distribution' in report:
        print(f"\n🛒 Phân bố theo sàn:")
        for platform, count in report['platform_distribution'].items():
            print(f"  • {platform}: {count} sản phẩm")
    
    # Show best deals
    best_deals = report.get('best_deals', [])
    if best_deals:
        print(f"\n💎 Deal tốt nhất:")
        for deal in best_deals[:3]:
            savings = f"{deal['savings']:,.0f} VND" if deal['savings'] else "N/A"
            print(f"  • {deal['product']}: giảm {deal['discount_percent']:.1f}% (tiết kiệm {savings})")
    
    return current_prices


if __name__ == "__main__":
    main()
