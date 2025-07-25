#!/usr/bin/env python3
"""
Academic Research Assistant Sample

This sample demonstrates how to automate academic research tasks including
literature searches, citation extraction, and research paper analysis.
"""

import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict

from nova_act import NovaAct


class ResearchPaper(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    publication_year: Optional[int]
    journal: Optional[str]
    doi: Optional[str]
    citation_count: Optional[int]
    keywords: List[str]
    research_area: Optional[str]
    url: str
    source: str
    extracted_at: str


class Citation(BaseModel):
    title: str
    authors: List[str]
    year: Optional[int]
    journal: Optional[str]
    citation_format: str  # APA, MLA, Chicago, etc.


class ResearchQuery(BaseModel):
    topic: str
    keywords: List[str]
    year_range: Optional[Dict[str, int]]  # {"start": 2020, "end": 2024}
    research_area: Optional[str]


class AcademicResearchAssistant:
    def __init__(self):
        self.research_papers = []
        self.citations = []
    
    def search_academic_database(self, database_config: dict, query: ResearchQuery, max_papers: int = 20) -> List[ResearchPaper]:
        """Search for research papers in an academic database"""
        papers = []
        
        try:
            with NovaAct(starting_page=database_config['url']) as nova:
                # Construct search query
                search_terms = f"{query.topic} {' '.join(query.keywords)}"
                
                # Perform search
                nova.act(f"search for '{search_terms}'")
                
                # Apply filters if available
                if query.year_range:
                    nova.act(f"filter results by publication year from {query.year_range['start']} to {query.year_range['end']}")
                
                if query.research_area:
                    nova.act(f"filter results by research area or subject: {query.research_area}")
                
                # Extract paper information
                for i in range(max_papers):
                    try:
                        # Navigate to paper details
                        if i == 0:
                            nova.act("click on the first research paper result")
                        else:
                            nova.act("go back to search results")
                            nova.act(f"click on the {i+1}th research paper result")
                        
                        # Extract comprehensive paper information
                        paper_schema = ResearchPaper.model_json_schema()
                        result = nova.act(
                            f"""Extract comprehensive research paper information:
                            - Paper title
                            - List of authors
                            - Abstract or summary
                            - Publication year
                            - Journal or conference name
                            - DOI (if available)
                            - Citation count (if available)
                            - Keywords or tags
                            - Research area or field
                            
                            Use source: '{database_config['name']}' and current URL
                            """,
                            schema=paper_schema
                        )
                        
                        if result.matches_schema:
                            paper = ResearchPaper.model_validate(result.parsed_response)
                            paper.extracted_at = datetime.now().isoformat()
                            papers.append(paper)
                            print(f"✓ Extracted: {paper.title[:60]}...")
                        
                    except Exception as e:
                        print(f"Error extracting paper {i+1} from {database_config['name']}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error accessing {database_config['name']}: {e}")
        
        return papers
    
    def conduct_literature_review(self, query: ResearchQuery, databases: List[dict], max_workers: int = 2) -> List[ResearchPaper]:
        """Conduct literature review across multiple academic databases"""
        all_papers = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_db = {
                executor.submit(self.search_academic_database, db, query): db 
                for db in databases
            }
            
            for future in as_completed(future_to_db.keys()):
                db_config = future_to_db[future]
                try:
                    papers = future.result()
                    all_papers.extend(papers)
                    print(f"✓ {db_config['name']}: {len(papers)} papers")
                except Exception as e:
                    print(f"✗ Error with {db_config['name']}: {e}")
        
        # Remove duplicates based on title and DOI
        unique_papers = []
        seen_titles = set()
        seen_dois = set()
        
        for paper in all_papers:
            title_key = paper.title.lower().strip()
            doi_key = paper.doi.lower() if paper.doi else None
            
            if title_key not in seen_titles and (not doi_key or doi_key not in seen_dois):
                unique_papers.append(paper)
                seen_titles.add(title_key)
                if doi_key:
                    seen_dois.add(doi_key)
        
        self.research_papers.extend(unique_papers)
        return unique_papers
    
    def analyze_research_trends(self, papers: List[ResearchPaper]) -> Dict:
        """Analyze research trends from collected papers"""
        if not papers:
            return {"error": "No papers to analyze"}
        
        # Publication year trends
        year_distribution = {}
        for paper in papers:
            if paper.publication_year:
                year = str(paper.publication_year)
                year_distribution[year] = year_distribution.get(year, 0) + 1
        
        # Journal analysis
        journal_distribution = {}
        for paper in papers:
            if paper.journal:
                journal = paper.journal.lower()
                journal_distribution[journal] = journal_distribution.get(journal, 0) + 1
        
        top_journals = sorted(journal_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Keyword analysis
        keyword_frequency = {}
        for paper in papers:
            for keyword in paper.keywords:
                keyword_lower = keyword.lower()
                keyword_frequency[keyword_lower] = keyword_frequency.get(keyword_lower, 0) + 1
        
        trending_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Author analysis
        author_frequency = {}
        for paper in papers:
            for author in paper.authors:
                author_frequency[author] = author_frequency.get(author, 0) + 1
        
        prolific_authors = sorted(author_frequency.items(), key=lambda x: x[1], reverse=True)[:15]
        
        # Citation analysis
        citation_stats = {}
        citations = [p.citation_count for p in papers if p.citation_count is not None]
        if citations:
            citations.sort()
            citation_stats = {
                "total_papers_with_citations": len(citations),
                "average_citations": sum(citations) / len(citations),
                "median_citations": citations[len(citations)//2],
                "max_citations": max(citations),
                "min_citations": min(citations)
            }
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "total_papers_analyzed": len(papers),
            "publication_trends": {
                "year_distribution": year_distribution,
                "most_active_years": sorted(year_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "journal_analysis": {
                "total_journals": len(journal_distribution),
                "top_journals": [{"journal": journal.title(), "count": count} for journal, count in top_journals]
            },
            "keyword_trends": {
                "total_unique_keywords": len(keyword_frequency),
                "trending_keywords": [{"keyword": keyword.title(), "frequency": freq} for keyword, freq in trending_keywords]
            },
            "author_analysis": {
                "total_unique_authors": len(author_frequency),
                "prolific_authors": [{"author": author, "paper_count": count} for author, count in prolific_authors]
            },
            "citation_analysis": citation_stats
        }
    
    def generate_citations(self, papers: List[ResearchPaper], citation_style: str = "APA") -> List[Citation]:
        """Generate citations for research papers in specified format"""
        citations = []
        
        for paper in papers:
            try:
                with NovaAct(starting_page=paper.url) as nova:
                    # Generate citation
                    citation_schema = Citation.model_json_schema()
                    result = nova.act(
                        f"""Generate a {citation_style} format citation for this research paper.
                        Include title, authors, year, and journal information.
                        Format it according to {citation_style} style guidelines.
                        """,
                        schema=citation_schema
                    )
                    
                    if result.matches_schema:
                        citation = Citation.model_validate(result.parsed_response)
                        citation.citation_format = citation_style
                        citations.append(citation)
                        print(f"✓ Generated {citation_style} citation for: {paper.title[:50]}...")
                    
            except Exception as e:
                print(f"Error generating citation for {paper.title}: {e}")
                continue
        
        self.citations.extend(citations)
        return citations
    
    def find_highly_cited_papers(self, papers: List[ResearchPaper], min_citations: int = 50) -> List[ResearchPaper]:
        """Find highly cited papers from the collection"""
        highly_cited = []
        
        for paper in papers:
            if paper.citation_count and paper.citation_count >= min_citations:
                highly_cited.append(paper)
        
        # Sort by citation count (descending)
        highly_cited.sort(key=lambda x: x.citation_count or 0, reverse=True)
        
        return highly_cited
    
    def generate_research_report(self, query: ResearchQuery, papers: List[ResearchPaper]) -> Dict:
        """Generate comprehensive research report"""
        if not papers:
            return {"error": "No papers to analyze"}
        
        # Detailed analyses
        trend_analysis = self.analyze_research_trends(papers)
        highly_cited = self.find_highly_cited_papers(papers)
        
        # Research gap analysis (simplified)
        research_areas = {}
        for paper in papers:
            if paper.research_area:
                area = paper.research_area.lower()
                research_areas[area] = research_areas.get(area, 0) + 1
        
        # Source distribution
        source_distribution = {}
        for paper in papers:
            source_distribution[paper.source] = source_distribution.get(paper.source, 0) + 1
        
        return {
            "research_query": query.dict(),
            "analysis_date": datetime.now().isoformat(),
            "summary": {
                "total_papers_found": len(papers),
                "unique_sources": len(source_distribution),
                "date_range_covered": {
                    "earliest": min([p.publication_year for p in papers if p.publication_year], default=None),
                    "latest": max([p.publication_year for p in papers if p.publication_year], default=None)
                }
            },
            "source_distribution": source_distribution,
            "trend_analysis": trend_analysis,
            "highly_cited_papers": [
                {
                    "title": paper.title,
                    "authors": paper.authors,
                    "year": paper.publication_year,
                    "citations": paper.citation_count,
                    "journal": paper.journal,
                    "url": paper.url
                }
                for paper in highly_cited[:10]
            ],
            "research_areas": research_areas,
            "key_findings": {
                "most_productive_year": max(trend_analysis['publication_trends']['year_distribution'].items(), key=lambda x: x[1])[0] if trend_analysis['publication_trends']['year_distribution'] else None,
                "top_journal": trend_analysis['journal_analysis']['top_journals'][0]['journal'] if trend_analysis['journal_analysis']['top_journals'] else None,
                "most_common_keyword": trend_analysis['keyword_trends']['trending_keywords'][0]['keyword'] if trend_analysis['keyword_trends']['trending_keywords'] else None
            },
            "detailed_papers": [paper.dict() for paper in papers]
        }
    
    def save_research_report(self, report: Dict, filename: str = None):
        """Save research report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic = report['research_query']['topic'].replace(' ', '_').lower()
            filename = f"research_report_{topic}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Research report saved to {filename}")


def main():
    # Define academic databases to search
    academic_databases = [
        {
            'name': 'Google Scholar',
            'url': 'https://scholar.google.com'
        },
        {
            'name': 'PubMed',
            'url': 'https://pubmed.ncbi.nlm.nih.gov'
        },
        {
            'name': 'IEEE Xplore',
            'url': 'https://ieeexplore.ieee.org'
        }
    ]
    
    # Define research query
    research_query = ResearchQuery(
        topic="machine learning in healthcare",
        keywords=["artificial intelligence", "medical diagnosis", "deep learning"],
        year_range={"start": 2020, "end": 2024},
        research_area="Computer Science"
    )
    
    assistant = AcademicResearchAssistant()
    
    print(f"🔬 Conducting literature review on: {research_query.topic}")
    print(f"📚 Searching {len(academic_databases)} databases...")
    
    # Conduct literature review
    papers = assistant.conduct_literature_review(research_query, academic_databases)
    
    if papers:
        print(f"\n📊 Successfully found {len(papers)} unique research papers")
        
        # Generate comprehensive report
        report = assistant.generate_research_report(research_query, papers)
        
        # Display key insights
        print(f"\n📈 Research Summary:")
        print(f"  • Total Papers: {report['summary']['total_papers_found']}")
        print(f"  • Sources: {report['summary']['unique_sources']}")
        print(f"  • Date Range: {report['summary']['date_range_covered']['earliest']} - {report['summary']['date_range_covered']['latest']}")
        
        if report['key_findings']['most_productive_year']:
            print(f"  • Most Productive Year: {report['key_findings']['most_productive_year']}")
        
        if report['key_findings']['top_journal']:
            print(f"  • Top Journal: {report['key_findings']['top_journal']}")
        
        print(f"\n🔥 Trending Keywords:")
        for keyword in report['trend_analysis']['keyword_trends']['trending_keywords'][:5]:
            print(f"  • {keyword['keyword']}: {keyword['frequency']} papers")
        
        print(f"\n📰 Top Journals:")
        for journal in report['trend_analysis']['journal_analysis']['top_journals'][:3]:
            print(f"  • {journal['journal']}: {journal['count']} papers")
        
        if report['highly_cited_papers']:
            print(f"\n⭐ Highly Cited Papers:")
            for paper in report['highly_cited_papers'][:3]:
                print(f"  • {paper['title'][:60]}... ({paper['citations']} citations)")
        
        # Generate citations for top papers
        print(f"\n📝 Generating APA citations for top papers...")
        top_papers = papers[:5]  # Top 5 papers
        citations = assistant.generate_citations(top_papers, "APA")
        
        if citations:
            print(f"✅ Generated {len(citations)} citations")
        
        # Save detailed report
        assistant.save_research_report(report)
        
    else:
        print("❌ No papers found for the research query")


if __name__ == "__main__":
    main()
