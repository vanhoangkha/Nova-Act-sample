#!/usr/bin/env python3
"""
Nova Act Demo: Enhanced Real Estate Search
==========================================

This demo shows how to search for real estate properties with location-aware
filtering, transportation analysis, and comprehensive property data extraction.
"""

import os
import sys
import time
from typing import Dict, Any, List
from nova_act import NovaAct, BOOL_SCHEMA
from pydantic import BaseModel

# Import our enhanced framework
from demo_framework import BaseDemo, DemoResult


class PropertyInfo(BaseModel):
    """Property information model."""
    address: str
    price: str
    bedrooms: str = "N/A"
    bathrooms: str = "N/A"
    square_feet: str = "N/A"
    property_type: str = "N/A"


class RealEstateDemo(BaseDemo):
    """Enhanced real estate demo with location awareness and transportation analysis."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 6  # Setup, Site selection, Location search, Property filtering, Transportation analysis, Data extraction
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up Real Estate Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            return False
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites for real estate operations."""
        return [
            "https://example.com",
            "https://httpbin.org/html"
        ]
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Step 1: Choose real estate site
            site_info = self._step_choose_real_estate_site()
            extracted_data.update(site_info)
            self.increment_step("Real estate site selection completed")
            
            # Step 2: Set search location
            location_result = self._step_set_search_location(site_info["target_site"])
            extracted_data.update(location_result)
            self.increment_step("Search location set")
            
            # Step 3: Apply property filters
            filter_result = self._step_apply_property_filters(site_info["target_site"])
            extracted_data.update(filter_result)
            self.increment_step("Property filters applied")
            
            # Step 4: Analyze properties
            analysis_result = self._step_analyze_properties(site_info["target_site"])
            extracted_data.update(analysis_result)
            self.increment_step("Property analysis completed")
            
            # Step 5: Check transportation
            transport_result = self._step_check_transportation(site_info["target_site"])
            extracted_data.update(transport_result)
            self.increment_step("Transportation analysis completed")
            
            # Step 6: Extract property data
            extraction_result = self._step_extract_property_data(site_info["target_site"])
            extracted_data.update(extraction_result)
            self.increment_step("Property data extraction completed")
            
        except Exception as e:
            self.logger.error(f"Error during real estate operations: {str(e)}")
            raise
        
        return extracted_data
    
    def _step_choose_real_estate_site(self) -> Dict[str, Any]:
        """Step 1: Choose appropriate real estate site based on user's region."""
        self.logger.log_step(1, "Real Estate Site Selection", "starting")
        
        # Get region-appropriate real estate sites
        real_estate_sites = self.config_manager.get_optimal_sites("real_estate")
        
        # Choose first accessible site
        target_site = None
        for site_url in real_estate_sites:
            if self.config_manager.validate_site_access(site_url):
                target_site = {
                    "url": site_url,
                    "name": site_url.replace("https://", "").replace("www.", ""),
                    "type": "real_estate",
                    "supports_filters": True,
                    "supports_maps": True
                }
                break
        
        if not target_site:
            # Use fallback
            fallback_sites = self.get_fallback_sites()
            target_site = {
                "url": fallback_sites[0],
                "name": "Fallback Site",
                "type": "fallback",
                "supports_filters": False,
                "supports_maps": False
            }
            self.add_warning("Using fallback site - limited real estate functionality")
        
        # Determine search location based on site and user region
        env_info = self.config_manager.detect_environment()
        search_locations = self._get_search_locations(target_site["name"], env_info.region)
        target_site["search_locations"] = search_locations
        
        self.logger.log_step(1, "Real Estate Site Selection", "completed", f"Selected {target_site['name']}")
        self.logger.log_data_extraction("target_site", target_site, "site_selection")
        
        return {"target_site": target_site}
    
    def _get_search_locations(self, site_name: str, region: str) -> List[str]:
        """Get appropriate search locations based on site and region."""
        location_mappings = {
            "north_america": {
                "zillow.com": ["San Francisco, CA", "New York, NY", "Austin, TX"],
                "realtor.com": ["Los Angeles, CA", "Chicago, IL", "Miami, FL"],
                "redfin.com": ["Seattle, WA", "Denver, CO", "Portland, OR"]
            },
            "europe": {
                "rightmove.co.uk": ["London", "Manchester", "Birmingham"],
                "immobilienscout24.de": ["Berlin", "Munich", "Hamburg"],
                "seloger.com": ["Paris", "Lyon", "Marseille"]
            },
            "asia_pacific": {
                "realestate.com.au": ["Sydney", "Melbourne", "Brisbane"],
                "suumo.jp": ["Tokyo", "Osaka", "Kyoto"]
            },
            "other": ["City Center", "Downtown", "Residential Area"]
        }
        
        region_locations = location_mappings.get(region, location_mappings["other"])
        if isinstance(region_locations, dict):
            return region_locations.get(site_name, ["City Center", "Downtown"])
        else:
            return region_locations
    
    def _step_set_search_location(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Set search location for property search."""
        self.logger.log_step(2, "Search Location Setup", "starting")
        
        search_locations = site_info.get("search_locations", ["City Center"])
        selected_location = search_locations[0]  # Use first location
        
        if site_info.get("type") == "fallback":
            self.logger.log_step(2, "Search Location Setup", "skipped", "Fallback site doesn't support location search")
            return {"location_result": {"skipped": True, "reason": "fallback_site"}}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/real_estate_location"
            ) as nova:
                
                # Set search location
                nova.act(f"search for properties in {selected_location}")
                time.sleep(3)
                
                # Verify location was set
                result = nova.act("Are property listings visible for the searched location?", schema=BOOL_SCHEMA)
                location_set = result.matches_schema and result.parsed_response
                
                location_data = {
                    "selected_location": selected_location,
                    "available_locations": search_locations,
                    "location_set_successfully": location_set,
                    "site_type": site_info.get("type", "unknown")
                }
                
                self.logger.log_step(2, "Search Location Setup", "completed", 
                                   f"Location '{selected_location}' set: {location_set}")
                self.logger.log_data_extraction("location_data", location_data, "location_setup")
                
                return {"location_result": location_data}
                
        except Exception as e:
            self.logger.log_step(2, "Search Location Setup", "failed", str(e))
            return {
                "location_result": {
                    "selected_location": selected_location,
                    "location_set_successfully": False,
                    "error": str(e)
                }
            }
    
    def _step_apply_property_filters(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Apply property filters."""
        self.logger.log_step(3, "Property Filters", "starting")
        
        if not site_info.get("supports_filters", False):
            self.logger.log_step(3, "Property Filters", "skipped", "Site doesn't support filters")
            return {"filter_result": {"skipped": True, "reason": "not_supported"}}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/real_estate_filters"
            ) as nova:
                
                # Re-search to ensure we're on results page
                search_locations = site_info.get("search_locations", ["City Center"])
                nova.act(f"search for properties in {search_locations[0]}")
                time.sleep(2)
                
                applied_filters = []
                
                # Apply price filter
                try:
                    nova.act("look for price filters and set a reasonable price range")
                    applied_filters.append({
                        "type": "price_range",
                        "applied": True,
                        "method": "price_filter"
                    })
                    time.sleep(1)
                except Exception as e:
                    applied_filters.append({
                        "type": "price_range",
                        "applied": False,
                        "error": str(e)
                    })
                
                # Apply bedroom filter
                try:
                    nova.act("look for bedroom filters and select 2+ bedrooms")
                    applied_filters.append({
                        "type": "bedrooms",
                        "applied": True,
                        "method": "bedroom_filter"
                    })
                    time.sleep(1)
                except Exception as e:
                    applied_filters.append({
                        "type": "bedrooms",
                        "applied": False,
                        "error": str(e)
                    })
                
                # Apply property type filter
                try:
                    nova.act("look for property type filters and select houses or apartments")
                    applied_filters.append({
                        "type": "property_type",
                        "applied": True,
                        "method": "type_filter"
                    })
                    time.sleep(1)
                except Exception as e:
                    applied_filters.append({
                        "type": "property_type",
                        "applied": False,
                        "error": str(e)
                    })
                
                successful_filters = len([f for f in applied_filters if f.get("applied", False)])
                
                filter_data = {
                    "filters_applied": applied_filters,
                    "successful_count": successful_filters,
                    "total_attempted": len(applied_filters)
                }
                
                self.logger.log_step(3, "Property Filters", "completed", 
                                   f"{successful_filters}/{len(applied_filters)} filters applied")
                self.logger.log_data_extraction("filter_data", filter_data, "property_filtering")
                
                return {"filter_result": filter_data}
                
        except Exception as e:
            self.logger.log_step(3, "Property Filters", "failed", str(e))
            return {"filter_result": {"failed": True, "error": str(e)}}
    
    def _step_analyze_properties(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Analyze available properties."""
        self.logger.log_step(4, "Property Analysis", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/real_estate_analysis"
            ) as nova:
                
                # Re-search to ensure we have results
                search_locations = site_info.get("search_locations", ["City Center"])
                nova.act(f"search for properties in {search_locations[0]}")
                time.sleep(3)
                
                analysis_data = {
                    "analysis_method": "simplified_demo",
                    "properties_analyzed": []
                }
                
                # Get general information about available properties
                try:
                    result = nova.act("How many property listings are visible on this page?")
                    if result.response:
                        analysis_data["property_count_description"] = result.response
                    
                    # Analyze first few properties
                    for i in range(1, 4):  # Analyze first 3 properties
                        try:
                            ordinal = "first" if i == 1 else "second" if i == 2 else "third"
                            result = nova.act(f"What are the key details of the {ordinal} property listing (price, bedrooms, location)?")
                            if result.response:
                                analysis_data["properties_analyzed"].append({
                                    "position": i,
                                    "description": result.response,
                                    "analysis_method": "natural_language"
                                })
                        except:
                            continue
                    
                    # Check property availability
                    result = nova.act("Do the properties appear to be currently available for sale or rent?", schema=BOOL_SCHEMA)
                    analysis_data["properties_available"] = result.matches_schema and result.parsed_response
                    
                    # Check for property images
                    result = nova.act("Do the property listings have photos or images?", schema=BOOL_SCHEMA)
                    analysis_data["has_property_images"] = result.matches_schema and result.parsed_response
                    
                except Exception as e:
                    analysis_data["analysis_error"] = str(e)
                
                analyzed_count = len(analysis_data.get("properties_analyzed", []))
                
                self.logger.log_step(4, "Property Analysis", "completed", 
                                   f"Analyzed {analyzed_count} properties")
                self.logger.log_data_extraction("analysis_data", analysis_data, "property_analysis")
                
                return {"analysis_result": analysis_data}
                
        except Exception as e:
            self.logger.log_step(4, "Property Analysis", "failed", str(e))
            return {"analysis_result": {"failed": True, "error": str(e)}}
    
    def _step_check_transportation(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Check transportation options for properties."""
        self.logger.log_step(5, "Transportation Analysis", "starting")
        
        if not site_info.get("supports_maps", False):
            self.logger.log_step(5, "Transportation Analysis", "skipped", "Site doesn't support maps/transportation")
            return {"transport_result": {"skipped": True, "reason": "not_supported"}}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/real_estate_transport"
            ) as nova:
                
                # Re-search to ensure we have results
                search_locations = site_info.get("search_locations", ["City Center"])
                nova.act(f"search for properties in {search_locations[0]}")
                time.sleep(2)
                
                transport_analysis = []
                
                # Check for transportation information
                try:
                    nova.act("look for transportation information, nearby transit, or commute details")
                    
                    # Check for public transit info
                    result = nova.act("Is there information about public transportation or transit nearby?", schema=BOOL_SCHEMA)
                    has_transit_info = result.matches_schema and result.parsed_response
                    
                    transport_analysis.append({
                        "type": "public_transit",
                        "information_available": has_transit_info,
                        "method": "transit_check"
                    })
                    
                    # Check for walkability information
                    result = nova.act("Is there information about walkability or walk scores?", schema=BOOL_SCHEMA)
                    has_walk_info = result.matches_schema and result.parsed_response
                    
                    transport_analysis.append({
                        "type": "walkability",
                        "information_available": has_walk_info,
                        "method": "walkability_check"
                    })
                    
                    # Check for nearby amenities
                    result = nova.act("Is there information about nearby schools, shopping, or amenities?", schema=BOOL_SCHEMA)
                    has_amenity_info = result.matches_schema and result.parsed_response
                    
                    transport_analysis.append({
                        "type": "amenities",
                        "information_available": has_amenity_info,
                        "method": "amenity_check"
                    })
                    
                except Exception as e:
                    transport_analysis.append({
                        "type": "general_transport",
                        "information_available": False,
                        "error": str(e)
                    })
                
                available_info_count = len([t for t in transport_analysis if t.get("information_available", False)])
                
                transport_data = {
                    "transport_analysis": transport_analysis,
                    "available_info_count": available_info_count,
                    "total_checks": len(transport_analysis)
                }
                
                self.logger.log_step(5, "Transportation Analysis", "completed", 
                                   f"{available_info_count}/{len(transport_analysis)} transport info types found")
                self.logger.log_data_extraction("transport_data", transport_data, "transportation_analysis")
                
                return {"transport_result": transport_data}
                
        except Exception as e:
            self.logger.log_step(5, "Transportation Analysis", "failed", str(e))
            return {"transport_result": {"failed": True, "error": str(e)}}
    
    def _step_extract_property_data(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: Extract detailed property data."""
        self.logger.log_step(6, "Property Data Extraction", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/real_estate_extraction"
            ) as nova:
                
                # Re-search to ensure we have results
                search_locations = site_info.get("search_locations", ["City Center"])
                nova.act(f"search for properties in {search_locations[0]}")
                time.sleep(3)
                
                # Click on first property for detailed extraction
                try:
                    nova.act("click on the first property listing to see more details")
                    time.sleep(3)
                    
                    # Extract detailed property information
                    property_details = {}
                    
                    # Get property address
                    try:
                        result = nova.act("What is the address of this property?")
                        property_details["address"] = result.response if result.response else "Address not found"
                    except:
                        property_details["address"] = "Address extraction failed"
                    
                    # Get property price
                    try:
                        result = nova.act("What is the price of this property?")
                        property_details["price"] = result.response if result.response else "Price not found"
                    except:
                        property_details["price"] = "Price extraction failed"
                    
                    # Get property specifications
                    try:
                        result = nova.act("How many bedrooms and bathrooms does this property have?")
                        property_details["bed_bath"] = result.response if result.response else "Bed/bath info not found"
                    except:
                        property_details["bed_bath"] = "Bed/bath extraction failed"
                    
                    # Get property size
                    try:
                        result = nova.act("What is the square footage or size of this property?")
                        property_details["size"] = result.response if result.response else "Size not found"
                    except:
                        property_details["size"] = "Size extraction failed"
                    
                    extraction_data = {
                        "extraction_successful": True,
                        "property_details": property_details,
                        "extraction_method": "detailed_view"
                    }
                    
                except Exception as e:
                    # Fallback to list view extraction
                    extraction_data = {
                        "extraction_successful": False,
                        "fallback_attempted": True,
                        "error": str(e)
                    }
                    
                    try:
                        # Try to extract from list view
                        result = nova.act("Extract basic information about the first few properties from the list view")
                        extraction_data["list_view_data"] = result.response if result.response else "No data extracted"
                        extraction_data["extraction_method"] = "list_view_fallback"
                    except:
                        extraction_data["list_view_data"] = "List view extraction also failed"
                
                self.logger.log_step(6, "Property Data Extraction", "completed", 
                                   f"Extraction successful: {extraction_data.get('extraction_successful', False)}")
                self.logger.log_data_extraction("extraction_data", extraction_data, "property_data_extraction")
                
                return {"extraction_result": extraction_data}
                
        except Exception as e:
            self.logger.log_step(6, "Property Data Extraction", "failed", str(e))
            return {"extraction_result": {"failed": True, "error": str(e)}}


def run_real_estate_demo():
    """Run the real estate demo."""
    print("🏠 Starting Enhanced Real Estate Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = RealEstateDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted:
            print("\n📋 Real Estate Search Summary:")
            
            # Site and location info
            if "target_site" in result.data_extracted:
                site = result.data_extracted["target_site"]
                print(f"   🌐 Site used: {site.get('name', 'Unknown')}")
                locations = site.get("search_locations", [])
                if locations:
                    print(f"   📍 Available locations: {', '.join(locations[:3])}")
            
            # Location setup
            if "location_result" in result.data_extracted:
                location = result.data_extracted["location_result"]
                if not location.get("skipped"):
                    selected = location.get("selected_location", "Unknown")
                    success = location.get("location_set_successfully", False)
                    print(f"   🎯 Search location: {selected} ({'✅ Set' if success else '❌ Failed'})")
            
            # Filter results
            if "filter_result" in result.data_extracted:
                filters = result.data_extracted["filter_result"]
                if not filters.get("skipped"):
                    successful = filters.get("successful_count", 0)
                    total = filters.get("total_attempted", 0)
                    print(f"   🎛️  Property filters: {successful}/{total} applied")
            
            # Analysis results
            if "analysis_result" in result.data_extracted:
                analysis = result.data_extracted["analysis_result"]
                if not analysis.get("failed"):
                    analyzed = len(analysis.get("properties_analyzed", []))
                    available = analysis.get("properties_available", False)
                    print(f"   🔍 Properties analyzed: {analyzed}")
                    print(f"   ✅ Properties available: {available}")
            
            # Transportation info
            if "transport_result" in result.data_extracted:
                transport = result.data_extracted["transport_result"]
                if not transport.get("skipped"):
                    available = transport.get("available_info_count", 0)
                    total = transport.get("total_checks", 0)
                    print(f"   🚌 Transportation info: {available}/{total} types available")
            
            # Extraction results
            if "extraction_result" in result.data_extracted:
                extraction = result.data_extracted["extraction_result"]
                success = extraction.get("extraction_successful", False)
                method = extraction.get("extraction_method", "unknown")
                print(f"   📄 Data extraction: {'✅ Success' if success else '❌ Failed'} ({method})")
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
    print("Nova Act Enhanced Real Estate Demo")
    print("=" * 50)
    
    # Run the demo
    result = run_real_estate_demo()
    
    if result.success:
        print("\n🎉 Real estate demo completed successfully!")
        print("This demo showcased:")
        print("  • Geographic-aware real estate site selection")
        print("  • Location-based property searching")
        print("  • Multi-criteria property filtering")
        print("  • Transportation and amenity analysis")
        print("  • Detailed property data extraction")
    else:
        print("\n⚠️ Demo encountered some issues, but this demonstrates:")
        print("  • Robust error handling in real estate operations")
        print("  • Graceful degradation when sites have restrictions")
        print("  • Adaptive strategies for different regional sites")
    
    print("\n💡 Production Tips:")
    print("  • Implement property data validation and normalization")
    print("  • Use structured schemas for consistent data extraction")
    print("  • Consider market trend analysis and price predictions")
    print("  • Implement property alert systems for new listings")
    print("  • Add mortgage calculator and affordability analysis")


if __name__ == "__main__":
    main()