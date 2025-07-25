#!/usr/bin/env python3
"""
Job Market Analysis Sample

This sample demonstrates how to extract job postings from multiple job boards,
analyze market trends, salary ranges, and skill requirements.
"""

import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict

from nova_act import NovaAct


class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    salary_range: Optional[str]
    employment_type: Optional[str]  # full-time, part-time, contract
    experience_level: Optional[str]  # entry, mid, senior
    required_skills: List[str]
    job_description: str
    posted_date: Optional[str]
    source: str
    url: str
    extracted_at: str


class JobMarketAnalyzer:
    def __init__(self):
        self.job_postings = []
    
    def extract_jobs_from_site(self, site_config: dict, search_term: str, location: str, max_jobs: int = 10) -> List[JobPosting]:
        """Extract job postings from a single job board"""
        jobs = []
        
        try:
            with NovaAct(starting_page=site_config['url']) as nova:
                # Search for jobs
                nova.act(f"search for '{search_term}' jobs in '{location}'")
                
                # Extract multiple job postings
                for i in range(max_jobs):
                    try:
                        # Navigate to job posting
                        if i == 0:
                            nova.act("click on the first job posting")
                        else:
                            nova.act("go back to job search results")
                            nova.act(f"click on the {i+1}th job posting")
                        
                        # Extract job details
                        job_schema = JobPosting.model_json_schema()
                        result = nova.act(
                            f"""Extract comprehensive job posting information:
                            - Job title
                            - Company name
                            - Job location
                            - Salary range (if mentioned)
                            - Employment type (full-time, part-time, contract, etc.)
                            - Experience level required (entry, mid-level, senior, etc.)
                            - Required skills and technologies (list format)
                            - Brief job description (2-3 sentences)
                            - When the job was posted (if available)
                            
                            Use source: '{site_config['name']}' and current URL
                            """,
                            schema=job_schema
                        )
                        
                        if result.matches_schema:
                            job = JobPosting.model_validate(result.parsed_response)
                            job.extracted_at = datetime.now().isoformat()
                            jobs.append(job)
                            print(f"✓ Extracted: {job.title} at {job.company}")
                        
                    except Exception as e:
                        print(f"Error extracting job {i+1} from {site_config['name']}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error accessing {site_config['name']}: {e}")
        
        return jobs
    
    def analyze_job_market(self, search_term: str, location: str, job_sites: List[dict], max_workers: int = 3) -> List[JobPosting]:
        """Analyze job market across multiple job boards"""
        all_jobs = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_site = {
                executor.submit(self.extract_jobs_from_site, site, search_term, location): site 
                for site in job_sites
            }
            
            for future in as_completed(future_to_site.keys()):
                site_config = future_to_site[future]
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                    print(f"✓ {site_config['name']}: {len(jobs)} jobs")
                except Exception as e:
                    print(f"✗ Error with {site_config['name']}: {e}")
        
        self.job_postings.extend(all_jobs)
        return all_jobs
    
    def analyze_salary_trends(self, jobs: List[JobPosting]) -> Dict:
        """Analyze salary trends from job postings"""
        salary_data = []
        
        for job in jobs:
            if job.salary_range:
                # Extract numeric values from salary strings
                numbers = re.findall(r'\d+(?:,\d+)*', job.salary_range.replace('$', '').replace('k', '000'))
                if len(numbers) >= 2:
                    try:
                        min_salary = int(numbers[0].replace(',', ''))
                        max_salary = int(numbers[1].replace(',', ''))
                        salary_data.append({
                            'min': min_salary,
                            'max': max_salary,
                            'avg': (min_salary + max_salary) / 2,
                            'company': job.company,
                            'title': job.title
                        })
                    except ValueError:
                        continue
        
        if not salary_data:
            return {"error": "No salary data found"}
        
        avg_salaries = [s['avg'] for s in salary_data]
        min_salaries = [s['min'] for s in salary_data]
        max_salaries = [s['max'] for s in salary_data]
        
        return {
            "total_jobs_with_salary": len(salary_data),
            "average_salary_range": {
                "min": sum(min_salaries) / len(min_salaries),
                "max": sum(max_salaries) / len(max_salaries),
                "average": sum(avg_salaries) / len(avg_salaries)
            },
            "salary_distribution": {
                "lowest": min(min_salaries),
                "highest": max(max_salaries),
                "median": sorted(avg_salaries)[len(avg_salaries)//2]
            },
            "top_paying_companies": sorted(
                salary_data, key=lambda x: x['avg'], reverse=True
            )[:5]
        }
    
    def analyze_skill_demand(self, jobs: List[JobPosting]) -> List[Dict]:
        """Analyze most in-demand skills"""
        skill_frequency = {}
        
        for job in jobs:
            for skill in job.required_skills:
                skill_lower = skill.lower().strip()
                skill_frequency[skill_lower] = skill_frequency.get(skill_lower, 0) + 1
        
        # Sort by frequency
        top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "skill": skill.title(),
                "frequency": freq,
                "percentage": (freq / len(jobs) * 100)
            }
            for skill, freq in top_skills[:20]
        ]
    
    def analyze_company_trends(self, jobs: List[JobPosting]) -> Dict:
        """Analyze hiring trends by company"""
        company_stats = {}
        
        for job in jobs:
            if job.company not in company_stats:
                company_stats[job.company] = {
                    "job_count": 0,
                    "positions": [],
                    "locations": set(),
                    "employment_types": set()
                }
            
            company_stats[job.company]["job_count"] += 1
            company_stats[job.company]["positions"].append(job.title)
            company_stats[job.company]["locations"].add(job.location)
            if job.employment_type:
                company_stats[job.company]["employment_types"].add(job.employment_type)
        
        # Convert sets to lists for JSON serialization
        for company in company_stats:
            company_stats[company]["locations"] = list(company_stats[company]["locations"])
            company_stats[company]["employment_types"] = list(company_stats[company]["employment_types"])
        
        # Top hiring companies
        top_hiring = sorted(
            company_stats.items(), 
            key=lambda x: x[1]["job_count"], 
            reverse=True
        )[:10]
        
        return {
            "total_companies": len(company_stats),
            "top_hiring_companies": [
                {
                    "company": company,
                    "job_count": stats["job_count"],
                    "unique_positions": len(set(stats["positions"])),
                    "locations": stats["locations"]
                }
                for company, stats in top_hiring
            ],
            "detailed_company_stats": company_stats
        }
    
    def generate_market_report(self, search_term: str, location: str, jobs: List[JobPosting]) -> Dict:
        """Generate comprehensive job market analysis report"""
        if not jobs:
            return {"error": "No jobs to analyze"}
        
        # Basic statistics
        employment_types = {}
        experience_levels = {}
        sources = {}
        
        for job in jobs:
            if job.employment_type:
                employment_types[job.employment_type] = employment_types.get(job.employment_type, 0) + 1
            if job.experience_level:
                experience_levels[job.experience_level] = experience_levels.get(job.experience_level, 0) + 1
            sources[job.source] = sources.get(job.source, 0) + 1
        
        # Detailed analyses
        salary_analysis = self.analyze_salary_trends(jobs)
        skill_analysis = self.analyze_skill_demand(jobs)
        company_analysis = self.analyze_company_trends(jobs)
        
        return {
            "search_criteria": {
                "position": search_term,
                "location": location,
                "analysis_date": datetime.now().isoformat()
            },
            "summary": {
                "total_jobs_found": len(jobs),
                "sources_searched": len(sources),
                "companies_hiring": len(set(job.company for job in jobs))
            },
            "employment_type_distribution": employment_types,
            "experience_level_distribution": experience_levels,
            "source_distribution": sources,
            "salary_analysis": salary_analysis,
            "top_skills": skill_analysis[:15],
            "company_analysis": company_analysis,
            "sample_job_titles": list(set(job.title for job in jobs))[:10],
            "detailed_jobs": [job.dict() for job in jobs]
        }
    
    def save_report(self, report: Dict, filename: str = None):
        """Save job market report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            position = report['search_criteria']['position'].replace(' ', '_').lower()
            location = report['search_criteria']['location'].replace(' ', '_').lower()
            filename = f"job_market_{position}_{location}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Job market report saved to {filename}")


def main():
    # Define job boards to search
    job_sites = [
        {
            'name': 'Indeed',
            'url': 'https://www.indeed.com'
        },
        {
            'name': 'LinkedIn Jobs',
            'url': 'https://www.linkedin.com/jobs'
        },
        {
            'name': 'Glassdoor',
            'url': 'https://www.glassdoor.com/Jobs'
        }
    ]
    
    # Job search parameters
    search_term = "software engineer"
    location = "San Francisco, CA"
    
    analyzer = JobMarketAnalyzer()
    
    print(f"💼 Analyzing job market for '{search_term}' in '{location}'...")
    
    # Analyze job market
    jobs = analyzer.analyze_job_market(search_term, location, job_sites)
    
    if jobs:
        print(f"\n📊 Successfully analyzed {len(jobs)} job postings")
        
        # Generate comprehensive report
        report = analyzer.generate_market_report(search_term, location, jobs)
        
        # Display key insights
        print(f"\n📈 Market Summary:")
        print(f"  • Total Jobs: {report['summary']['total_jobs_found']}")
        print(f"  • Companies Hiring: {report['summary']['companies_hiring']}")
        print(f"  • Sources Searched: {report['summary']['sources_searched']}")
        
        if 'average_salary_range' in report['salary_analysis']:
            salary = report['salary_analysis']['average_salary_range']
            print(f"\n💰 Salary Analysis:")
            print(f"  • Average Range: ${salary['min']:,.0f} - ${salary['max']:,.0f}")
            print(f"  • Market Average: ${salary['average']:,.0f}")
        
        print(f"\n🔧 Top Skills in Demand:")
        for skill in report['top_skills'][:5]:
            print(f"  • {skill['skill']}: {skill['frequency']} jobs ({skill['percentage']:.1f}%)")
        
        print(f"\n🏢 Top Hiring Companies:")
        for company in report['company_analysis']['top_hiring_companies'][:5]:
            print(f"  • {company['company']}: {company['job_count']} positions")
        
        # Save detailed report
        analyzer.save_report(report)
        
    else:
        print("❌ No jobs found for analysis")


if __name__ == "__main__":
    main()
