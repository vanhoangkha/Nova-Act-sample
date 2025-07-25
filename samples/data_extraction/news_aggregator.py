#!/usr/bin/env python3
"""
News Aggregation and Analysis Sample

This sample demonstrates how to extract news articles from multiple sources,
analyze sentiment, and create comprehensive reports.
"""

import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict

from nova_act import NovaAct


class NewsArticle(BaseModel):
    title: str
    summary: str
    author: Optional[str]
    publication_date: Optional[str]
    source: str
    category: Optional[str]
    url: str
    sentiment: Optional[str]  # positive, negative, neutral
    key_topics: List[str]
    extracted_at: str


class NewsAggregator:
    def __init__(self):
        self.articles = []
    
    def extract_articles_from_source(self, source_config: dict, topic: str, max_articles: int = 5) -> List[NewsArticle]:
        """Extract articles from a single news source"""
        articles = []
        
        try:
            with NovaAct(starting_page=source_config['url']) as nova:
                # Search for the topic if search is available
                if source_config.get('has_search', True):
                    nova.act(f"search for '{topic}'")
                
                # Extract multiple articles
                for i in range(max_articles):
                    try:
                        # Navigate to article
                        if i == 0:
                            nova.act("click on the first relevant article about the topic")
                        else:
                            nova.act("go back to the previous page")
                            nova.act(f"click on the {i+1}th relevant article about the topic")
                        
                        # Extract article details
                        article_schema = NewsArticle.model_json_schema()
                        result = nova.act(
                            f"""Extract comprehensive article information:
                            - Article title
                            - Brief summary (2-3 sentences)
                            - Author name (if available)
                            - Publication date (if available)
                            - Article category/section (if available)
                            - Analyze sentiment (positive/negative/neutral)
                            - Identify 3-5 key topics or keywords
                            
                            Use source: '{source_config['name']}' and current URL
                            """,
                            schema=article_schema
                        )
                        
                        if result.matches_schema:
                            article = NewsArticle.model_validate(result.parsed_response)
                            article.extracted_at = datetime.now().isoformat()
                            articles.append(article)
                            print(f"✓ Extracted: {article.title[:50]}...")
                        
                    except Exception as e:
                        print(f"Error extracting article {i+1} from {source_config['name']}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error accessing {source_config['name']}: {e}")
        
        return articles
    
    def aggregate_news(self, topic: str, sources: List[dict], max_workers: int = 3) -> List[NewsArticle]:
        """Aggregate news from multiple sources"""
        all_articles = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(self.extract_articles_from_source, source, topic): source 
                for source in sources
            }
            
            for future in as_completed(future_to_source.keys()):
                source_config = future_to_source[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                    print(f"✓ {source_config['name']}: {len(articles)} articles")
                except Exception as e:
                    print(f"✗ Error with {source_config['name']}: {e}")
        
        self.articles.extend(all_articles)
        return all_articles
    
    def analyze_sentiment_trends(self, articles: List[NewsArticle]) -> Dict:
        """Analyze sentiment trends across articles"""
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        sentiment_by_source = {}
        
        for article in articles:
            if article.sentiment:
                sentiment_counts[article.sentiment] = sentiment_counts.get(article.sentiment, 0) + 1
                
                if article.source not in sentiment_by_source:
                    sentiment_by_source[article.source] = {"positive": 0, "negative": 0, "neutral": 0}
                sentiment_by_source[article.source][article.sentiment] += 1
        
        total_articles = len(articles)
        sentiment_percentages = {
            sentiment: (count / total_articles * 100) if total_articles > 0 else 0
            for sentiment, count in sentiment_counts.items()
        }
        
        return {
            "overall_sentiment": sentiment_counts,
            "sentiment_percentages": sentiment_percentages,
            "sentiment_by_source": sentiment_by_source
        }
    
    def extract_trending_topics(self, articles: List[NewsArticle]) -> List[Dict]:
        """Extract and rank trending topics"""
        topic_frequency = {}
        
        for article in articles:
            for topic in article.key_topics:
                topic_lower = topic.lower()
                topic_frequency[topic_lower] = topic_frequency.get(topic_lower, 0) + 1
        
        # Sort by frequency
        trending_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"topic": topic, "frequency": freq, "percentage": (freq / len(articles) * 100)}
            for topic, freq in trending_topics[:20]
        ]
    
    def generate_news_report(self, topic: str, articles: List[NewsArticle]) -> Dict:
        """Generate comprehensive news analysis report"""
        if not articles:
            return {"error": "No articles to analyze"}
        
        # Basic statistics
        sources = list(set(article.source for article in articles))
        categories = list(set(article.category for article in articles if article.category))
        
        # Sentiment analysis
        sentiment_analysis = self.analyze_sentiment_trends(articles)
        
        # Trending topics
        trending_topics = self.extract_trending_topics(articles)
        
        # Recent articles (last 24 hours if dates available)
        recent_articles = []
        for article in articles:
            if article.publication_date:
                # Simple check for recent articles (you might want to improve date parsing)
                if "today" in article.publication_date.lower() or "hour" in article.publication_date.lower():
                    recent_articles.append(article)
        
        # Top articles by source
        articles_by_source = {}
        for article in articles:
            if article.source not in articles_by_source:
                articles_by_source[article.source] = []
            articles_by_source[article.source].append(article)
        
        return {
            "topic": topic,
            "analysis_date": datetime.now().isoformat(),
            "summary": {
                "total_articles": len(articles),
                "sources_covered": len(sources),
                "categories_found": len(categories)
            },
            "sources": sources,
            "sentiment_analysis": sentiment_analysis,
            "trending_topics": trending_topics[:10],
            "recent_articles_count": len(recent_articles),
            "articles_by_source": {
                source: len(articles) for source, articles in articles_by_source.items()
            },
            "sample_headlines": [article.title for article in articles[:10]],
            "detailed_articles": [article.dict() for article in articles]
        }
    
    def save_report(self, report: Dict, filename: str = None):
        """Save news report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_safe = report.get('topic', 'news').replace(' ', '_').lower()
            filename = f"news_report_{topic_safe}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"News report saved to {filename}")


def main():
    # Define news sources to aggregate from
    news_sources = [
        {
            'name': 'BBC News',
            'url': 'https://www.bbc.com/news',
            'has_search': True
        },
        {
            'name': 'Reuters',
            'url': 'https://www.reuters.com',
            'has_search': True
        },
        {
            'name': 'Associated Press',
            'url': 'https://apnews.com',
            'has_search': True
        }
    ]
    
    # Topic to research
    topic = "artificial intelligence"
    
    aggregator = NewsAggregator()
    
    print(f"📰 Aggregating news about '{topic}' from {len(news_sources)} sources...")
    
    # Aggregate news articles
    articles = aggregator.aggregate_news(topic, news_sources)
    
    if articles:
        print(f"\n📊 Successfully extracted {len(articles)} articles")
        
        # Generate comprehensive report
        report = aggregator.generate_news_report(topic, articles)
        
        # Display key insights
        print(f"\n📈 Coverage Summary:")
        print(f"  • Total Articles: {report['summary']['total_articles']}")
        print(f"  • Sources: {report['summary']['sources_covered']}")
        print(f"  • Categories: {report['summary']['categories_found']}")
        
        print(f"\n😊 Sentiment Analysis:")
        sentiment = report['sentiment_analysis']['sentiment_percentages']
        print(f"  • Positive: {sentiment['positive']:.1f}%")
        print(f"  • Neutral: {sentiment['neutral']:.1f}%")
        print(f"  • Negative: {sentiment['negative']:.1f}%")
        
        print(f"\n🔥 Top Trending Topics:")
        for topic_data in report['trending_topics'][:5]:
            print(f"  • {topic_data['topic'].title()}: {topic_data['frequency']} mentions ({topic_data['percentage']:.1f}%)")
        
        print(f"\n📰 Sample Headlines:")
        for headline in report['sample_headlines'][:3]:
            print(f"  • {headline}")
        
        # Save detailed report
        aggregator.save_report(report)
        
    else:
        print("❌ No articles found for analysis")


if __name__ == "__main__":
    main()
