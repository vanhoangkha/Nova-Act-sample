#!/usr/bin/env python3
"""
Vietnam Real Estate Market Analysis Sample

This sample demonstrates how to analyze Vietnamese real estate markets by extracting
property listings from sites like Batdongsan.com.vn, Nhadat24h.net, and Alonhadat.com.vn.
"""

import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict

from nova_act import NovaAct


class VietnamPropertyListing(BaseModel):
    address: str
    price: Optional[float]  # in VND
    price_per_m2: Optional[float]  # VND per m2
    area: Optional[float]  # in m2
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    property_type: Optional[str]  # nhà riêng, chung cư, đất nền, etc.
    legal_status: Optional[str]  # sổ đỏ, sổ hồng, etc.
    direction: Optional[str]  # hướng nhà
    listing_date: Optional[str]
    description: str
    amenities: List[str]
    district: Optional[str]
    ward: Optional[str]
    city: Optional[str]
    contact_info: Optional[str]
    source: str
    url: str
    extracted_at: str


class VietnamRealEstateAnalyzer:
    def __init__(self):
        self.properties = []
    
    def extract_properties_from_site(self, site_config: dict, search_criteria: dict, max_properties: int = 20) -> List[VietnamPropertyListing]:
        """Extract property listings from a Vietnamese real estate website"""
        properties = []
        
        try:
            with NovaAct(starting_page=site_config['url']) as nova:
                # Set up search criteria in Vietnamese
                location = search_criteria.get('location', '')
                min_price = search_criteria.get('min_price', '')
                max_price = search_criteria.get('max_price', '')
                property_type = search_criteria.get('property_type', '')
                
                # Perform search in Vietnamese
                search_query = f"tìm kiếm bất động sản tại {location}"
                if min_price or max_price:
                    search_query += f" với khoảng giá từ {min_price} đến {max_price}"
                if property_type:
                    search_query += f" loại {property_type}"
                
                nova.act(search_query)
                
                # Extract multiple property listings
                for i in range(max_properties):
                    try:
                        # Navigate to property listing
                        if i == 0:
                            nova.act("nhấp vào tin đăng bất động sản đầu tiên")
                        else:
                            nova.act("quay lại trang kết quả tìm kiếm")
                            nova.act(f"nhấp vào tin đăng bất động sản thứ {i+1}")
                        
                        # Extract property details
                        property_schema = VietnamPropertyListing.model_json_schema()
                        result = nova.act(
                            f"""Trích xuất thông tin chi tiết bất động sản:
                            - Địa chỉ đầy đủ
                            - Giá bán (chỉ số, không ký tự, đơn vị VND)
                            - Giá trên m2 (nếu có)
                            - Diện tích (m2)
                            - Số phòng ngủ
                            - Số phòng tắm/WC
                            - Loại hình bất động sản (nhà riêng, chung cư, đất nền, v.v.)
                            - Tình trạng pháp lý (sổ đỏ, sổ hồng, v.v.)
                            - Hướng nhà (nếu có)
                            - Ngày đăng tin
                            - Mô tả ngắn gọn
                            - Tiện ích xung quanh (danh sách)
                            - Quận/huyện
                            - Phường/xã
                            - Thành phố/tỉnh
                            - Thông tin liên hệ (nếu có)
                            
                            Sử dụng source: '{site_config['name']}' và URL hiện tại
                            """,
                            schema=property_schema
                        )
                        
                        if result.matches_schema:
                            property_listing = VietnamPropertyListing.model_validate(result.parsed_response)
                            property_listing.extracted_at = datetime.now().isoformat()
                            properties.append(property_listing)
                            
                            price_display = f"{property_listing.price/1000000000:.1f} tỷ VND" if property_listing.price and property_listing.price >= 1000000000 else f"{property_listing.price/1000000:.0f} triệu VND" if property_listing.price else "Thỏa thuận"
                            print(f"✓ Đã trích xuất: {property_listing.address} - {price_display}")
                        
                    except Exception as e:
                        print(f"Lỗi trích xuất bất động sản {i+1} từ {site_config['name']}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Lỗi truy cập {site_config['name']}: {e}")
        
        return properties
    
    def analyze_vietnam_market(self, search_criteria: dict, real_estate_sites: List[dict], max_workers: int = 2) -> List[VietnamPropertyListing]:
        """Analyze Vietnamese real estate market across multiple sites"""
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
                    print(f"✓ {site_config['name']}: {len(properties)} bất động sản")
                except Exception as e:
                    print(f"✗ Lỗi với {site_config['name']}: {e}")
        
        self.properties.extend(all_properties)
        return all_properties
    
    def analyze_vietnam_price_trends(self, properties: List[VietnamPropertyListing]) -> Dict:
        """Analyze price trends in Vietnamese real estate market"""
        properties_with_price = [p for p in properties if p.price and p.price > 0]
        
        if not properties_with_price:
            return {"error": "Không tìm thấy bất động sản có giá hợp lệ"}
        
        prices = [p.price for p in properties_with_price]
        prices.sort()
        
        # Price statistics in VND
        price_stats = {
            "count": len(prices),
            "average": sum(prices) / len(prices),
            "median": prices[len(prices)//2],
            "min": min(prices),
            "max": max(prices),
            "range": max(prices) - min(prices),
            "currency": "VND"
        }
        
        # Price per m2 analysis
        price_per_m2_data = []
        for prop in properties_with_price:
            if prop.area and prop.area > 0:
                price_per_m2_data.append(prop.price / prop.area)
        
        price_per_m2_stats = {}
        if price_per_m2_data:
            price_per_m2_data.sort()
            price_per_m2_stats = {
                "average": sum(price_per_m2_data) / len(price_per_m2_data),
                "median": price_per_m2_data[len(price_per_m2_data)//2],
                "min": min(price_per_m2_data),
                "max": max(price_per_m2_data)
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
        
        # Price by location (district)
        price_by_district = {}
        for prop in properties_with_price:
            if prop.district:
                district = prop.district.lower()
                if district not in price_by_district:
                    price_by_district[district] = []
                price_by_district[district].append(prop.price)
        
        avg_price_by_district = {}
        for district, prices in price_by_district.items():
            avg_price_by_district[district] = {
                "average": sum(prices) / len(prices),
                "count": len(prices),
                "min": min(prices),
                "max": max(prices)
            }
        
        return {
            "overall_price_stats": price_stats,
            "price_per_m2_stats": price_per_m2_stats,
            "price_by_property_type": avg_price_by_type,
            "price_by_district": avg_price_by_district
        }
    
    def analyze_vietnam_market_inventory(self, properties: List[VietnamPropertyListing]) -> Dict:
        """Analyze Vietnamese real estate market inventory"""
        # Property type distribution
        property_types = {}
        for prop in properties:
            if prop.property_type:
                prop_type = prop.property_type.lower()
                property_types[prop_type] = property_types.get(prop_type, 0) + 1
        
        # Legal status distribution
        legal_status = {}
        for prop in properties:
            if prop.legal_status:
                status = prop.legal_status.lower()
                legal_status[status] = legal_status.get(status, 0) + 1
        
        # Direction distribution (feng shui important in Vietnam)
        directions = {}
        for prop in properties:
            if prop.direction:
                direction = prop.direction.lower()
                directions[direction] = directions.get(direction, 0) + 1
        
        # Area distribution
        areas = [p.area for p in properties if p.area is not None and p.area > 0]
        area_stats = {}
        if areas:
            areas.sort()
            area_stats = {
                "average": sum(areas) / len(areas),
                "median": areas[len(areas)//2],
                "min": min(areas),
                "max": max(areas)
            }
        
        # Location analysis
        districts = {}
        cities = {}
        for prop in properties:
            if prop.district:
                district = prop.district.lower()
                districts[district] = districts.get(district, 0) + 1
            if prop.city:
                city = prop.city.lower()
                cities[city] = cities.get(city, 0) + 1
        
        top_districts = sorted(districts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_properties": len(properties),
            "property_type_distribution": property_types,
            "legal_status_distribution": legal_status,
            "direction_distribution": directions,
            "area_statistics": area_stats,
            "top_districts": [
                {"district": district.title(), "count": count}
                for district, count in top_districts
            ],
            "top_cities": [
                {"city": city.title(), "count": count}
                for city, count in top_cities
            ]
        }
    
    def find_vietnam_best_value_properties(self, properties: List[VietnamPropertyListing], top_n: int = 10) -> List[Dict]:
        """Find properties with best value in Vietnamese market"""
        value_properties = []
        
        for prop in properties:
            if prop.price and prop.area and prop.price > 0 and prop.area > 0:
                price_per_m2 = prop.price / prop.area
                
                # Calculate value score considering Vietnamese preferences
                value_score = 1 / price_per_m2  # Lower price per m2 = better value
                
                # Bonus for legal status
                if prop.legal_status and ('sổ đỏ' in prop.legal_status.lower() or 'sổ hồng' in prop.legal_status.lower()):
                    value_score *= 1.2
                
                # Bonus for good direction (feng shui)
                if prop.direction and any(direction in prop.direction.lower() for direction in ['đông', 'nam', 'đông nam']):
                    value_score *= 1.1
                
                value_properties.append({
                    "property": prop,
                    "price_per_m2": price_per_m2,
                    "value_score": value_score
                })
        
        # Sort by value score (descending)
        value_properties.sort(key=lambda x: x["value_score"], reverse=True)
        
        return [
            {
                "address": vp["property"].address,
                "price": vp["property"].price,
                "area": vp["property"].area,
                "price_per_m2": round(vp["price_per_m2"], 0),
                "bedrooms": vp["property"].bedrooms,
                "bathrooms": vp["property"].bathrooms,
                "property_type": vp["property"].property_type,
                "legal_status": vp["property"].legal_status,
                "direction": vp["property"].direction,
                "district": vp["property"].district,
                "url": vp["property"].url
            }
            for vp in value_properties[:top_n]
        ]
    
    def generate_vietnam_market_report(self, search_criteria: dict, properties: List[VietnamPropertyListing]) -> Dict:
        """Generate comprehensive Vietnamese real estate market report"""
        if not properties:
            return {"error": "Không có bất động sản để phân tích"}
        
        # Detailed analyses
        price_analysis = self.analyze_vietnam_price_trends(properties)
        inventory_analysis = self.analyze_vietnam_market_inventory(properties)
        best_value_properties = self.find_vietnam_best_value_properties(properties)
        
        # Source distribution
        source_distribution = {}
        for prop in properties:
            source_distribution[prop.source] = source_distribution.get(prop.source, 0) + 1
        
        # Market insights specific to Vietnam
        market_insights = self._generate_vietnam_market_insights(properties)
        
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
            "market_insights": market_insights,
            "sample_properties": [
                {
                    "address": prop.address,
                    "price": prop.price,
                    "area": prop.area,
                    "bedrooms": prop.bedrooms,
                    "bathrooms": prop.bathrooms,
                    "property_type": prop.property_type,
                    "legal_status": prop.legal_status,
                    "district": prop.district
                }
                for prop in properties[:5]
            ],
            "detailed_properties": [prop.dict() for prop in properties]
        }
    
    def _generate_vietnam_market_insights(self, properties: List[VietnamPropertyListing]) -> List[str]:
        """Generate market insights specific to Vietnamese real estate"""
        insights = []
        
        if not properties:
            return insights
        
        # Legal status insights
        legal_properties = [p for p in properties if p.legal_status and ('sổ đỏ' in p.legal_status.lower() or 'sổ hồng' in p.legal_status.lower())]
        legal_percentage = (len(legal_properties) / len(properties)) * 100
        insights.append(f"Tỷ lệ bất động sản có sổ đỏ/sổ hồng: {legal_percentage:.1f}%")
        
        # Direction insights (feng shui)
        good_directions = [p for p in properties if p.direction and any(d in p.direction.lower() for d in ['đông', 'nam', 'đông nam'])]
        if good_directions:
            direction_percentage = (len(good_directions) / len(properties)) * 100
            insights.append(f"Tỷ lệ bất động sản hướng tốt (Đông/Nam/Đông Nam): {direction_percentage:.1f}%")
        
        # Price insights
        properties_with_price = [p for p in properties if p.price]
        if properties_with_price:
            avg_price = sum(p.price for p in properties_with_price) / len(properties_with_price)
            if avg_price >= 1000000000:
                insights.append(f"Giá trung bình thị trường: {avg_price/1000000000:.1f} tỷ VND")
            else:
                insights.append(f"Giá trung bình thị trường: {avg_price/1000000:.0f} triệu VND")
        
        # Area insights
        areas = [p.area for p in properties if p.area and p.area > 0]
        if areas:
            avg_area = sum(areas) / len(areas)
            insights.append(f"Diện tích trung bình: {avg_area:.0f} m²")
        
        # Property type insights
        property_types = {}
        for prop in properties:
            if prop.property_type:
                property_types[prop.property_type] = property_types.get(prop.property_type, 0) + 1
        
        if property_types:
            most_common_type = max(property_types.items(), key=lambda x: x[1])
            insights.append(f"Loại hình phổ biến nhất: {most_common_type[0]} ({most_common_type[1]} tin đăng)")
        
        return insights
    
    def save_report(self, report: Dict, filename: str = None):
        """Save Vietnamese real estate market report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            location = report['search_criteria'].get('location', 'vietnam').replace(' ', '_').lower()
            filename = f"vietnam_real_estate_market_{location}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Báo cáo thị trường bất động sản đã được lưu vào {filename}")


def main():
    # Vietnamese real estate websites to search
    vietnam_real_estate_sites = [
        {
            'name': 'Batdongsan.com.vn',
            'url': 'https://batdongsan.com.vn'
        },
        {
            'name': 'Nhadat24h.net',
            'url': 'https://www.nhadat24h.net'
        },
        {
            'name': 'Alonhadat.com.vn',
            'url': 'https://alonhadat.com.vn'
        }
    ]
    
    # Search criteria for Vietnamese market
    search_criteria = {
        'location': 'Quận 1, TP. Hồ Chí Minh',
        'min_price': '3 tỷ',
        'max_price': '8 tỷ',
        'property_type': 'nhà riêng'
    }
    
    analyzer = VietnamRealEstateAnalyzer()
    
    print(f"🏠 Phân tích thị trường bất động sản tại {search_criteria['location']}...")
    
    # Analyze Vietnamese market
    properties = analyzer.analyze_vietnam_market(search_criteria, vietnam_real_estate_sites)
    
    if properties:
        print(f"\n📊 Đã phân tích thành công {len(properties)} bất động sản")
        
        # Generate comprehensive report
        report = analyzer.generate_vietnam_market_report(search_criteria, properties)
        
        # Display key insights
        print(f"\n📈 Tóm tắt thị trường:")
        print(f"  • Tổng số bất động sản: {report['summary']['total_properties_analyzed']}")
        print(f"  • Có thông tin giá: {report['summary']['properties_with_prices']}")
        
        if 'overall_price_stats' in report['price_analysis']:
            price_stats = report['price_analysis']['overall_price_stats']
            avg_price_display = f"{price_stats['average']/1000000000:.1f} tỷ VND" if price_stats['average'] >= 1000000000 else f"{price_stats['average']/1000000:.0f} triệu VND"
            min_price_display = f"{price_stats['min']/1000000000:.1f} tỷ VND" if price_stats['min'] >= 1000000000 else f"{price_stats['min']/1000000:.0f} triệu VND"
            max_price_display = f"{price_stats['max']/1000000000:.1f} tỷ VND" if price_stats['max'] >= 1000000000 else f"{price_stats['max']/1000000:.0f} triệu VND"
            
            print(f"\n💰 Phân tích giá:")
            print(f"  • Giá trung bình: {avg_price_display}")
            print(f"  • Khoảng giá: {min_price_display} - {max_price_display}")
        
        if 'price_per_m2_stats' in report['price_analysis'] and report['price_analysis']['price_per_m2_stats']:
            psf_stats = report['price_analysis']['price_per_m2_stats']
            print(f"  • Giá trung bình/m²: {psf_stats['average']/1000000:.1f} triệu VND/m²")
        
        if 'top_districts' in report['inventory_analysis']:
            print(f"\n🏘️ Quận/huyện có nhiều tin đăng:")
            for district in report['inventory_analysis']['top_districts'][:5]:
                print(f"  • {district['district']}: {district['count']} bất động sản")
        
        print(f"\n💎 Bất động sản đáng mua nhất:")
        for prop in report['best_value_properties'][:3]:
            price_display = f"{prop['price']/1000000000:.1f} tỷ VND" if prop['price'] >= 1000000000 else f"{prop['price']/1000000:.0f} triệu VND"
            print(f"  • {prop['address']}: {price_display} ({prop['price_per_m2']/1000000:.1f} triệu/m²)")
        
        if 'market_insights' in report:
            print(f"\n💡 Thông tin thị trường:")
            for insight in report['market_insights']:
                print(f"  • {insight}")
        
        # Save detailed report
        analyzer.save_report(report)
        
    else:
        print("❌ Không tìm thấy bất động sản để phân tích")


if __name__ == "__main__":
    main()
