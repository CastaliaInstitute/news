# Quick Start Guide

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/InquiryInstitute/news.git
cd news
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys (Optional)

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run First Aggregation

```bash
python aggregate.py
```

This will generate `news_data.json` with the latest curated content.
Until this first run completes, the frontend will show an empty state (no synthetic fallback data).

## 🔧 GitHub Actions Setup

The system automatically runs every 6 hours via GitHub Actions.

### Required Secrets

Go to your repository Settings → Secrets and variables → Actions:

1. **GH_TOKEN** (optional but recommended)
   - Create at: https://github.com/settings/tokens
   - Permissions needed: `public_repo`
   - Increases API rate limits for GitHub signal detection

2. **OPENAI_API_KEY** (optional)
   - For enhanced embeddings
   - System works with local embeddings if not provided

3. **NEWS_API_KEY** (optional)
   - Get free key at: https://newsapi.org/
   - Adds more news sources

4. **HF_TOKEN** (optional)
   - Create at: https://huggingface.co/settings/tokens
   - For Hugging Face model tracking

### Manual Workflow Trigger

You can manually trigger the aggregation:

1. Go to Actions tab
2. Select "News Aggregation" workflow
3. Click "Run workflow"

## 📱 View the Site

Your news aggregator is live at:
**https://inquiryinstitute.github.io/news/**

## 🎯 Testing Locally

### Test Signal Detection
```bash
python signal_detector.py
```

### Test News Ingestion
```bash
python ingestion.py
```

### Test Full Pipeline
```bash
python aggregate.py
```

### View Frontend Locally
```bash
# Simple Python server
python -m http.server 8000

# Then open: http://localhost:8000
```

## 🔧 Customization

### Add Faculty Keywords

Edit `config.py`:

```python
FACULTY_KEYWORDS = [
    'your-keyword',
    'another-topic',
    # Add more...
]
```

### Add News Sources

Edit `config.py`:

```python
RSS_FEEDS = [
    'https://your-source.com/rss',
    # Add more...
]
```

### Adjust Thresholds

Edit `config.py`:

```python
GITHUB_STAR_THRESHOLD = 1000  # Trending threshold
SIMILARITY_THRESHOLD = 0.85   # Duplicate detection
MAX_ARTICLES = 50             # Max to display
```

## 🐛 Troubleshooting

### "Rate limit exceeded" on GitHub API
- Add `GITHUB_TOKEN` to your secrets
- Reduce frequency in `.github/workflows/aggregate.yml`

### "No news available"
- Check if workflow has run (Actions tab)
- Verify API keys if using external sources
- Run manually: `python aggregate.py`

### Frontend shows old data
- GitHub Pages can take 1-2 minutes to update
- Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)

## 📊 Monitoring

Check workflow status:
1. Go to Actions tab
2. View recent runs
3. Check logs for errors

## 🤝 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review workflow logs in Actions tab
- Test components individually with test commands above
