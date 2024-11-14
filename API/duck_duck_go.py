from duckduckgo_search import DDGS # type: ignore
from scrape_details import scrape_url
def search_duckduckgo_news(query, max_results=10):
    with DDGS() as ddgs:
        results = ddgs.news(query, max_results=max_results)
        links = [result['url'] for result in results]
    return links

# Example usage
query = "btc sensational news today"
news_links = search_duckduckgo_news(query, max_results=10)
for idx, link in enumerate(news_links, 1):
    print(f"{idx}. {link}")
    print(scrape_url(link))