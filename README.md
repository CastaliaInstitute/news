# Inquiry Institute News Aggregator

A modern, AI-powered news aggregator for the Inquiry Institute, designed to curate and display news and insights related to critical thinking, education, research, and inquiry-based learning.

## 🚀 Features

### Signal Detection
- **GitHub Trending**: Tracks repos with >1k stars in 24h
- **Model Releases**: Monitors new AI models on Hugging Face
- **Benchmark Updates**: Detects new benchmark leaders

### Smart Content Selection
- **Multi-source Ingestion**: RSS feeds, NewsAPI, arXiv, Hacker News, Reddit
- **Duplicate Detection**: Clusters similar stories using TF-IDF and cosine similarity
- **RAG-based Filtering**: Scores articles for faculty relevance using Supabase faculty interests
- **Faculty Tracking**: Identifies which faculty members might be interested in each article
- **Automated Updates**: GitHub Actions runs every 6 hours
- **Social Media Posting**: Automatically posts top 5 articles to social.inquiry.institute (GoToSocial)

## 📋 Architecture

```
aggregate.py (main orchestrator)
    ├── signal_detector.py    # AI signals (GitHub, HuggingFace, benchmarks)
    ├── ingestion.py          # News from RSS feeds and APIs
    ├── clustering.py         # Deduplication using TF-IDF
    └── rag.py                # Faculty-relevance scoring
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

**Required**:
- `SUPABASE_URL`: Supabase project URL (for faculty interests)
- `SUPABASE_KEY`: Supabase anon key (for faculty interests)
- `GOTOSOCIAL_API_TOKEN`: GoToSocial API token (for posting to social.inquiry.institute)

**Optional** API keys (system works without them but with limited features):
- `GITHUB_TOKEN`: Increases API rate limits
- `OPENAI_API_KEY`: For enhanced embeddings (uses local otherwise)
- `NEWS_API_KEY`: For NewsAPI.org integration
- `HF_TOKEN`: For Hugging Face API access

### 3. Run Locally

```bash
python aggregate.py
```

This will:
1. Detect AI signals (GitHub trends, new models, benchmarks)
2. Ingest news from RSS feeds
3. Deduplicate similar articles
4. Score by faculty relevance
5. Save top 50 items to `news_data.json`
6. Post top 5 articles to social.inquiry.institute

> The frontend now uses live pipeline output only. If `news_data.json` has no items yet,
> the site shows an empty-state message instead of synthetic placeholder articles.

## 📊 Customization

### Faculty Interests (Dynamic via Supabase)

Faculty members can update their news interests directly in the Supabase `faculty` table:

```sql
UPDATE faculty 
SET news_topics = ARRAY['AI', 'philosophy', 'quantum computing', 'education']
WHERE id = 'faculty_id';
```

The system automatically pulls all unique topics from faculty members and uses them for relevance scoring.

### Fallback Keywords

If Supabase is unavailable, the system falls back to default keywords in `config.py`:

```python
DEFAULT_FACULTY_KEYWORDS = [
    'critical thinking',
    'education',
    # Add more fallbacks...
]
```

### News Sources

Add RSS feeds in `config.py`:

```python
RSS_FEEDS = [
    'https://your-source.com/rss',
    # Add more feeds...
]
```

### Thresholds

Adjust detection thresholds:

```python
GITHUB_STAR_THRESHOLD = 1000      # Stars in 24h
SIMILARITY_THRESHOLD = 0.85       # Duplicate detection
MAX_ARTICLES = 50                 # Max articles to display
```

## 🤖 Automated Updates

The system uses GitHub Actions to run every 6 hours:

1. Fetches latest news and signals
2. Processes and scores content
3. Updates `news_data.json`
4. Commits and pushes changes
5. GitHub Pages automatically deploys

### Required GitHub Secrets

Add these in your repository settings:

- `SUPABASE_URL`: Supabase project URL (required)
- `SUPABASE_KEY`: Supabase anon key (required)
- `GOTOSOCIAL_API_TOKEN`: GoToSocial API token (required - for social posting)
- `GH_TOKEN`: GitHub Personal Access Token (optional)
- `OPENAI_API_KEY`: (optional)
- `NEWS_API_KEY`: (optional)
- `HF_TOKEN`: (optional)

#### Getting GoToSocial API Token

1. Go to https://social.inquiry.institute/settings/applications
2. Click "New Application"
3. Name: "Inquiry Institute News Aggregator"
4. Scopes: `write:statuses`
5. Copy the access token
6. Add to GitHub Secrets as `GOTOSOCIAL_API_TOKEN`

## 🌐 Deployment

This site is hosted on GitHub Pages at: https://inquiryinstitute.github.io/news/

The frontend automatically loads from `news_data.json` and displays:
- 🔥 Trending GitHub repos
- 🤖 New model releases
- 📊 Benchmark updates
- 📰 Relevant articles

## 🎨 Frontend Features

- Responsive grid layout
- Type-specific icons and colors
- Relevance score badges
- Matched keyword tags
- Smooth animations
- Mobile-friendly design

## 📈 System Flow

```
Every 6 hours:
  ↓
GitHub Actions triggers
  ↓
Run aggregate.py
  ↓
├─ Detect signals (GitHub, HF, benchmarks)
├─ Ingest news (RSS, APIs)
├─ Deduplicate (clustering)
└─ Score relevance (RAG)
  ↓
Save news_data.json
  ↓
Commit & push
  ↓
GitHub Pages deploys
  ↓
Frontend updates automatically
```

## 🧪 Testing

Test individual components:

```bash
# Test signal detection
python signal_detector.py

# Test ingestion
python ingestion.py

# Test clustering
python clustering.py

# Test RAG scoring
python rag.py
```

## 📝 License

© 2026 Inquiry Institute. All rights reserved.

## 🤝 Contributing

To add new signal detectors or news sources:

1. Add detector class in `signal_detector.py` or source in `ingestion.py`
2. Update `config.py` with new parameters
3. Test locally with `python aggregate.py`
4. Commit and push changes

---

**Built with**: Python, scikit-learn, Beautiful Soup, feedparser, GitHub Actions
