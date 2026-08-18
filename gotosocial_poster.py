"""GoToSocial poster for sharing news articles - Faculty Edition."""
import requests
from typing import List, Dict, Optional
import config
import os
from faculty_db import FacultyDatabase

class GoToSocialPoster:
    """Post news articles to GoToSocial under faculty member accounts."""
    
    def __init__(self):
        self.instance_url = os.getenv('GOTOSOCIAL_URL', 'https://social.castalia.institute')
        self.db = FacultyDatabase()
        self.faculty_accounts = self._load_faculty_accounts()
        
        print(f"✅ GoToSocial posting configured for {len(self.faculty_accounts)} faculty members")
    
    def _load_faculty_accounts(self) -> Dict[str, Dict]:
        """Load faculty GoToSocial accounts from Supabase."""
        if not self.db.client:
            print("⚠️  No Supabase connection, faculty posting disabled")
            return {}
        
        try:
            # Query faculty with GoToSocial credentials
            response = self.db.client.table('faculty').select(
                'id, name, slug, gotosocial_handle, gotosocial_api_token, fediverse_enabled'
            ).eq('fediverse_enabled', True).execute()
            
            if not response.data:
                print("⚠️  No faculty with GoToSocial accounts configured")
                return {}
            
            # Build lookup dictionary by faculty ID
            accounts = {}
            for faculty in response.data:
                if faculty.get('gotosocial_api_token'):
                    accounts[faculty['id']] = {
                        'name': faculty['name'],
                        'slug': faculty['slug'],
                        'handle': faculty['gotosocial_handle'],
                        'token': faculty['gotosocial_api_token']
                    }
            
            print(f"📱 Loaded {len(accounts)} faculty GoToSocial accounts")
            for fac in accounts.values():
                print(f"   • @{fac['handle']} ({fac['name']})")
            
            return accounts
            
        except Exception as e:
            print(f"❌ Error loading faculty accounts: {e}")
            return {}
    
    def format_post(self, article: Dict, faculty_name: str, max_length: int = 500) -> str:
        """Format article as a social media post from faculty perspective."""
        title = article.get('title', 'Untitled')
        url = article.get('url', '')
        description = article.get('description', '')
        source = article.get('source', 'Unknown')
        
        # Get article type icon
        article_type = article.get('type', 'article')
        icons = {
            'github_trending': '🔥',
            'model_release': '🤖',
            'benchmark_update': '📊',
            'article': '📰'
        }
        icon = icons.get(article_type, '📄')
        
        # Build post with personal touch
        post = f"{icon} {title}\n\n"
        
        # Add description (truncated if needed)
        desc_max = max_length - len(post) - len(url) - 100  # Buffer for hashtags
        if description and desc_max > 50:
            if len(description) > desc_max:
                description = description[:desc_max-3] + "..."
            post += f"{description}\n\n"
        
        post += f"🔗 {url}\n\n"
        
        # Add hashtags from keywords
        keywords = article.get('metadata', {}).get('matched_keywords', [])
        if keywords:
            # Convert to hashtags (limit to 3, clean up)
            hashtags = ['#' + kw.replace(' ', '').replace('-', '').title() for kw in keywords[:3]]
            post += ' '.join(hashtags)
        
        return post
    
    def post_status(self, status_text: str, api_token: str, faculty_handle: str, visibility: str = 'public') -> Optional[Dict]:
        """Post a status to GoToSocial as a specific faculty member."""
        if not api_token:
            return None
        
        try:
            response = requests.post(
                f"{self.instance_url}/api/v1/statuses",
                headers={
                    'Authorization': f'Bearer {api_token}',
                    'Content-Type': 'application/json',
                },
                json={
                    'status': status_text,
                    'visibility': visibility,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status_url = data.get('url', '')
                print(f"   ✅ Posted as @{faculty_handle}: {status_url}")
                return data
            else:
                print(f"   ❌ API error for @{faculty_handle}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error posting as @{faculty_handle}: {e}")
            return None
    
    def post_articles(self, articles: List[Dict], max_posts_per_faculty: int = 3) -> Dict[str, int]:
        """Post articles under relevant faculty member accounts."""
        if not self.faculty_accounts:
            print("⚠️  No faculty accounts configured for posting")
            return {}
        
        print(f"\n📱 Posting articles to GoToSocial...")
        
        # Track posts per faculty
        faculty_post_counts = {fac_id: 0 for fac_id in self.faculty_accounts.keys()}
        total_posted = 0
        
        # Iterate through articles
        for article in articles:
            # Get interested faculty for this article
            interested_faculty = article.get('metadata', {}).get('interested_faculty', [])
            
            if not interested_faculty:
                continue
            
            # Get the top interested faculty member who has a GoToSocial account
            posted_by_faculty = []
            for faculty_info in interested_faculty:
                faculty_slug = faculty_info.get('slug', '')
                
                # Find matching faculty account
                faculty_account = None
                for fac_id, fac_data in self.faculty_accounts.items():
                    if fac_data['slug'] == faculty_slug:
                        faculty_account = (fac_id, fac_data)
                        break
                
                if not faculty_account:
                    continue
                
                fac_id, fac_data = faculty_account
                
                # Check if this faculty member hasn't posted too many already
                if faculty_post_counts[fac_id] >= max_posts_per_faculty:
                    continue
                
                # Format and post
                print(f"\n📄 {article.get('title', 'Untitled')[:60]}...")
                print(f"   Posting as: {fac_data['name']} (@{fac_data['handle']})")
                
                post_text = self.format_post(article, fac_data['name'])
                result = self.post_status(
                    post_text, 
                    fac_data['token'],
                    fac_data['handle']
                )
                
                if result:
                    faculty_post_counts[fac_id] += 1
                    total_posted += 1
                    posted_by_faculty.append(fac_data['name'])
                    
                    # Delay between posts
                    import time
                    time.sleep(2)
                    
                    # Only post once per article (by the most interested faculty)
                    break
        
        # Summary
        print(f"\n✅ Posted {total_posted} articles to GoToSocial")
        for fac_id, count in faculty_post_counts.items():
            if count > 0:
                fac_data = self.faculty_accounts[fac_id]
                print(f"   • @{fac_data['handle']}: {count} posts")
        
        return faculty_post_counts

if __name__ == '__main__':
    # Test with sample article
    test_article = {
        'type': 'article',
        'title': 'New Study on Electrical Engineering Applications in AI',
        'description': 'Researchers develop new framework combining electrical engineering principles with modern AI systems.',
        'url': 'https://example.com/article',
        'source': 'Engineering Weekly',
        'relevance_score': 0.95,
        'metadata': {
            'matched_keywords': ['electrical engineering', 'AI', 'systems'],
            'interested_faculty': [
                {'name': 'Nikola Tesla', 'slug': 'nikola-tesla'},
                {'name': 'Thomas Edison', 'slug': 'thomas-edison'}
            ]
        }
    }
    
    poster = GoToSocialPoster()
    if poster.faculty_accounts:
        post_text = poster.format_post(test_article, 'Nikola Tesla')
        print("\n" + "="*60)
        print("TEST POST (as Nikola Tesla):")
        print("="*60)
        print(post_text)
        print("="*60)
        print(f"\nPost length: {len(post_text)} characters")
    else:
        print("No faculty accounts configured. Run the SQL migration first.")
