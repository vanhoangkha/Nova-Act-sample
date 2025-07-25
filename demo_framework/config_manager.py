"""
Configuration management system for Nova Act demos.
"""

import json
import os
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import platform
from datetime import datetime


@dataclass
class EnvironmentInfo:
    """Information about the user's environment."""
    country_code: str
    region: str
    platform: str
    python_version: str
    has_vpn: bool = False
    internet_speed: str = "unknown"


class ConfigManager:
    """Manages configuration and environment detection for demos."""
    
    def __init__(self):
        self.config_file = "demo/config.json"
        self.environment_cache = None
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
    
    def detect_environment(self) -> EnvironmentInfo:
        """Detect user's environment and geographic location."""
        if self.environment_cache:
            return self.environment_cache
        
        # Detect geographic location
        country_code, region = self._detect_location()
        
        # Get system information
        platform_info = platform.platform()
        python_version = platform.python_version()
        
        # Check for VPN (basic heuristic)
        has_vpn = self._detect_vpn()
        
        self.environment_cache = EnvironmentInfo(
            country_code=country_code,
            region=region,
            platform=platform_info,
            python_version=python_version,
            has_vpn=has_vpn
        )
        
        return self.environment_cache
    
    def _detect_location(self) -> tuple[str, str]:
        """Detect user's geographic location."""
        try:
            # Try multiple IP geolocation services
            services = [
                "https://ipapi.co/json/",
                "https://ipinfo.io/json",
                "https://api.ipify.org?format=json"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract country code and region
                        country_code = data.get('country_code', data.get('country', 'US'))
                        region = self._get_region_from_country(country_code)
                        
                        return country_code, region
                except:
                    continue
            
            # Fallback to US if detection fails
            return "US", "north_america"
            
        except Exception:
            return "US", "north_america"
    
    def _get_region_from_country(self, country_code: str) -> str:
        """Map country code to region."""
        region_mapping = {
            # North America
            "US": "north_america", "CA": "north_america", "MX": "north_america",
            
            # Europe
            "GB": "europe", "DE": "europe", "FR": "europe", "IT": "europe",
            "ES": "europe", "NL": "europe", "SE": "europe", "NO": "europe",
            "DK": "europe", "FI": "europe", "CH": "europe", "AT": "europe",
            
            # Asia Pacific
            "JP": "asia_pacific", "KR": "asia_pacific", "CN": "asia_pacific",
            "IN": "asia_pacific", "AU": "asia_pacific", "NZ": "asia_pacific",
            "SG": "asia_pacific", "HK": "asia_pacific", "TW": "asia_pacific",
            
            # Other regions
            "BR": "south_america", "AR": "south_america", "CL": "south_america",
            "ZA": "africa", "EG": "africa", "NG": "africa"
        }
        
        return region_mapping.get(country_code, "other")
    
    def _detect_vpn(self) -> bool:
        """Basic VPN detection (heuristic)."""
        try:
            # Check for common VPN indicators
            import subprocess
            
            # Check for VPN network interfaces (basic check)
            if platform.system() == "Windows":
                result = subprocess.run(["ipconfig"], capture_output=True, text=True)
                output = result.stdout.lower()
                vpn_indicators = ["vpn", "tunnel", "tap", "tun"]
                return any(indicator in output for indicator in vpn_indicators)
            
            return False  # More complex detection would be needed for other platforms
            
        except Exception:
            return False
    
    def get_optimal_sites(self, demo_type: str) -> List[str]:
        """Get optimal sites for a demo type based on user's location."""
        env = self.detect_environment()
        
        site_mappings = {
            "ecommerce": {
                "north_america": ["https://amazon.com", "https://ebay.com", "https://walmart.com"],
                "europe": ["https://amazon.co.uk", "https://ebay.co.uk", "https://zalando.com"],
                "asia_pacific": ["https://amazon.co.jp", "https://rakuten.com", "https://alibaba.com"],
                "other": ["https://ebay.com", "https://aliexpress.com"]
            },
            "news": {
                "north_america": ["https://cnn.com", "https://bbc.com", "https://reuters.com"],
                "europe": ["https://bbc.com", "https://theguardian.com", "https://reuters.com"],
                "asia_pacific": ["https://bbc.com", "https://reuters.com", "https://japantimes.co.jp"],
                "other": ["https://bbc.com", "https://reuters.com"]
            },
            "real_estate": {
                "north_america": ["https://zillow.com", "https://realtor.com", "https://redfin.com"],
                "europe": ["https://rightmove.co.uk", "https://immobilienscout24.de", "https://seloger.com"],
                "asia_pacific": ["https://realestate.com.au", "https://suumo.jp"],
                "other": ["https://globalpropertyguide.com"]
            },
            "forms": {
                "north_america": ["https://forms.gle", "https://typeform.com", "https://surveymonkey.com"],
                "europe": ["https://forms.gle", "https://typeform.com", "https://surveymonkey.com"],
                "asia_pacific": ["https://forms.gle", "https://typeform.com"],
                "other": ["https://forms.gle", "https://typeform.com"]
            }
        }
        
        return site_mappings.get(demo_type, {}).get(env.region, site_mappings[demo_type]["other"])
    
    def save_successful_config(self, demo_name: str, config: Dict[str, Any]):
        """Save a successful configuration for future use."""
        try:
            # Load existing config
            all_configs = self.load_all_configs()
            
            # Update with new successful config
            all_configs[demo_name] = {
                "config": config,
                "environment": self.detect_environment().__dict__,
                "timestamp": str(datetime.now())
            }
            
            # Save back to file
            with open(self.config_file, 'w') as f:
                json.dump(all_configs, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def load_config(self, demo_name: str) -> Optional[Dict[str, Any]]:
        """Load saved configuration for a demo."""
        try:
            all_configs = self.load_all_configs()
            demo_config = all_configs.get(demo_name)
            
            if demo_config:
                # Check if environment matches
                saved_env = demo_config.get("environment", {})
                current_env = self.detect_environment().__dict__
                
                # If country matches, use saved config
                if saved_env.get("country_code") == current_env.get("country_code"):
                    return demo_config.get("config")
            
            return None
            
        except Exception:
            return None
    
    def load_all_configs(self) -> Dict[str, Any]:
        """Load all saved configurations."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def get_site_alternatives(self, primary_site: str) -> List[str]:
        """Get alternative sites when primary site fails."""
        alternatives = {
            "amazon.com": ["ebay.com", "walmart.com", "target.com"],
            "amazon.co.uk": ["ebay.co.uk", "argos.co.uk", "johnlewis.com"],
            "amazon.co.jp": ["rakuten.com", "yahoo.co.jp"],
            "zillow.com": ["realtor.com", "redfin.com", "homes.com"],
            "cnn.com": ["bbc.com", "reuters.com", "npr.org"],
            "bbc.com": ["reuters.com", "theguardian.com", "cnn.com"]
        }
        
        domain = primary_site.replace("https://", "").replace("http://", "")
        return alternatives.get(domain, [])
    
    def validate_site_access(self, url: str) -> bool:
        """Check if a site is accessible from user's location."""
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            return response.status_code < 400
        except Exception:
            return False
    
    def get_recommended_config(self, demo_type: str) -> Dict[str, Any]:
        """Get recommended configuration for a demo type."""
        env = self.detect_environment()
        
        base_config = {
            "timeout": 30,
            "retry_attempts": 3,
            "wait_time": 2,
            "screenshot_on_error": True,
            "verbose_logging": True
        }
        
        # Adjust based on region
        if env.region != "north_america":
            base_config.update({
                "timeout": 45,  # Longer timeout for international users
                "retry_attempts": 5,
                "use_fallback_sites": True
            })
        
        # Demo-specific adjustments
        if demo_type == "ecommerce":
            base_config["sites"] = self.get_optimal_sites("ecommerce")
        elif demo_type == "news":
            base_config["sites"] = self.get_optimal_sites("news")
        elif demo_type == "real_estate":
            base_config["sites"] = self.get_optimal_sites("real_estate")
        
        return base_config