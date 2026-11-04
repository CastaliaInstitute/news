"""News ingestion pipeline from multiple sources."""
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import config

class NewsIngestion:
    """Ingest news from RSS feeds and APIs."""
    
    def __init__(self):
        self.articles = []
    
    def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch articles from RSS feeds."""
        articles = []
        
        for feed_url in config.RSS_FEEDS:
            try:
                print(f"📰 Fetching: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Limit per feed
                    published = entry.get('published_parsed', entry.get('updated_parsed'))
                    if published:
                        pub_date = datetime(*published[:6])
                    else:
                        pub_date = datetime.now()
                    
                    # Only include articles from last 7 days
                    if datetime.now() - pub_date > timedelta(days=7):
                        continue
                    
                    raw_summary = entry.get('summary', '')
                    articles.append({
                        'type': 'article',
                        'title': entry.get('title', 'No title'),
                        # Keep cards concise while retaining enough source text for
                        # the faculty analysis to be genuinely substantive.
                        'description': self._clean_description(raw_summary),
                        'url': entry.get('link', ''),
                        'source': self._extract_source(feed_url),
                        'date': pub_date.isoformat(),
                        'metadata': {
                            'feed_url': feed_url,
                            'author': entry.get('author', ''),
                            'source_excerpt': self._clean_description(raw_summary, limit=6000),
                        }
                    })
                    
            except Exception as e:
                print(f"❌ Error fetching {feed_url}: {e}")
        
        return articles
    
    def _clean_description(self, text: str, limit: int = 300) -> str:
        """Clean HTML and limit text to the requested publication length."""
        from bs4 import BeautifulSoup
        
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        
        # Limit length
        if len(clean_text) > limit:
            clean_text = clean_text[:limit - 3] + '...'
        
        return clean_text.strip()
    
    def _extract_source(self, feed_url: str) -> str:
        """Extract source name from feed URL."""
        if 'arxiv.org' in feed_url:
            return 'arXiv'
        elif 'ycombinator' in feed_url:
            return 'Hacker News'
        elif 'reddit.com' in feed_url:
            return 'Reddit ML'
        elif 'google' in feed_url:
            return 'Google AI Blog'
        elif 'openai' in feed_url:
            return 'OpenAI'
        else:
            return 'News'
    
    def fetch_news_api(self) -> List[Dict]:
        """Fetch from NewsAPI.org if API key is available."""
        articles = []
        
        if not config.NEWS_API_KEY:
            return articles
        
        try:
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': 'artificial intelligence OR machine learning OR AI',
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 20,
                'apiKey': config.NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', []):
                    articles.append({
                        'type': 'article',
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'News'),
                        'date': article.get('publishedAt', datetime.now().isoformat()),
                        'metadata': {
                            'author': article.get('author', ''),
                            'image': article.get('urlToImage', ''),
                            'source_excerpt': article.get('content') or article.get('description', ''),
                        }
                    })
        except Exception as e:
            print(f"❌ Error fetching NewsAPI: {e}")
        
        return articles

def ingest_all_news() -> List[Dict]:
    """Ingest news from all sources."""
    ingestion = NewsIngestion()
    
    print("\n📥 Ingesting news from RSS feeds...")
    articles = ingestion.fetch_rss_feeds()
    
    print("📥 Ingesting from NewsAPI...")
    articles.extend(ingestion.fetch_news_api())
    
    return articles

if __name__ == '__main__':
    articles = ingest_all_news()
    print(f"\n✅ Ingested {len(articles)} articles")
