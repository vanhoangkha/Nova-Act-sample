# Nova Act Demo Use Cases - Enhanced Edition

[![Nova Act](https://img.shields.io/badge/Nova%20Act-1.0.4013.0-blue)](https://nova.amazon.com/act)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/Framework-Enhanced-brightgreen)](https://github.com/vanhoangkha/Nova-Act-sample)

A comprehensive collection of **10 practical demo use cases** for Amazon Nova Act, now featuring **robust error handling**, **geographic awareness**, and **production-ready reliability**.

## 🚀 What is Nova Act?

Nova Act is Amazon's experimental SDK for building reliable web browser agents. It enables developers to break down complex workflows into smaller, reliable commands while providing advanced features for production use.

## 🆕 What's New in Enhanced Edition

### 🛡️ Robust Error Handling
- **Geographic Restriction Detection**: Automatically detects and handles region-blocked sites
- **Fallback Site Support**: Switches to alternative sites when primary sites fail
- **Graceful Degradation**: Continues execution even when individual steps fail
- **Comprehensive Error Recovery**: Smart retry logic with exponential backoff

### 🌍 Geographic Awareness
- **Automatic Region Detection**: Detects user's location and suggests optimal sites
- **Region-Specific Site Mapping**: Uses appropriate alternatives (Amazon.co.uk for UK users, etc.)
- **VPN Detection**: Basic detection of VPN usage for better site selection
- **International Compatibility**: Works reliably from any geographic location

### 📊 Enhanced Logging & Reporting
- **Structured Logging**: JSON-formatted logs with timestamps and context
- **Performance Metrics**: Detailed timing and success rate tracking
- **Comprehensive Reports**: Automated generation of execution summaries
- **Troubleshooting Guidance**: Specific tips for common issues

### 🏗️ Production-Ready Framework
- **BaseDemo Class**: Standardized demo structure with common functionality
- **Multi-Selector Engine**: Multiple element selection strategies with fallbacks
- **Configuration Management**: Environment-aware configuration with persistence
- **Modular Architecture**: Reusable components for building new demos

## 📋 Demo Overview

This repository contains **10 comprehensive demos** enhanced with the new reliability framework:

| Demo | Description | Enhanced Features |
|------|-------------|-------------------|
| **01_basic_ecommerce.py** | E-commerce automation | ✅ Geographic site selection, fallback stores, cart error handling |
| **02_information_extraction.py** | Structured data extraction | ✅ Multi-site extraction, schema validation, region-aware sources |
| **03_parallel_processing.py** | Concurrent browser sessions | ✅ Site availability checking, parallel error handling, result aggregation |
| **04_authentication_demo.py** | Login and session management | ✅ Session persistence, secure credential handling, auth state validation |
| **05_file_operations.py** | File upload/download | ✅ File validation, integrity checking, alternative hosting support |
| **06_form_filling.py** | Form automation | ✅ Adaptive form field detection, multi-strategy filling, validation |
| **07_search_filter.py** | Search and filtering | ✅ Multi-criteria filtering, sorting, search refinement strategies |
| **08_real_estate.py** | Property analysis | ✅ Location-aware property sites, transportation analysis, data extraction |
| **09_interactive_demo.py** | Interactive mode usage | ✅ Enhanced debugging, breakpoints, state capture, manual intervention |
| **10_advanced_features.py** | Production features | ✅ Video recording, S3 integration, monitoring, performance optimization |

**Legend**: ✅ Fully Enhanced and Production-Ready

## 🏗️ Enhanced Framework Architecture

### Core Components

```
demo_framework/
├── base_demo.py          # Abstract base class for all demos
├── error_handler.py      # Centralized error handling and recovery
├── config_manager.py     # Environment detection and configuration
├── logger.py            # Enhanced logging with structured output
├── multi_selector.py    # Multiple selector strategies with fallbacks
└── __init__.py          # Framework exports
```

### Key Features

- **BaseDemo Class**: Standardized demo lifecycle with setup, execute, cleanup
- **Error Recovery**: Automatic retry logic with exponential backoff
- **Geographic Awareness**: Detects user location and selects optimal sites
- **Multi-Selector Engine**: Tries multiple element selection strategies
- **Structured Logging**: JSON logs with performance metrics and debugging info
- **Configuration Persistence**: Saves successful configurations for reuse

## 🛠️ Quick Setup

### 1. Prerequisites
- **Python 3.10+**
- **Nova Act API Key** from [nova.amazon.com/act](https://nova.amazon.com/act)
- **Linux/macOS/WSL2** (Windows 10+ supported)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/vanhoangkha/Nova-Act-sample.git
cd Nova-Act-sample

# Install dependencies (if needed)
pip install nova-act pydantic requests

# Set your API key
export NOVA_ACT_API_KEY="your_api_key_here"
```

### 3. Run Enhanced Demos

```bash
# Run the complete enhanced demo suite (recommended)
python3 complete_demo_suite.py

# Or run the orchestrator directly
python3 run_all_demos.py

# Or run individual enhanced demos
python3 01_basic_ecommerce.py
python3 02_information_extraction.py
python3 03_parallel_processing.py
python3 04_authentication_demo.py
python3 05_file_operations.py
python3 06_form_filling.py
python3 07_search_filter.py
python3 08_real_estate.py
python3 09_interactive_demo.py
python3 10_advanced_features.py
```

### 4. Framework Usage

```python
from demo_framework import BaseDemo, DemoResult

class MyCustomDemo(BaseDemo):
    def setup(self) -> bool:
        # Validate prerequisites
        return True
    
    def execute_steps(self) -> Dict[str, Any]:
        # Your demo logic here
        return {"extracted_data": "example"}
    
    def get_fallback_sites(self) -> List[str]:
        # Alternative sites if primary fails
        return ["https://backup-site.com"]

# Run your demo
demo = MyCustomDemo()
result = demo.run()
```

## 📚 Demo Details

### 🛒 E-commerce Automation
```python
with NovaAct(starting_page="https://www.amazon.com") as nova:
    nova.act("search for wireless headphones")
    nova.act("select the first result")
    nova.act("add to cart")
```

### 📊 Data Extraction with Pydantic
```python
class Product(BaseModel):
    name: str
    price: str
    rating: Optional[str] = None

result = nova.act("Extract product information", schema=Product.model_json_schema())
product = Product.model_validate(result.parsed_response)
```

### 🔄 Parallel Processing
```python
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(search_product, site) for site in websites]
    results = [future.result() for future in futures]
```

### 🔐 Authentication & Sessions
```python
with NovaAct(user_data_dir="./sessions", clone_user_data_dir=False) as nova:
    nova.act("sign in to the website")
    # Session persists for future runs
```

## 🎯 Key Features Demonstrated

### ✅ Core Nova Act Concepts
- **Prescriptive Prompting**: Breaking complex tasks into smaller `act()` calls
- **Schema-based Extraction**: Using Pydantic for structured data
- **Error Handling**: Robust error management and validation
- **Session Management**: Persistent authentication and state

### 🚀 Advanced Capabilities
- **Parallel Execution**: Multiple browser instances
- **File Operations**: Upload/download automation
- **Form Automation**: Complex form handling
- **Real-time Analysis**: Data extraction and processing

### 🛠️ Production Features
- **Video Recording**: Session recording for debugging
- **S3 Integration**: Cloud storage for session data
- **Custom Logging**: Detailed execution traces
- **Headless Operation**: Server-friendly execution

## 📖 Usage Examples

### Basic Usage
```python
from nova_act import NovaAct

with NovaAct(starting_page="https://example.com", headless=True) as nova:
    result = nova.act("What is the main heading?")
    print(result.response)
```

### Information Extraction
```python
from pydantic import BaseModel
from nova_act import NovaAct

class NewsArticle(BaseModel):
    headline: str
    summary: str
    author: Optional[str] = None

with NovaAct(starting_page="https://news.site.com") as nova:
    result = nova.act("Extract the top news article", 
                     schema=NewsArticle.model_json_schema())
    if result.matches_schema:
        article = NewsArticle.model_validate(result.parsed_response)
        print(f"Headline: {article.headline}")
```

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor
from nova_act import NovaAct

def search_site(site_url, query):
    with NovaAct(starting_page=site_url) as nova:
        return nova.act(f"search for {query}")

sites = ["https://site1.com", "https://site2.com", "https://site3.com"]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(lambda site: search_site(site, "laptops"), sites))
```

## 🔧 Configuration

### Environment Variables
```bash
export NOVA_ACT_API_KEY="your_api_key"
export NOVA_ACT_LOG_LEVEL="10"  # DEBUG level
```

### Advanced Configuration
```python
nova = NovaAct(
    starting_page="https://example.com",
    headless=True,                    # Server environments
    user_data_dir="./sessions",       # Persistent sessions
    logs_directory="./logs",          # Custom log location
    record_video=True,                # Record sessions
    proxy={"server": "http://proxy:8080"}  # Proxy support
)
```

## 🐛 Troubleshooting

### Enhanced Framework Issues

**1. Geographic Restrictions**
```
✅ The framework automatically detects and handles this!

What happens:
- Detects your location (US, UK, EU, etc.)
- Selects region-appropriate sites
- Falls back to alternatives if primary sites are blocked
- Provides clear messaging about limitations
```

**2. Website Changes**
```
✅ Multi-selector engine handles this!

What happens:
- Tries multiple selector strategies (ID, class, text, xpath)
- Automatically falls back when primary selectors fail
- Waits with exponential backoff for elements to load
- Logs detailed information for debugging
```

**3. Demo Failures**
```
✅ Graceful degradation keeps demos running!

What happens:
- Individual step failures don't crash entire demo
- Error recovery attempts alternative approaches
- Comprehensive logging helps identify root causes
- Detailed troubleshooting tips provided in results
```

### Traditional Issues

**1. "Missing X server" Error**
```bash
# Solution: Use headless mode
nova = NovaAct(starting_page="...", headless=True)
```

**2. API Key Issues**
```bash
# Verify API key is set
echo $NOVA_ACT_API_KEY

# Check key format (should be UUID)
python3 -c "import os; print(len(os.getenv('NOVA_ACT_API_KEY', '')))"
```

**3. Framework Import Issues**
```bash
# Ensure you're in the correct directory
cd Nova-Act-sample

# Check if framework files exist
ls demo_framework/

# Run with Python path if needed
PYTHONPATH=. python3 01_basic_ecommerce.py
```

## 📊 Enhanced Demo Results

When you run the enhanced demo suite, you'll see comprehensive reporting:

```
Enhanced Nova Act Demo Suite Runner
==================================================

Nova Act Demo Suite Comprehensive Report
================================================================================
Generated: 2024-12-19 14:30:15
Total Execution Time: 180.45 seconds

SUMMARY
========================================
Total Demos: 10
Successful: 9
Failed: 1
Success Rate: 90.0%

ENVIRONMENT INFORMATION
========================================
Country: US
Region: north_america
Platform: Linux-5.4.0-74-generic-x86_64
Python Version: 3.10.12
VPN Detected: False

✅ SUCCESSFUL DEMOS (9)
========================================
• Basic E-commerce Operations
  Duration: 25.34s
  Steps: 6/6
  
• Information Extraction
  Duration: 18.92s
  Steps: 4/4
  
• [Additional demos...]

❌ FAILED DEMOS (1)
========================================
• Advanced Features Demo
  Duration: 5.23s
  Errors: 1
    - ConnectionError: S3 service unavailable
      Troubleshooting:
        * Check your AWS credentials
        * Verify S3 bucket permissions
        * Try running without S3 integration

RECOMMENDATIONS
========================================
⚠️ Some demos encountered issues:
• Check individual demo logs for detailed troubleshooting
• Consider that some sites may have geographic restrictions
• The framework automatically tries alternative sites
```

### Key Improvements

- **Higher Success Rates**: Geographic awareness and fallbacks improve reliability
- **Detailed Error Analysis**: Specific troubleshooting guidance for each failure
- **Environment Context**: Understanding of your setup helps with debugging
- **Performance Tracking**: Detailed timing and step completion metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-demo`)
3. Commit your changes (`git commit -m 'Add amazing demo'`)
4. Push to the branch (`git push origin feature/amazing-demo`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Nova Act Documentation**: [Official README](https://github.com/amazon-science/nova-act)
- **Issues**: Report bugs via [GitHub Issues](https://github.com/vanhoangkha/Nova-Act-sample/issues)
- **Nova Act Support**: nova-act@amazon.com

## 🙏 Acknowledgments

- **Amazon Nova Act Team** for creating this amazing SDK
- **Nova Act Community** for feedback and contributions
- **Contributors** who help improve these demos

---

⭐ **Star this repository** if you find these demos helpful!

🔗 **Get your Nova Act API key**: [nova.amazon.com/act](https://nova.amazon.com/act)
