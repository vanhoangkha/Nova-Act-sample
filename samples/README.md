# Nova Act Samples Collection

This directory contains comprehensive samples demonstrating various use cases for Amazon Nova Act across different industries and applications.

## 📁 Directory Structure

```
samples/
├── ecommerce/           # E-commerce and retail automation
├── data_extraction/     # Web scraping and data collection
├── automation/          # General automation tasks
├── research/            # Academic and market research
├── real_estate/         # Property and real estate analysis
├── finance/             # Financial data and analysis
├── social_media/        # Social media monitoring
└── testing/             # Web application testing
```

## 🚀 Getting Started

### Prerequisites

1. **Nova Act Installation**:
   ```bash
   pip install nova-act
   ```

2. **API Key Setup**:
   ```bash
   export NOVA_ACT_API_KEY="your_api_key"
   ```
   Get your API key from [nova.amazon.com/act](https://nova.amazon.com/act)

3. **Dependencies**:
   ```bash
   pip install pydantic concurrent.futures
   ```

### Running Samples

Each sample is self-contained and can be run independently:

```bash
cd samples/ecommerce
python product_price_monitor.py
```

## 📊 Sample Categories

### 🛒 E-commerce
- **Product Price Monitor** (`ecommerce/product_price_monitor.py`)
  - Monitor product prices across multiple sites
  - Track price changes and find deals
  - Generate price history reports

- **Competitor Analysis** (`ecommerce/competitor_analysis.py`)
  - Compare products across different platforms
  - Analyze pricing strategies and features
  - Generate competitive intelligence reports

### 📈 Data Extraction
- **News Aggregator** (`data_extraction/news_aggregator.py`)
  - Collect news articles from multiple sources
  - Analyze sentiment and trending topics
  - Generate comprehensive news reports

- **Job Market Analyzer** (`data_extraction/job_market_analyzer.py`)
  - Extract job postings from job boards
  - Analyze salary trends and skill demands
  - Generate market intelligence reports

### 🏠 Real Estate
- **Property Market Analyzer** (`real_estate/property_market_analyzer.py`)
  - Analyze real estate listings across platforms
  - Compare prices and market trends
  - Find best value properties

### 🤖 Automation
- **Form Automation** (`automation/form_automation.py`)
  - Automate form filling across websites
  - Handle different input types and validation
  - Batch process multiple forms

### 🔬 Research
- **Academic Research Assistant** (`research/academic_research_assistant.py`)
  - Search academic databases for papers
  - Analyze research trends and citations
  - Generate literature review reports

### 🧪 Testing
- **Web App Tester** (`testing/web_app_tester.py`)
  - Automated web application testing
  - Functional, UI, and regression testing
  - Generate comprehensive test reports

## 🛠️ Common Patterns

### 1. Parallel Processing
Most samples use ThreadPoolExecutor for concurrent operations:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process_site, site) for site in sites]
    for future in as_completed(futures):
        result = future.result()
```

### 2. Data Validation with Pydantic
All samples use Pydantic models for data validation:

```python
from pydantic import BaseModel

class DataModel(BaseModel):
    field1: str
    field2: int
    field3: Optional[float]

# Use with Nova Act
result = nova.act("extract data", schema=DataModel.model_json_schema())
if result.matches_schema:
    data = DataModel.model_validate(result.parsed_response)
```

### 3. Error Handling
Robust error handling patterns:

```python
try:
    with NovaAct(starting_page=url) as nova:
        result = nova.act("perform action")
        # Process result
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

### 4. Report Generation
Standardized reporting across samples:

```python
def generate_report(self, data: List[DataModel]) -> Dict:
    return {
        "analysis_date": datetime.now().isoformat(),
        "summary": {"total_items": len(data)},
        "detailed_results": [item.dict() for item in data]
    }
```

## 📋 Sample Features

### Common Features Across Samples:
- ✅ **Parallel Processing**: Multiple sites/sources processed concurrently
- ✅ **Data Validation**: Pydantic models for structured data
- ✅ **Error Handling**: Robust error handling and recovery
- ✅ **Report Generation**: JSON reports with detailed analytics
- ✅ **Configurable**: Easy to modify for different use cases
- ✅ **Logging**: Comprehensive logging and progress tracking

### Advanced Features:
- 🔄 **Retry Logic**: Automatic retry on failures
- 📊 **Analytics**: Trend analysis and insights
- 💾 **Data Persistence**: Save results to files
- 🎯 **Filtering**: Advanced filtering and search capabilities
- 📈 **Visualization**: Data ready for visualization tools

## 🔧 Customization Guide

### Modifying Samples for Your Use Case

1. **Change Target Websites**:
   ```python
   sites_to_analyze = [
       {'name': 'Your Site', 'url': 'https://yoursite.com'}
   ]
   ```

2. **Adjust Data Models**:
   ```python
   class YourDataModel(BaseModel):
       your_field: str
       # Add your specific fields
   ```

3. **Customize Analysis**:
   ```python
   def your_custom_analysis(self, data):
       # Implement your specific analysis logic
       pass
   ```

## 📚 Best Practices

### 1. Rate Limiting
Be respectful to websites:
```python
import time
time.sleep(2)  # Wait between requests
```

### 2. Error Recovery
Handle failures gracefully:
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        result = nova.act("action")
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise e
        time.sleep(5)  # Wait before retry
```

### 3. Data Quality
Validate extracted data:
```python
if result.matches_schema:
    data = DataModel.model_validate(result.parsed_response)
else:
    print("Data validation failed")
```

## 🚨 Important Notes

### Security Considerations
- Never hardcode sensitive information
- Use environment variables for API keys
- Be cautious with authentication data

### Legal Compliance
- Respect robots.txt files
- Follow website terms of service
- Consider rate limiting and ethical scraping

### Performance Tips
- Use appropriate max_workers for parallel processing
- Implement caching where appropriate
- Monitor memory usage for large datasets

## 🤝 Contributing

To add new samples:

1. Create a new directory for your category
2. Follow the existing code structure and patterns
3. Include comprehensive error handling
4. Add documentation and examples
5. Test thoroughly before submitting

## 📞 Support

For questions or issues:
- Email: nova-act@amazon.com
- Check the main README.md for general Nova Act documentation
- Review the FAQ.md for common questions

## 📄 License

These samples are provided under the same license as Nova Act. See LICENSE file for details.
