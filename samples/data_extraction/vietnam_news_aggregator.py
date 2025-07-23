#!/usr/bin/env python3
"""
Vietnam News Aggregation Sample

This sample demonstrates how to extract news articles from Vietnamese news sources
like VnExpress, Tuoi Tre, Thanh Nien, and Dan Tri.
"""

import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict

from nova_act import NovaAct


class VietnamNewsArticle(BaseModel):
    title: str
    summary: str
    author: Optional[str]
    publication_date: Optional[str]
    source: str
    category: Optional[str]
    url: str
    sentiment: Optional[str]  # tích cực, tiêu cực, trung tính
    key_topics: List[str]
    view_count: Optional[str] = None
    comment_count: Optional[str] = None
    extracted_at: str


class VietnamNewsAggregator:
    def __init__(self):
        self.articles = []
    
    def extract_articles_from_source(self, source_config: dict, topic: str, max_articles: int = 5) -> List[VietnamNewsArticle]:
        """Extract articles from a Vietnamese news source"""
        articles = []
        
        try:
            with NovaAct(starting_page=source_config['url']) as nova:
                # Search for the topic if search is available
                if source_config.get('has_search', True):
                    nova.act(f"tìm kiếm '{topic}'")
                
                # Extract multiple articles
                for i in range(max_articles):
                    try:
                        # Navigate to article
                        if i == 0:
                            nova.act("nhấp vào bài viết đầu tiên liên quan đến chủ đề")
                        else:
                            nova.act("quay lại trang trước")
                            nova.act(f"nhấp vào bài viết thứ {i+1} liên quan đến chủ đề")
                        
                        # Extract article details
                        article_schema = VietnamNewsArticle.model_json_schema()
                        result = nova.act(
                            f"""Trích xuất thông tin bài viết một cách chi tiết:
                            - Tiêu đề bài viết
                            - Tóm tắt ngắn gọn (2-3 câu)
                            - Tên tác giả (nếu có)
                            - Ngày xuất bản (nếu có)
                            - Chuyên mục/danh mục (nếu có)
                            - Phân tích cảm xúc (tích cực/tiêu cực/trung tính)
                            - Xác định 3-5 từ khóa chính hoặc chủ đề
                            - Số lượt xem (nếu có)
                            - Số bình luận (nếu có)
                            
                            Sử dụng source: '{source_config['name']}' và URL hiện tại
                            """,
                            schema=article_schema
                        )
                        
                        if result.matches_schema:
                            article = VietnamNewsArticle.model_validate(result.parsed_response)
                            article.extracted_at = datetime.now().isoformat()
                            articles.append(article)
                            print(f"✓ Đã trích xuất: {article.title[:50]}...")
                        
                    except Exception as e:
                        print(f"Lỗi trích xuất bài viết {i+1} từ {source_config['name']}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Lỗi truy cập {source_config['name']}: {e}")
        
        return articles
    
    def aggregate_vietnam_news(self, topic: str, sources: List[dict], max_workers: int = 2) -> List[VietnamNewsArticle]:
        """Aggregate news from multiple Vietnamese sources"""
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
                    print(f"✓ {source_config['name']}: {len(articles)} bài viết")
                except Exception as e:
                    print(f"✗ Lỗi với {source_config['name']}: {e}")
        
        self.articles.extend(all_articles)
        return all_articles
    
    def analyze_vietnam_sentiment(self, articles: List[VietnamNewsArticle]) -> Dict:
        """Analyze sentiment trends in Vietnamese news"""
        sentiment_counts = {"tích cực": 0, "tiêu cực": 0, "trung tính": 0}
        sentiment_by_source = {}
        
        for article in articles:
            if article.sentiment:
                sentiment_counts[article.sentiment] = sentiment_counts.get(article.sentiment, 0) + 1
                
                if article.source not in sentiment_by_source:
                    sentiment_by_source[article.source] = {"tích cực": 0, "tiêu cực": 0, "trung tính": 0}
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
    
    def extract_vietnam_trending_topics(self, articles: List[VietnamNewsArticle]) -> List[Dict]:
        """Extract and rank trending topics in Vietnamese news"""
        topic_frequency = {}
        
        for article in articles:
            for topic in article.key_topics:
                topic_lower = topic.lower()
                topic_frequency[topic_lower] = topic_frequency.get(topic_lower, 0) + 1
        
        # Sort by frequency
        trending_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"topic": topic.title(), "frequency": freq, "percentage": (freq / len(articles) * 100)}
            for topic, freq in trending_topics[:20]
        ]
    
    def analyze_vietnam_categories(self, articles: List[VietnamNewsArticle]) -> Dict:
        """Analyze news categories in Vietnamese media"""
        category_stats = {}
        
        for article in articles:
            if article.category:
                category = article.category.lower()
                category_stats[category] = category_stats.get(category, 0) + 1
        
        # Sort by frequency
        top_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_categories": len(category_stats),
            "category_distribution": category_stats,
            "top_categories": [
                {"category": cat.title(), "count": count, "percentage": (count / len(articles) * 100)}
                for cat, count in top_categories
            ]
        }
    
    def generate_vietnam_news_report(self, topic: str, articles: List[VietnamNewsArticle]) -> Dict:
        """Generate comprehensive Vietnamese news analysis report"""
        if not articles:
            return {"error": "Không có bài viết để phân tích"}
        
        # Basic statistics
        sources = list(set(article.source for article in articles))
        
        # Sentiment analysis
        sentiment_analysis = self.analyze_vietnam_sentiment(articles)
        
        # Trending topics
        trending_topics = self.extract_vietnam_trending_topics(articles)
        
        # Category analysis
        category_analysis = self.analyze_vietnam_categories(articles)
        
        # Source analysis
        articles_by_source = {}
        for article in articles:
            if article.source not in articles_by_source:
                articles_by_source[article.source] = []
            articles_by_source[article.source].append(article)
        
        # Engagement analysis (views and comments)
        engagement_stats = self._analyze_engagement(articles)
        
        return {
            "topic": topic,
            "analysis_date": datetime.now().isoformat(),
            "summary": {
                "total_articles": len(articles),
                "sources_covered": len(sources),
                "categories_found": len(set(a.category for a in articles if a.category))
            },
            "sources": sources,
            "sentiment_analysis": sentiment_analysis,
            "trending_topics": trending_topics[:10],
            "category_analysis": category_analysis,
            "engagement_statistics": engagement_stats,
            "articles_by_source": {
                source: len(articles) for source, articles in articles_by_source.items()
            },
            "sample_headlines": [article.title for article in articles[:10]],
            "recommendations": self._generate_news_recommendations(articles),
            "detailed_articles": [article.dict() for article in articles]
        }
    
    def _analyze_engagement(self, articles: List[VietnamNewsArticle]) -> Dict:
        """Analyze engagement metrics of Vietnamese news articles"""
        articles_with_views = [a for a in articles if a.view_count]
        articles_with_comments = [a for a in articles if a.comment_count]
        
        return {
            "articles_with_view_count": len(articles_with_views),
            "articles_with_comment_count": len(articles_with_comments),
            "engagement_rate": (len(articles_with_comments) / len(articles) * 100) if articles else 0
        }
    
    def _generate_news_recommendations(self, articles: List[VietnamNewsArticle]) -> List[str]:
        """Generate recommendations for Vietnamese news consumption"""
        recommendations = []
        
        if not articles:
            return recommendations
        
        # Most active source
        source_counts = {}
        for article in articles:
            source_counts[article.source] = source_counts.get(article.source, 0) + 1
        
        most_active_source = max(source_counts.items(), key=lambda x: x[1])
        recommendations.append(f"Nguồn tin tích cực nhất: {most_active_source[0]} với {most_active_source[1]} bài viết")
        
        # Sentiment recommendation
        sentiment_counts = {"tích cực": 0, "tiêu cực": 0, "trung tính": 0}
        for article in articles:
            if article.sentiment:
                sentiment_counts[article.sentiment] += 1
        
        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])
        recommendations.append(f"Xu hướng cảm xúc chủ đạo: {dominant_sentiment[0]} ({dominant_sentiment[1]} bài viết)")
        
        # Category recommendation
        categories = {}
        for article in articles:
            if article.category:
                categories[article.category] = categories.get(article.category, 0) + 1
        
        if categories:
            top_category = max(categories.items(), key=lambda x: x[1])
            recommendations.append(f"Chuyên mục được quan tâm nhất: {top_category[0]} ({top_category[1]} bài viết)")
        
        return recommendations
    
    def save_report(self, report: Dict, filename: str = None):
        """Save Vietnamese news report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_safe = report.get('topic', 'news').replace(' ', '_').lower()
            filename = f"vietnam_news_report_{topic_safe}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Báo cáo tin tức đã được lưu vào {filename}")


def main():
    # Vietnamese news sources to aggregate from
    vietnam_news_sources = [
        {
            'name': 'VnExpress',
            'url': 'https://vnexpress.net',
            'has_search': True
        },
        {
            'name': 'Tuoi Tre',
            'url': 'https://tuoitre.vn',
            'has_search': True
        },
        {
            'name': 'Thanh Nien',
            'url': 'https://thanhnien.vn',
            'has_search': True
        },
        {
            'name': 'Dan Tri',
            'url': 'https://dantri.com.vn',
            'has_search': True
        }
    ]
    
    # Topic to research
    topic = "công nghệ AI"
    
    aggregator = VietnamNewsAggregator()
    
    print(f"📰 Tổng hợp tin tức về '{topic}' từ {len(vietnam_news_sources)} nguồn...")
    
    # Aggregate Vietnamese news articles
    articles = aggregator.aggregate_vietnam_news(topic, vietnam_news_sources)
    
    if articles:
        print(f"\n📊 Đã trích xuất thành công {len(articles)} bài viết")
        
        # Generate comprehensive report
        report = aggregator.generate_vietnam_news_report(topic, articles)
        
        # Display key insights
        print(f"\n📈 Tóm tắt phủ sóng:")
        print(f"  • Tổng số bài viết: {report['summary']['total_articles']}")
        print(f"  • Nguồn tin: {report['summary']['sources_covered']}")
        print(f"  • Chuyên mục: {report['summary']['categories_found']}")
        
        print(f"\n😊 Phân tích cảm xúc:")
        sentiment = report['sentiment_analysis']['sentiment_percentages']
        print(f"  • Tích cực: {sentiment['tích cực']:.1f}%")
        print(f"  • Trung tính: {sentiment['trung tính']:.1f}%")
        print(f"  • Tiêu cực: {sentiment['tiêu cực']:.1f}%")
        
        print(f"\n🔥 Chủ đề nổi bật:")
        for topic_data in report['trending_topics'][:5]:
            print(f"  • {topic_data['topic']}: {topic_data['frequency']} lần xuất hiện ({topic_data['percentage']:.1f}%)")
        
        print(f"\n📰 Tiêu đề mẫu:")
        for headline in report['sample_headlines'][:3]:
            print(f"  • {headline}")
        
        if 'recommendations' in report:
            print(f"\n💡 Khuyến nghị:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        # Save detailed report
        aggregator.save_report(report)
        
    else:
        print("❌ Không tìm thấy bài viết để phân tích")


if __name__ == "__main__":
    main()
