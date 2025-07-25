#!/usr/bin/env python3
"""
Nova Act Demo: Enhanced Search and Filter Operations
===================================================

This demo shows advanced search and filtering capabilities with Nova Act,
including multi-criteria filtering, sorting, and result refinement.
"""

import os
import sys
import time
from typing import Dict, Any, List
from nova_act import NovaAct, BOOL_SCHEMA
from pydantic import BaseModel

# Import our enhanced framework
from demo_framework import BaseDemo, DemoResult
from demo_framework.multi_selector import SelectorBuilder


class SearchResult(BaseModel):
    """Search result model."""
    title: str
    price: str = "N/A"
    rating: str = "N/A"
    availability: str = "Unknown"


class SearchFilterDemo(BaseDemo):
    """Enhanced search and filter demo with multi-criteria filtering."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 6  # Setup, Site selection, Search, Filter, Sort, Results extraction
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up Search and Filter Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            return False
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites for search and filter operations."""
        return [
            "https://example.com",
            "https://httpbin.org/html"
        ]
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Step 1: Choose search site
            site_info = self._step_choose_search_site()
            extracted_data.update(site_info)
            self.increment_step("Search site selection completed")
            
            # Step 2: Perform initial search
            search_result = self._step_perform_search(site_info["target_site"])
            extracted_data.update(search_result)
            self.increment_step("Initial search completed")
            
            # Step 3: Apply filters
            filter_result = self._step_apply_filters(site_info["target_site"])
            extracted_data.update(filter_result)
            self.increment_step("Filters applied")
            
            # Step 4: Sort results
            sort_result = self._step_sort_results(site_info["target_site"])
            extracted_data.update(sort_result)
            self.increment_step("Results sorted")
            
            # Step 5: Refine search
            refinement_result = self._step_refine_search(site_info["target_site"])
            extracted_data.update(refinement_result)
            self.increment_step("Search refinement completed")
            
            # Step 6: Extract final results
            extraction_result = self._step_extract_results(site_info["target_site"])
            extracted_data.update(extraction_result)
            self.increment_step("Results extraction completed")
            
        except Exception as e:
            self.logger.error(f"Error during search and filter operations: {str(e)}")
            raise
        
        return extracted_data
    
    def _step_choose_search_site(self) -> Dict[str, Any]:
        """Step 1: Choose appropriate site for search and filter demo."""
        self.logger.log_step(1, "Search Site Selection", "starting")
        
        # Get region-appropriate e-commerce sites
        ecommerce_sites = self.config_manager.get_optimal_sites("ecommerce")
        
        # Choose first accessible site
        target_site = None
        for site_url in ecommerce_sites:
            if self.config_manager.validate_site_access(site_url):
                target_site = {
                    "url": site_url,
                    "name": site_url.replace("https://", "").replace("www.", ""),
                    "type": "ecommerce",
                    "supports_filters": True,
                    "supports_sorting": True
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
                "supports_sorting": False
            }
            self.add_warning("Using fallback site - limited search functionality")
        
        self.logger.log_step(1, "Search Site Selection", "completed", f"Selected {target_site['name']}")
        self.logger.log_data_extraction("target_site", target_site, "site_selection")
        
        return {"target_site": target_site}
    
    def _step_perform_search(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Perform initial search."""
        self.logger.log_step(2, "Initial Search", "starting")
        
        search_term = "laptop"
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/search_initial"
            ) as nova:
                
                # Perform search
                nova.act(f"search for {search_term}")
                
                # Wait for results to load
                time.sleep(3)
                
                # Check if search was successful
                result = nova.act("Are there search results visible on the page?", schema=BOOL_SCHEMA)
                search_successful = result.matches_schema and result.parsed_response
                
                # Get approximate result count
                result_count = 0
                if search_successful:
                    try:
                        # Try to get result count (simplified approach)
                        nova.act("look at the search results")
                        result_count = "multiple"  # Simplified for demo
                    except:
                        result_count = "unknown"
                
                search_data = {
                    "search_term": search_term,
                    "search_successful": search_successful,
                    "result_count": result_count,
                    "site_type": site_info.get("type", "unknown")
                }
                
                self.logger.log_step(2, "Initial Search", "completed", 
                                   f"Search for '{search_term}' successful: {search_successful}")
                self.logger.log_data_extraction("search_data", search_data, "initial_search")
                
                return {"search_result": search_data}
                
        except Exception as e:
            self.logger.log_step(2, "Initial Search", "failed", str(e))
            return {
                "search_result": {
                    "search_term": search_term,
                    "search_successful": False,
                    "error": str(e)
                }
            }
    
    def _step_apply_filters(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Apply various filters to search results."""
        self.logger.log_step(3, "Apply Filters", "starting")
        
        if not site_info.get("supports_filters", False):
            self.logger.log_step(3, "Apply Filters", "skipped", "Site doesn't support filters")
            return {"filter_result": {"skipped": True, "reason": "not_supported"}}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/search_filters"
            ) as nova:
                
                # Re-perform search to ensure we're on results page
                nova.act("search for laptop")
                time.sleep(2)
                
                applied_filters = []
                
                # Try to apply price filter
                try:
                    nova.act("look for price filters or price range options")
                    nova.act("if there are price filters, select a reasonable price range")
                    applied_filters.append({
                        "type": "price",
                        "applied": True,
                        "method": "price_range"
                    })
                    time.sleep(1)
                except Exception as e:
                    applied_filters.append({
                        "type": "price",
                        "applied": False,
                        "error": str(e)
                    })
                
                # Try to apply brand filter
                try:
                    nova.act("look for brand filters and select a popular brand if available")
                    applied_filters.append({
                        "type": "brand",
                        "applied": True,
                        "method": "brand_selection"
                    })
                    time.sleep(1)
                except Exception as e:
                    applied_filters.append({
                        "type": "brand",
                        "applied": False,
                        "error": str(e)
                    })
                
                # Try to apply rating filter
                try:
                    nova.act("look for customer rating filters and select 4 stars and up if available")
                    applied_filters.append({
                        "type": "rating",
                        "applied": True,
                        "method": "rating_filter"
                    })
                    time.sleep(1)
                except Exception as e:
                    applied_filters.append({
                        "type": "rating",
                        "applied": False,
                        "error": str(e)
                    })
                
                # Try to apply availability filter
                try:
                    nova.act("look for availability filters and select 'in stock' if available")
                    applied_filters.append({
                        "type": "availability",
                        "applied": True,
                        "method": "stock_filter"
                    })
                    time.sleep(1)
                except Exception as e:
                    applied_filters.append({
                        "type": "availability",
                        "applied": False,
                        "error": str(e)
                    })
                
                successful_filters = len([f for f in applied_filters if f.get("applied", False)])
                
                filter_data = {
                    "filters_applied": applied_filters,
                    "successful_count": successful_filters,
                    "total_attempted": len(applied_filters)
                }
                
                self.logger.log_step(3, "Apply Filters", "completed", 
                                   f"{successful_filters}/{len(applied_filters)} filters applied")
                self.logger.log_data_extraction("filter_data", filter_data, "filter_application")
                
                return {"filter_result": filter_data}
                
        except Exception as e:
            self.logger.log_step(3, "Apply Filters", "failed", str(e))
            return {"filter_result": {"failed": True, "error": str(e)}}
    
    def _step_sort_results(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Sort search results."""
        self.logger.log_step(4, "Sort Results", "starting")
        
        if not site_info.get("supports_sorting", False):
            self.logger.log_step(4, "Sort Results", "skipped", "Site doesn't support sorting")
            return {"sort_result": {"skipped": True, "reason": "not_supported"}}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/search_sorting"
            ) as nova:
                
                # Re-perform search to ensure we're on results page
                nova.act("search for laptop")
                time.sleep(2)
                
                sort_attempts = []
                
                # Try different sorting options
                sort_options = [
                    {"name": "price_low_high", "instruction": "sort by price from low to high"},
                    {"name": "price_high_low", "instruction": "sort by price from high to low"},
                    {"name": "customer_rating", "instruction": "sort by customer rating or reviews"},
                    {"name": "newest", "instruction": "sort by newest or most recent"},
                    {"name": "popularity", "instruction": "sort by popularity or best sellers"}
                ]
                
                for sort_option in sort_options[:2]:  # Try first 2 options
                    try:
                        nova.act(f"look for sorting options and {sort_option['instruction']}")
                        time.sleep(2)
                        
                        # Check if sorting was applied
                        result = nova.act("Did the page refresh or change after sorting?", schema=BOOL_SCHEMA)
                        sort_applied = result.matches_schema and result.parsed_response
                        
                        sort_attempts.append({
                            "sort_type": sort_option["name"],
                            "applied": sort_applied,
                            "method": "natural_language"
                        })
                        
                        if sort_applied:
                            break  # Stop after first successful sort
                            
                    except Exception as e:
                        sort_attempts.append({
                            "sort_type": sort_option["name"],
                            "applied": False,
                            "error": str(e)
                        })
                
                successful_sorts = len([s for s in sort_attempts if s.get("applied", False)])
                
                sort_data = {
                    "sort_attempts": sort_attempts,
                    "successful_count": successful_sorts,
                    "total_attempted": len(sort_attempts)
                }
                
                self.logger.log_step(4, "Sort Results", "completed", 
                                   f"{successful_sorts} sorting operations successful")
                self.logger.log_data_extraction("sort_data", sort_data, "result_sorting")
                
                return {"sort_result": sort_data}
                
        except Exception as e:
            self.logger.log_step(4, "Sort Results", "failed", str(e))
            return {"sort_result": {"failed": True, "error": str(e)}}
    
    def _step_refine_search(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Refine search with additional criteria."""
        self.logger.log_step(5, "Search Refinement", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/search_refinement"
            ) as nova:
                
                # Re-perform search
                nova.act("search for laptop")
                time.sleep(2)
                
                refinement_attempts = []
                
                # Try to refine search with more specific terms
                try:
                    nova.act("refine the search by adding more specific terms like 'gaming laptop' or 'business laptop'")
                    time.sleep(2)
                    
                    result = nova.act("Are the search results more specific now?", schema=BOOL_SCHEMA)
                    refinement_successful = result.matches_schema and result.parsed_response
                    
                    refinement_attempts.append({
                        "type": "term_refinement",
                        "successful": refinement_successful,
                        "method": "specific_terms"
                    })
                    
                except Exception as e:
                    refinement_attempts.append({
                        "type": "term_refinement",
                        "successful": False,
                        "error": str(e)
                    })
                
                # Try to use search suggestions
                try:
                    nova.act("look for search suggestions or related searches and try one")
                    time.sleep(2)
                    
                    refinement_attempts.append({
                        "type": "suggestions",
                        "successful": True,
                        "method": "search_suggestions"
                    })
                    
                except Exception as e:
                    refinement_attempts.append({
                        "type": "suggestions",
                        "successful": False,
                        "error": str(e)
                    })
                
                successful_refinements = len([r for r in refinement_attempts if r.get("successful", False)])
                
                refinement_data = {
                    "refinement_attempts": refinement_attempts,
                    "successful_count": successful_refinements,
                    "total_attempted": len(refinement_attempts)
                }
                
                self.logger.log_step(5, "Search Refinement", "completed", 
                                   f"{successful_refinements} refinements successful")
                self.logger.log_data_extraction("refinement_data", refinement_data, "search_refinement")
                
                return {"refinement_result": refinement_data}
                
        except Exception as e:
            self.logger.log_step(5, "Search Refinement", "failed", str(e))
            return {"refinement_result": {"failed": True, "error": str(e)}}
    
    def _step_extract_results(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: Extract final search results."""
        self.logger.log_step(6, "Results Extraction", "starting")
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/search_extraction"
            ) as nova:
                
                # Re-perform search to ensure we have results
                nova.act("search for laptop")
                time.sleep(3)
                
                # Extract result information
                extraction_data = {
                    "extraction_method": "simplified_demo",
                    "results": []
                }
                
                try:
                    # Get basic information about search results
                    result = nova.act("How many search results are visible on this page?")
                    if result.response:
                        extraction_data["result_count_description"] = result.response
                    
                    # Try to get information about first few results
                    for i in range(1, 4):  # Try to get info about first 3 results
                        try:
                            result = nova.act(f"What is the title and price of the {i}{'st' if i==1 else 'nd' if i==2 else 'rd'} search result?")
                            if result.response:
                                extraction_data["results"].append({
                                    "position": i,
                                    "description": result.response,
                                    "extraction_method": "natural_language"
                                })
                        except:
                            continue
                    
                    # Check if results seem relevant
                    result = nova.act("Do the search results appear to be relevant to laptops?", schema=BOOL_SCHEMA)
                    extraction_data["results_relevant"] = result.matches_schema and result.parsed_response
                    
                except Exception as e:
                    extraction_data["extraction_error"] = str(e)
                
                extracted_count = len(extraction_data.get("results", []))
                
                self.logger.log_step(6, "Results Extraction", "completed", 
                                   f"Extracted information about {extracted_count} results")
                self.logger.log_data_extraction("extraction_data", extraction_data, "result_extraction")
                
                return {"extraction_result": extraction_data}
                
        except Exception as e:
            self.logger.log_step(6, "Results Extraction", "failed", str(e))
            return {"extraction_result": {"failed": True, "error": str(e)}}


def run_search_filter_demo():
    """Run the search and filter demo."""
    print("🔍 Starting Enhanced Search and Filter Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = SearchFilterDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted:
            print("\n📋 Search and Filter Summary:")
            
            # Search results
            if "search_result" in result.data_extracted:
                search = result.data_extracted["search_result"]
                term = search.get("search_term", "unknown")
                successful = search.get("search_successful", False)
                print(f"   🔍 Search term: '{term}' - {'✅ Success' if successful else '❌ Failed'}")
            
            # Filter results
            if "filter_result" in result.data_extracted:
                filters = result.data_extracted["filter_result"]
                if not filters.get("skipped"):
                    successful = filters.get("successful_count", 0)
                    total = filters.get("total_attempted", 0)
                    print(f"   🎛️  Filters applied: {successful}/{total}")
            
            # Sort results
            if "sort_result" in result.data_extracted:
                sorts = result.data_extracted["sort_result"]
                if not sorts.get("skipped"):
                    successful = sorts.get("successful_count", 0)
                    print(f"   📊 Sorting operations: {successful} successful")
            
            # Refinement results
            if "refinement_result" in result.data_extracted:
                refinement = result.data_extracted["refinement_result"]
                if not refinement.get("failed"):
                    successful = refinement.get("successful_count", 0)
                    print(f"   🎯 Search refinements: {successful} successful")
            
            # Extraction results
            if "extraction_result" in result.data_extracted:
                extraction = result.data_extracted["extraction_result"]
                if not extraction.get("failed"):
                    extracted = len(extraction.get("results", []))
                    relevant = extraction.get("results_relevant", False)
                    print(f"   📄 Results extracted: {extracted}")
                    print(f"   ✅ Results relevant: {relevant}")
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
    print("Nova Act Enhanced Search and Filter Demo")
    print("=" * 50)
    
    # Run the demo
    result = run_search_filter_demo()
    
    if result.success:
        print("\n🎉 Search and filter demo completed successfully!")
        print("This demo showcased:")
        print("  • Multi-criteria search and filtering")
        print("  • Dynamic sorting of search results")
        print("  • Search refinement techniques")
        print("  • Result extraction and validation")
        print("  • Geographic-aware site selection")
    else:
        print("\n⚠️ Demo encountered some issues, but this demonstrates:")
        print("  • Robust error handling in search operations")
        print("  • Graceful degradation when filters aren't available")
        print("  • Adaptive search strategies across different sites")
    
    print("\n💡 Production Tips:")
    print("  • Implement search result caching for performance")
    print("  • Use structured data extraction with schemas")
    print("  • Handle pagination for comprehensive results")
    print("  • Implement search analytics and optimization")
    print("  • Consider A/B testing different search strategies")


if __name__ == "__main__":
    main()