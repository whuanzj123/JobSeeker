import httpx
from pathlib import Path
import json
from datetime import datetime
import time
import logging
from urllib.robotparser import RobotFileParser
from typing import Dict, Optional

class ByteDanceCrawler:
    def __init__(self, base_url="https://jobs.bytedance.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/search/job/posts"
        self.robots_url = f"{base_url}/robots.txt"
        self.rp = RobotFileParser()
        self.output_dir = Path("bytedance_jobs")
        self.session = httpx.Client(
            timeout=10.0,
            follow_redirects=True,
            headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Origin": "https://jobs.bytedance.com",
                "Referer": "https://jobs.bytedance.com/experienced/position",
                "Portal-Channel": "office",
                "Portal-Platform": "pc",
                "Cookie": "locale=zh-CN; channel=office; platform=pc"
            }
        )
        self.setup_logging()
        self.setup_storage()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_storage(self):
        """Create necessary directories if they don't exist"""
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "json").mkdir(exist_ok=True)
        (self.output_dir / "data").mkdir(exist_ok=True)

    def check_robots_txt(self):
        """Check if crawling is allowed according to robots.txt"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.robots_url)
                if response.status_code == 200:
                    self.rp.parse(response.text.splitlines())
                    self.logger.info("Successfully parsed robots.txt")
                    return True
                else:
                    self.logger.warning(f"Failed to fetch robots.txt: {response.status_code}")
                    return False
        except Exception as e:
            self.logger.error(f"Error checking robots.txt: {str(e)}")
            return False

    def can_fetch(self, url):
        """Check if the URL can be fetched according to robots.txt"""
        return self.rp.can_fetch("*", url)

    def fetch_jobs(self, keyword: str, limit: int = 10, offset: int = 0) -> Optional[Dict]:
        """Fetch jobs from ByteDance API"""
        if not self.can_fetch(self.api_url):
            self.logger.warning(f"Crawling not allowed for API URL: {self.api_url}")
            return None

        try:
            # First, get the main page to establish a session
            initial_response = self.session.get(f"{self.base_url}/experienced/position")
            if initial_response.status_code != 200:
                self.logger.error(f"Failed to access main page: {initial_response.status_code}")
                return None

            # Prepare API request
            payload = {
                "keyword": keyword,
                "limit": limit,
                "offset": offset,
                "job_category_id_list": [],
                "tag_id_list": [],
                "location_code_list": [],
                "subject_id_list": [],
                "recruitment_id_list": [],
                "portal_type": 2,
                "job_function_id_list": [],
                "storefront_id_list": [],
                "portal_entrance": 1
            }

            # Use GET method with params instead of POST
            params = {
                "keyword": keyword,
                "limit": limit,
                "offset": offset,
                "job_category_id_list": "",
                "tag_id_list": "",
                "location_code_list": "",
                "subject_id_list": "",
                "recruitment_id_list": "",
                "portal_type": "2",
                "job_function_id_list": "",
                "portal_entrance": "1"
            }

            # Make the API request
            response = self.session.get(
                self.api_url,
                params=params
            )

            self.logger.debug(f"Request URL: {response.url}")
            self.logger.debug(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                json_data = response.json()
                
                # Save raw JSON response
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"bytedance_jobs_{timestamp}.json"
                json_path = self.output_dir / "json" / json_filename
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"Successfully fetched and saved jobs to {json_filename}")
                
                # Process and save structured data
                if 'data' in json_data and 'job_post_list' in json_data['data']:
                    processed_data = []
                    for job in json_data['data']['job_post_list']:
                        processed_job = {
                            'job_id': job.get('id'),
                            'code': job.get('code'),
                            'title': job.get('title'),
                            'description': job.get('description'),
                            'requirement': job.get('requirement'),
                            'category': job.get('job_category', {}).get('name'),
                            'location': job.get('city_info', {}).get('name'),
                            'recruit_type': job.get('recruit_type', {}).get('name'),
                            'posting_date': datetime.fromtimestamp(job.get('publish_time', 0)/1000).strftime('%Y-%m-%d %H:%M:%S') if job.get('publish_time') else None,
                            'link': f"{self.base_url}/experienced/position/{job.get('code')}"
                        }
                        processed_data.append(processed_job)
                    
                    # Save processed data
                    processed_filename = f"processed_jobs_{timestamp}.json"
                    processed_path = self.output_dir / "data" / processed_filename
                    with open(processed_path, 'w', encoding='utf-8') as f:
                        json.dump(processed_data, f, ensure_ascii=False, indent=2)
                    
                    self.logger.info(f"Successfully processed and saved structured data to {processed_filename}")
                    return processed_data
                else:
                    self.logger.error("Unexpected JSON structure in response")
                    return None
            else:
                self.logger.error(f"Failed to fetch jobs: {response.status_code}")
                self.logger.debug(f"Response Content: {response.text}")
                return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching jobs: {str(e)}")
            return None
        if not self.can_fetch(self.api_url):
            self.logger.warning(f"Crawling not allowed for API URL: {self.api_url}")
            return None

        payload = {
            "keyword": keyword,
            "limit": limit,
            "offset": offset,
            "job_category_id_list": [],
            "tag_id_list": [],
            "location_code_list": [],
            "subject_id_list": [],
            "recruitment_id_list": [],
            "portal_type": 2,
            "job_function_id_list": [],
            "storefront_id_list": [],
            "portal_entrance": 1
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                # Debug logging
                self.logger.debug(f"Request URL: {self.api_url}")
                self.logger.debug(f"Request Headers: {self.headers}")
                self.logger.debug(f"Request Payload: {payload}")
                
                response = client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    follow_redirects=True
                )
                
                self.logger.debug(f"Response Status: {response.status_code}")
                self.logger.debug(f"Response Headers: {dict(response.headers)}")
                if response.status_code != 200:
                    self.logger.debug(f"Response Content: {response.text}")
                
                if response.status_code == 200:
                    # Save raw JSON response
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_filename = f"bytedance_jobs_{timestamp}.json"
                    json_path = self.output_dir / "json" / json_filename
                    
                    json_data = response.json()
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    
                    self.logger.info(f"Successfully fetched and saved jobs to {json_filename}")
                    
                    # Process and save structured data
                    if 'data' in json_data and 'job_post_list' in json_data['data']:
                        processed_data = []
                        for job in json_data['data']['job_post_list']:
                            processed_job = {
                                'job_id': job.get('id'),
                                'code': job.get('code'),
                                'title': job.get('title'),
                                'description': job.get('description'),
                                'requirement': job.get('requirement'),
                                'category': job.get('job_category', {}).get('name'),
                                'location': job.get('city_info', {}).get('name'),
                                'recruit_type': job.get('recruit_type', {}).get('name'),
                                'posting_date': datetime.fromtimestamp(job.get('publish_time', 0)/1000).strftime('%Y-%m-%d %H:%M:%S') if job.get('publish_time') else None,
                                'link': f"{self.base_url}/experienced/position/{job.get('code')}"
                            }
                            processed_data.append(processed_job)
                        
                        # Save processed data
                        processed_filename = f"processed_jobs_{timestamp}.json"
                        processed_path = self.output_dir / "data" / processed_filename
                        with open(processed_path, 'w', encoding='utf-8') as f:
                            json.dump(processed_data, f, ensure_ascii=False, indent=2)
                        
                        self.logger.info(f"Successfully processed and saved structured data to {processed_filename}")
                        return processed_data
                    else:
                        self.logger.error("Unexpected JSON structure in response")
                        return None
                else:
                    self.logger.error(f"Failed to fetch jobs: {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching jobs: {str(e)}")
            return None

def main():
    # Initialize crawler
    crawler = ByteDanceCrawler()
    
    # Check robots.txt first
    if not crawler.check_robots_txt():
        crawler.logger.error("Failed to verify robots.txt. Exiting...")
        return

    # Fetch Python jobs
    jobs = crawler.fetch_jobs(keyword="python", limit=10, offset=0)
    
    if jobs:
        print(f"\nFound {len(jobs)} jobs:")
        for job in jobs:
            print(f"\nTitle: {job['title']}")
            print(f"Location: {job['location']}")
            print(f"Link: {job['link']}")
            print("-" * 80)

if __name__ == "__main__":
    main()