"""Configuration for the news aggregator system."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
HF_TOKEN = os.getenv('HF_TOKEN', '')

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Signal Detection Thresholds
GITHUB_STAR_THRESHOLD = 1000  # Stars gained in 24h
GITHUB_TRENDING_HOURS = 24

# News Sources - RSS Feeds
RSS_FEEDS = [
    'https://news.ycombinator.com/rss',
    'https://arxiv.org/rss/cs.AI',
    'https://arxiv.org/rss/cs.LG',
    'https://www.reddit.com/r/MachineLearning/.rss',
    'https://blog.google/technology/ai/rss/',
    'https://openai.com/blog/rss.xml',
]

# AI Benchmark Sources
BENCHMARK_SOURCES = [
    'https://paperswithcode.com',
    'https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard',
]

# Default Faculty Interest Keywords (fallback if Supabase unavailable)
DEFAULT_FACULTY_KEYWORDS = [
    'critical thinking',
    'education',
    'inquiry-based learning',
    'research methodology',
    'scientific method',
    'media literacy',
    'cognitive science',
    'reasoning',
    'argumentation',
    'epistemology',
    'pedagogy',
    'assessment',
    'learning sciences',
]

# Duplicate Detection
SIMILARITY_THRESHOLD = 0.85  # Cosine similarity threshold for duplicates

# Output
OUTPUT_FILE = 'news_data.json'
# Hourly publication favors a smaller, editorially reviewed-feeling feed.
MAX_ARTICLES = int(os.getenv('MAX_ARTICLES', '10'))
MAX_FACULTY_SUMMARIES = int(os.getenv('MAX_FACULTY_SUMMARIES', '10'))

# Faculty Posting
INTEREST_THRESHOLD = 0.3  # Minimum interest score for faculty to post (0.0-1.0)
MAX_POSTS_PER_FACULTY = 3  # Maximum posts per faculty per run
