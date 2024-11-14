import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore

def scrape_url( url ):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Trigger error if status code isn't 200
        if response.headers['Content-Type'].startswith('application/pdf'):
            # Skip PDFs or handle them separately
            return "PDF content found; processing skipped."
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text() for p in paragraphs])
        return content.strip()
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching {url}: {e}"
