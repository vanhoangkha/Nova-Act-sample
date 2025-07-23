#!/usr/bin/env python3
"""
Vietnam Job Market Analysis Sample

This sample demonstrates how to extract job postings from Vietnamese job boards
like TopCV, VietnamWorks, CareerBuilder, and ITviec.
"""

import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import List, Optional, Dict

from nova_act import NovaAct


class VietnamJobPosting(BaseModel):
    title: str
    company: str
    location: str
    salary_range: Optional[str]
    employment_type: Optional[str]  # toàn thời gian, bán thời gian, hợp đồng
    experience_level: Optional[str]  # mới ra trường, 1-3 năm, 3-5 năm, trên 5 năm
    required_skills: List[str]
    job_description: str
    benefits: List[str]
    posted_date: Optional[str]
    deadline: Optional[str]
    source: str
    url: str
    extracted_at: str


class VietnamJobMarketAnalyzer:
    def __init__(self):
        self.job_postings = []
    
    def extract_jobs_from_site(self, site_config: dict, search_term: str, location: str, max_jobs: int = 10) -> List[VietnamJobPosting]:
        """Extract job postings from a Vietnamese job board"""
        jobs = []
        
        try:
            with NovaAct(starting_page=site_config['url']) as nova:
                # Search for jobs in Vietnamese
                nova.act(f"tìm kiếm việc làm '{search_term}' tại '{location}'")
                
                # Extract multiple job postings
                for i in range(max_jobs):
                    try:
                        # Navigate to job posting
                        if i == 0:
                            nova.act("nhấp vào tin tuyển dụng đầu tiên")
                        else:
                            nova.act("quay lại trang kết quả tìm kiếm")
                            nova.act(f"nhấp vào tin tuyển dụng thứ {i+1}")
                        
                        # Extract job details
                        job_schema = VietnamJobPosting.model_json_schema()
                        result = nova.act(
                            f"""Trích xuất thông tin chi tiết về công việc:
                            - Tên vị trí tuyển dụng
                            - Tên công ty
                            - Địa điểm làm việc
                            - Mức lương (nếu có)
                            - Loại hình công việc (toàn thời gian, bán thời gian, hợp đồng, v.v.)
                            - Yêu cầu kinh nghiệm (mới ra trường, 1-3 năm, 3-5 năm, trên 5 năm)
                            - Kỹ năng yêu cầu (danh sách)
                            - Mô tả công việc (tóm tắt ngắn gọn)
                            - Quyền lợi và phúc lợi (danh sách)
                            - Ngày đăng tin
                            - Hạn nộp hồ sơ (nếu có)
                            
                            Sử dụng source: '{site_config['name']}' và URL hiện tại
                            """,
                            schema=job_schema
                        )
                        
                        if result.matches_schema:
                            job = VietnamJobPosting.model_validate(result.parsed_response)
                            job.extracted_at = datetime.now().isoformat()
                            jobs.append(job)
                            print(f"✓ Đã trích xuất: {job.title} tại {job.company}")
                        
                    except Exception as e:
                        print(f"Lỗi trích xuất công việc {i+1} từ {site_config['name']}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Lỗi truy cập {site_config['name']}: {e}")
        
        return jobs
    
    def analyze_vietnam_job_market(self, search_term: str, location: str, job_sites: List[dict], max_workers: int = 2) -> List[VietnamJobPosting]:
        """Analyze Vietnamese job market across multiple job boards"""
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
                    print(f"✓ {site_config['name']}: {len(jobs)} công việc")
                except Exception as e:
                    print(f"✗ Lỗi với {site_config['name']}: {e}")
        
        self.job_postings.extend(all_jobs)
        return all_jobs
    
    def analyze_vietnam_salary_trends(self, jobs: List[VietnamJobPosting]) -> Dict:
        """Analyze salary trends in Vietnamese job market"""
        salary_data = []
        
        for job in jobs:
            if job.salary_range:
                # Extract numeric values from Vietnamese salary strings
                # Handle formats like "10-15 triệu", "Thỏa thuận", "Từ 20 triệu"
                salary_text = job.salary_range.lower()
                
                # Convert "triệu" to millions, "nghìn" to thousands
                numbers = re.findall(r'\d+(?:\.\d+)?', salary_text)
                
                if numbers and ('triệu' in salary_text or 'tr' in salary_text):
                    try:
                        if len(numbers) >= 2:
                            min_salary = float(numbers[0]) * 1000000
                            max_salary = float(numbers[1]) * 1000000
                        elif 'từ' in salary_text or 'trên' in salary_text:
                            min_salary = float(numbers[0]) * 1000000
                            max_salary = min_salary * 1.5  # Estimate
                        else:
                            min_salary = max_salary = float(numbers[0]) * 1000000
                        
                        salary_data.append({
                            'min': min_salary,
                            'max': max_salary,
                            'avg': (min_salary + max_salary) / 2,
                            'company': job.company,
                            'title': job.title,
                            'location': job.location
                        })
                    except ValueError:
                        continue
        
        if not salary_data:
            return {"error": "Không tìm thấy dữ liệu lương"}
        
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
            )[:5],
            "salary_by_location": self._analyze_salary_by_location(salary_data)
        }
    
    def _analyze_salary_by_location(self, salary_data: List[dict]) -> Dict:
        """Analyze salary distribution by Vietnamese cities"""
        location_salaries = {}
        
        for salary in salary_data:
            location = salary['location']
            # Normalize location names
            if 'hồ chí minh' in location.lower() or 'tp.hcm' in location.lower() or 'sài gòn' in location.lower():
                location = 'TP. Hồ Chí Minh'
            elif 'hà nội' in location.lower():
                location = 'Hà Nội'
            elif 'đà nẵng' in location.lower():
                location = 'Đà Nẵng'
            elif 'cần thơ' in location.lower():
                location = 'Cần Thơ'
            
            if location not in location_salaries:
                location_salaries[location] = []
            location_salaries[location].append(salary['avg'])
        
        # Calculate averages by location
        location_averages = {}
        for location, salaries in location_salaries.items():
            location_averages[location] = {
                "average_salary": sum(salaries) / len(salaries),
                "job_count": len(salaries),
                "min_salary": min(salaries),
                "max_salary": max(salaries)
            }
        
        return location_averages
    
    def analyze_vietnam_skill_demand(self, jobs: List[VietnamJobPosting]) -> List[Dict]:
        """Analyze most in-demand skills in Vietnamese job market"""
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
    
    def analyze_vietnam_company_trends(self, jobs: List[VietnamJobPosting]) -> Dict:
        """Analyze hiring trends by Vietnamese companies"""
        company_stats = {}
        
        for job in jobs:
            if job.company not in company_stats:
                company_stats[job.company] = {
                    "job_count": 0,
                    "positions": [],
                    "locations": set(),
                    "benefits": []
                }
            
            company_stats[job.company]["job_count"] += 1
            company_stats[job.company]["positions"].append(job.title)
            company_stats[job.company]["locations"].add(job.location)
            company_stats[job.company]["benefits"].extend(job.benefits)
        
        # Convert sets to lists for JSON serialization
        for company in company_stats:
            company_stats[company]["locations"] = list(company_stats[company]["locations"])
            # Get unique benefits
            company_stats[company]["unique_benefits"] = list(set(company_stats[company]["benefits"]))
            del company_stats[company]["benefits"]
        
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
                    "locations": stats["locations"],
                    "top_benefits": stats["unique_benefits"][:5]
                }
                for company, stats in top_hiring
            ],
            "detailed_company_stats": company_stats
        }
    
    def generate_vietnam_market_report(self, search_term: str, location: str, jobs: List[VietnamJobPosting]) -> Dict:
        """Generate comprehensive Vietnamese job market analysis report"""
        if not jobs:
            return {"error": "Không có công việc để phân tích"}
        
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
        salary_analysis = self.analyze_vietnam_salary_trends(jobs)
        skill_analysis = self.analyze_vietnam_skill_demand(jobs)
        company_analysis = self.analyze_vietnam_company_trends(jobs)
        
        # Benefits analysis
        all_benefits = []
        for job in jobs:
            all_benefits.extend(job.benefits)
        
        benefit_frequency = {}
        for benefit in all_benefits:
            benefit_frequency[benefit] = benefit_frequency.get(benefit, 0) + 1
        
        top_benefits = sorted(benefit_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
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
            "top_benefits": [
                {"benefit": benefit, "frequency": freq, "percentage": (freq / len(jobs) * 100)}
                for benefit, freq in top_benefits
            ],
            "sample_job_titles": list(set(job.title for job in jobs))[:10],
            "market_insights": self._generate_market_insights(jobs),
            "detailed_jobs": [job.dict() for job in jobs]
        }
    
    def _generate_market_insights(self, jobs: List[VietnamJobPosting]) -> List[str]:
        """Generate market insights for Vietnamese job market"""
        insights = []
        
        if not jobs:
            return insights
        
        # Location insights
        locations = {}
        for job in jobs:
            locations[job.location] = locations.get(job.location, 0) + 1
        
        top_location = max(locations.items(), key=lambda x: x[1])
        insights.append(f"Thị trường việc làm tập trung nhất tại: {top_location[0]} với {top_location[1]} vị trí")
        
        # Experience insights
        experience_levels = {}
        for job in jobs:
            if job.experience_level:
                experience_levels[job.experience_level] = experience_levels.get(job.experience_level, 0) + 1
        
        if experience_levels:
            top_experience = max(experience_levels.items(), key=lambda x: x[1])
            insights.append(f"Yêu cầu kinh nghiệm phổ biến nhất: {top_experience[0]} ({top_experience[1]} vị trí)")
        
        # Company size insights
        company_job_counts = {}
        for job in jobs:
            company_job_counts[job.company] = company_job_counts.get(job.company, 0) + 1
        
        active_companies = len([c for c, count in company_job_counts.items() if count >= 2])
        insights.append(f"Có {active_companies} công ty đang tuyển dụng tích cực (≥2 vị trí)")
        
        return insights
    
    def save_report(self, report: Dict, filename: str = None):
        """Save Vietnamese job market report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            position = report['search_criteria']['position'].replace(' ', '_').lower()
            location = report['search_criteria']['location'].replace(' ', '_').lower()
            filename = f"vietnam_job_market_{position}_{location}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Báo cáo thị trường việc làm đã được lưu vào {filename}")


def main():
    # Vietnamese job boards to search
    vietnam_job_sites = [
        {
            'name': 'TopCV',
            'url': 'https://www.topcv.vn'
        },
        {
            'name': 'VietnamWorks',
            'url': 'https://www.vietnamworks.com'
        },
        {
            'name': 'CareerBuilder',
            'url': 'https://careerbuilder.vn'
        },
        {
            'name': 'ITviec',
            'url': 'https://itviec.com'
        }
    ]
    
    # Job search parameters
    search_term = "lập trình viên"
    location = "Hồ Chí Minh"
    
    analyzer = VietnamJobMarketAnalyzer()
    
    print(f"💼 Phân tích thị trường việc làm cho '{search_term}' tại '{location}'...")
    
    # Analyze Vietnamese job market
    jobs = analyzer.analyze_vietnam_job_market(search_term, location, vietnam_job_sites)
    
    if jobs:
        print(f"\n📊 Đã phân tích thành công {len(jobs)} tin tuyển dụng")
        
        # Generate comprehensive report
        report = analyzer.generate_vietnam_market_report(search_term, location, jobs)
        
        # Display key insights
        print(f"\n📈 Tóm tắt thị trường:")
        print(f"  • Tổng số việc làm: {report['summary']['total_jobs_found']}")
        print(f"  • Công ty đang tuyển: {report['summary']['companies_hiring']}")
        print(f"  • Nguồn tìm kiếm: {report['summary']['sources_searched']}")
        
        if 'average_salary_range' in report['salary_analysis']:
            salary = report['salary_analysis']['average_salary_range']
            print(f"\n💰 Phân tích lương:")
            print(f"  • Khoảng lương trung bình: {salary['min']/1000000:.1f} - {salary['max']/1000000:.1f} triệu VND")
            print(f"  • Lương trung bình thị trường: {salary['average']/1000000:.1f} triệu VND")
        
        print(f"\n🔧 Kỹ năng được yêu cầu nhiều nhất:")
        for skill in report['top_skills'][:5]:
            print(f"  • {skill['skill']}: {skill['frequency']} việc làm ({skill['percentage']:.1f}%)")
        
        print(f"\n🏢 Công ty tuyển dụng tích cực:")
        for company in report['company_analysis']['top_hiring_companies'][:5]:
            print(f"  • {company['company']}: {company['job_count']} vị trí")
        
        if 'market_insights' in report:
            print(f"\n💡 Thông tin thị trường:")
            for insight in report['market_insights']:
                print(f"  • {insight}")
        
        # Save detailed report
        analyzer.save_report(report)
        
    else:
        print("❌ Không tìm thấy việc làm để phân tích")


if __name__ == "__main__":
    main()
