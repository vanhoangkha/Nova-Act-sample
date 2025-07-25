#!/usr/bin/env python3
"""
Nova Act Demo: Enhanced Parallel Processing
===========================================

This demo shows how to run multiple Nova Act sessions in parallel
with robust error handling and geographic awareness.
"""

import os
import sys
import time
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from nova_act import NovaAct, ActError
from pydantic import BaseModel

# Import our enhanced framework
from demo_framework import BaseDemo, DemoResult


class ProductInfo(BaseModel):
    """Product information model."""
    name: str
    price: str
    source: str
    rating: str = "N/A"


class ParallelProcessingDemo(BaseDemo):
    """Enhanced parallel processing demo with error handling and site validation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 4  # Setup, Site validation, Parallel execution, Results aggregation
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up Parallel Processing Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            return False
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites for parallel processing."""
        return ["https://example.com", "https://httpbin.org/html"]
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Step 1: Get optimal sites for user's region
            sites = self._step_get_sites()
            extracted_data.update(sites)
            self.increment_step("Site selection completed")
            
            # Step 2: Validate site accessibility
            validated_sites = self._step_validate_sites(sites["sites"])
            extracted_data.update(validated_sites)
            self.increment_step("Site validation completed")
            
            # Step 3: Run parallel searches
            search_results = self._step_parallel_search(validated_sites["accessible_sites"])
            extracted_data.update(search_results)
            self.increment_step("Parallel search completed")
            
            # Step 4: Aggregate results
            aggregated = self._step_aggregate_results(search_results.get("results", []))
            extracted_data.update(aggregated)
            self.increment_step("Results aggregation completed")
            
        except Exception as e:
            self.logger.error(f"Error during parallel processing: {str(e)}")
            raise
        
        return extracted_data
    
    def _step_get_sites(self) -> Dict[str, Any]:
        """Step 1: Get optimal sites for user's region."""
        self.logger.log_step(1, "Site Selection", "starting")
        
        # Get region-appropriate e-commerce sites
        ecommerce_sites = self.config_manager.get_optimal_sites("ecommerce")
        
        # Limit to 3 sites for parallel demo
        selected_sites = ecommerce_sites[:3]
        
        self.logger.log_step(1, "Site Selection", "completed", f"Selected {len(selected_sites)} sites")
        self.logger.log_data_extraction("selected_sites", {"sites": selected_sites}, "config_manager")
        
        return {"sites": selected_sites}
    
    def _step_validate_sites(self, sites: List[str]) -> Dict[str, Any]:
        """Step 2: Validate site accessibility."""
        self.logger.log_step(2, "Site Validation", "starting")
        
        accessible_sites = []
        validation_results = {}
        
        for site in sites:
            is_accessible = self.config_manager.validate_site_access(site)
            validation_results[site] = is_accessible
            
            if is_accessible:
                accessible_sites.append(site)
                self.logger.info(f"✅ {site} is accessible")
            else:
                self.logger.warning(f"❌ {site} is not accessible")
        
        if not accessible_sites:
            # Use fallback sites
            fallback_sites = self.get_fallback_sites()
            accessible_sites = fallback_sites[:2]  # Limit fallbacks
            self.add_warning("No primary sites accessible, using fallback sites")
        
        self.logger.log_step(2, "Site Validation", "completed", f"{len(accessible_sites)} sites accessible")
        
        return {
            "accessible_sites": accessible_sites,
            "validation_results": validation_results
        }
    
    def _step_parallel_search(self, sites: List[str]) -> Dict[str, Any]:
        """Step 3: Run parallel searches across multiple sites."""
        self.logger.log_step(3, "Parallel Search", "starting")
        
        search_term = "laptop"
        results = []
        
        # Use ThreadPoolExecutor for parallel execution
        max_workers = min(len(sites), 3)  # Limit concurrent sessions
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit search tasks
            future_to_site = {
                executor.submit(self._search_single_site, site, search_term): site 
                for site in sites
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_site.keys()):
                site = future_to_site[future]
                try:
                    result = future.result(timeout=60)  # 60 second timeout per site
                    if result:
                        results.append(result)
                        self.logger.info(f"✅ Search completed on {site}")
                    else:
                        self.logger.warning(f"⚠️ No results from {site}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Search failed on {site}: {str(e)}")
                    # Continue with other sites
                    continue
        
        self.logger.log_step(3, "Parallel Search", "completed", f"Got results from {len(results)} sites")
        self.logger.log_data_extraction("search_results", {"results": results}, "parallel_search")
        
        return {"results": results, "search_term": search_term}
    
    def _search_single_site(self, site: str, search_term: str) -> Dict[str, Any]:
        """Search for a product on a single site."""
        try:
            with NovaAct(
                starting_page=site,
                logs_directory=f"./demo/logs/parallel_{site.replace('https://', '').replace('.', '_')}",
                headless=True  # Use headless for parallel execution
            ) as nova:
                
                # Search for the product
                nova.act(f"search for {search_term}")
                
                # Try to get first result info
                try:
                    # Simple approach - just get visible text from first result
                    nova.act("click on the first search result or product")
                    
                    # Extract basic product info
                    result = {
                        "source": site,
                        "search_term": search_term,
                        "found_product": True,
                        "timestamp": time.time()
                    }
                    
                    # Try to get product name and price (simplified)
                    try:
                        # This is a simplified extraction - in real usage you'd use schemas
                        result["product_name"] = f"Product from {site}"
                        result["price"] = "Price not extracted"
                    except:
                        pass
                    
                    return result
                    
                except Exception as e:
                    self.logger.warning(f"Could not extract product details from {site}: {str(e)}")
                    return {
                        "source": site,
                        "search_term": search_term,
                        "found_product": False,
                        "error": str(e),
                        "timestamp": time.time()
                    }
                    
        except Exception as e:
            self.logger.error(f"Failed to search {site}: {str(e)}")
            return None
    
    def _step_aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 4: Aggregate and analyze results from all sites."""
        self.logger.log_step(4, "Results Aggregation", "starting")
        
        if not results:
            self.logger.log_step(4, "Results Aggregation", "completed", "No results to aggregate")
            return {"aggregated_results": {"total_sites": 0, "successful_searches": 0}}
        
        # Aggregate statistics
        total_sites = len(results)
        successful_searches = len([r for r in results if r and r.get("found_product", False)])
        failed_searches = total_sites - successful_searches
        
        # Group by source
        by_source = {}
        for result in results:
            if result:
                source = result.get("source", "unknown")
                by_source[source] = result
        
        aggregated = {
            "total_sites_searched": total_sites,
            "successful_searches": successful_searches,
            "failed_searches": failed_searches,
            "success_rate": (successful_searches / total_sites * 100) if total_sites > 0 else 0,
            "results_by_source": by_source,
            "search_summary": {
                "sites_with_results": [r["source"] for r in results if r and r.get("found_product")],
                "sites_with_errors": [r["source"] for r in results if r and not r.get("found_product")]
            }
        }
        
        self.logger.log_step(4, "Results Aggregation", "completed", 
                           f"Aggregated {total_sites} results, {successful_searches} successful")
        self.logger.log_data_extraction("aggregated_results", aggregated, "parallel_processing")
        
        return {"aggregated_results": aggregated}


def run_parallel_demo():
    """Run the parallel processing demo."""
    print("🔄 Starting Enhanced Parallel Processing Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = ParallelProcessingDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted and "aggregated_results" in result.data_extracted:
            agg = result.data_extracted["aggregated_results"]
            print(f"\n📋 Parallel Processing Summary:")
            print(f"   🌐 Sites searched: {agg.get('total_sites_searched', 0)}")
            print(f"   ✅ Successful searches: {agg.get('successful_searches', 0)}")
            print(f"   ❌ Failed searches: {agg.get('failed_searches', 0)}")
            print(f"   📈 Success rate: {agg.get('success_rate', 0):.1f}%")
            
            if agg.get('search_summary'):
                summary = agg['search_summary']
                if summary.get('sites_with_results'):
                    print(f"   🎯 Sites with results: {', '.join(summary['sites_with_results'])}")
                if summary.get('sites_with_errors'):
                    print(f"   ⚠️  Sites with errors: {', '.join(summary['sites_with_errors'])}")
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
    print("Nova Act Enhanced Parallel Processing Demo")
    print("=" * 50)
    
    # Run the demo
    result = run_parallel_demo()
    
    if result.success:
        print("\n🎉 Parallel processing demo completed successfully!")
        print("This demo showcased:")
        print("  • Concurrent browser sessions with ThreadPoolExecutor")
        print("  • Site accessibility validation before parallel execution")
        print("  • Error handling for individual site failures")
        print("  • Results aggregation from multiple sources")
        print("  • Geographic-aware site selection")
    else:
        print("\n⚠️ Demo encountered some issues, but this demonstrates:")
        print("  • Robust error handling in parallel execution")
        print("  • Graceful degradation when sites are unavailable")
        print("  • Comprehensive logging for debugging parallel operations")


if __name__ == "__main__":
    main()