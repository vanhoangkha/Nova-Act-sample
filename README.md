# Nova Act Demo Use Cases

[![Nova Act](https://img.shields.io/badge/Nova%20Act-1.0.4013.0-blue)](https://nova.amazon.com/act)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive collection of **10 practical demo use cases** for Amazon Nova Act, showcasing all major features and capabilities through real-world examples.

## 🚀 What is Nova Act?

Nova Act is Amazon's experimental SDK for building reliable web browser agents. It enables developers to break down complex workflows into smaller, reliable commands while providing advanced features for production use.

## 📋 Demo Overview

This repository contains **10 comprehensive demos** that demonstrate every major Nova Act capability:

| Demo | Description | Key Features |
|------|-------------|--------------|
| **01_basic_ecommerce.py** | Amazon shopping automation | Product search, navigation, cart operations |
| **02_information_extraction.py** | Structured data extraction | Pydantic schemas, data validation, parsing |
| **03_parallel_processing.py** | Concurrent browser sessions | Multi-site comparison, parallel data collection |
| **04_authentication_demo.py** | Login and session management | Persistent sessions, secure credentials |
| **05_file_operations.py** | File upload/download | Multiple file types, bulk operations |
| **06_form_filling.py** | Form automation | Complex forms, validation, multi-step |
| **07_search_filter.py** | Search and filtering | Advanced filters, sorting, refinement |
| **08_real_estate.py** | Property analysis | Market analysis, transportation data |
| **09_interactive_demo.py** | Interactive mode usage | Debugging, breakpoints, manual intervention |
| **10_advanced_features.py** | Production features | Video recording, S3 integration, monitoring |

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

# Run setup script
./setup_demos.sh

# Set your API key
export NOVA_ACT_API_KEY="your_api_key_here"
```

### 3. Run Demos

```bash
# Test basic functionality
python3 basic_test.py

# Run individual demos
python3 01_basic_ecommerce.py

# Run all demos
python3 run_all_demos.py
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

### Common Issues

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

**3. Timeout Issues**
```python
# Increase timeout for complex actions
result = nova.act("complex action", timeout=120)
```

**4. Browser Installation**
```bash
# Install Chrome for better compatibility
playwright install chrome
```

## 📊 Demo Results

When you run the complete demo suite, you'll see:

```
📊 NOVA ACT DEMO SUITE RESULTS
=====================================
🎯 Overall Success Rate: 8/10 (80.0%)
⏱️ Total Execution Time: 245.67 seconds (4.1 minutes)

📋 Detailed Results:
✅ PASS    Basic E-commerce Operations        23.45s
✅ PASS    Information Extraction             18.92s
✅ PASS    Parallel Processing                45.23s
❌ FAIL    Authentication Demo                 0.00s
✅ PASS    File Operations                    31.78s
✅ PASS    Form Filling                       28.34s
✅ PASS    Search & Filter                    22.67s
✅ PASS    Real Estate Analysis               52.89s
✅ PASS    Interactive Mode                   15.43s
❌ FAIL    Advanced Features                   0.00s
```

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
