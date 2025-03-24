# scraper_jobcount.py
import requests
from bs4 import BeautifulSoup
import re

def scrape_job_count():
    """
    Scrapes the job count from allgovernmentjobs.in by finding the element with class "jobcount".
    Returns the count as a string, or None if not found.
    """
    url = "https://allgovernmentjobs.in/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print("Failed to retrieve job count page")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        # Look for the element with class "jobcount"
        job_count_elem = soup.find(class_="jobcount")
        if job_count_elem:
            text = job_count_elem.get_text(strip=True)
            # Example: "298 Notifications and 123,387 Jobs Available"
            # Use regex to extract the portion that includes the number and the word "Jobs"
            match = re.search(r'([\d,]+)\s+Jobs', text)
            if match:
                return match.group(1) + " Jobs"
            return text  # fallback if regex doesn't match
        return None
    except Exception as e:
        print(f"Error scraping job count: {e}")
        return None
