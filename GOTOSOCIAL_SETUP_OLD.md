# GoToSocial Integration for News Aggregator

## ✅ Setup Complete

The news aggregator now automatically posts top articles to **social.castalia.institute** (GoToSocial/Mastodon instance)!

## 🔑 Required: Get GoToSocial API Token

### Step 1: Create Application Token

1. Go to: https://social.castalia.institute/settings/applications
2. Log in with your Inquiry Institute credentials
3. Click **"New Application"**
4. Fill in details:
   - **Name**: `Inquiry Institute News Aggregator`
   - **Scopes**: Check `write:statuses`
   - **Redirect URI**: (leave default)
5. Click **"Submit"**
6. Copy the **Access Token** (you'll only see it once!)

### Step 2: Add to GitHub Secrets

```bash
gh secret set GOTOSOCIAL_API_TOKEN --body "YOUR_TOKEN_HERE" --repo InquiryInstitute/news
```

Or manually:
1. Go to: https://github.com/InquiryInstitute/news/settings/secrets/actions
2. Click "New repository secret"
3. Name: `GOTOSOCIAL_API_TOKEN`
4. Value: (paste your token)
5. Click "Add secret"

## 📱 What Gets Posted

Every 6 hours, the aggregator automatically posts the **top 5 articles** to social.castalia.institute:

### Post Format

```
🔥 Trending: AI/awesome-research-tool

A comprehensive framework for conducting AI safety research with
automated testing and evaluation...

🔗 https://github.com/example/awesome-research-tool

👥 Relevant for: Stuart Russell, Nick Bostrom, Eliezer Yudkowsky

#InquiryInstitute #News #AI #safety #research
```

### Features

- **Type Icons**: 🔥 GitHub trending, 🤖 model releases, 📊 benchmarks, 📰 articles
- **Faculty Mentions**: Shows which faculty members are interested
- **Smart Hashtags**: Automatically generated from matched keywords
- **URL Included**: Direct link to original source
- **Character Limit**: Respects 500-character limit

## 🔧 Configuration

### Environment Variables

```bash
# Required
GOTOSOCIAL_API_TOKEN=your_token_here
GOTOSOCIAL_URL=https://social.castalia.institute  # default

# Optional (for local testing)
# Set in .env file
```

### Posting Settings

Edit `gotosocial_poster.py` to customize:

```python
# Number of articles to post per run
max_posts = 5  # Default: top 5 articles

# Character limit
max_length = 500  # Mastodon/GoToSocial standard

# Visibility
visibility = 'public'  # Options: public, unlisted, private, direct
```

## 🧪 Testing Locally

```bash
# Set your API token
export GOTOSOCIAL_API_TOKEN="your_token_here"

# Test the poster
python gotosocial_poster.py

# Run full aggregation (will post to social.castalia.institute!)
python aggregate.py
```

## 📊 Post Content

### Article Metadata Used

- `title`: Main headline
- `description`: Article summary (truncated to fit)
- `url`: Link to original article
- `source`: Publication source
- `type`: Article type (determines icon)
- `relevance_score`: Faculty relevance (not shown in post)
- `metadata.interested_faculty`: Faculty member mentions
- `metadata.matched_keywords`: Converted to hashtags

### Example Post Data

```json
{
  "title": "Critical Thinking in AI Education",
  "description": "New framework for teaching...",
  "url": "https://example.com/article",
  "type": "article",
  "source": "Education Weekly",
  "relevance_score": 0.95,
  "metadata": {
    "interested_faculty": [
      {"name": "John Dewey", "slug": "john-dewey"}
    ],
    "matched_keywords": ["critical thinking", "education", "AI"]
  }
}
```

## 🔄 Automation Flow

```
Every 6 hours (GitHub Actions)
         ↓
Aggregate news (top 50 articles)
         ↓
Select top 5 by relevance score
         ↓
Format each as GoToSocial post
         ↓
Post to social.castalia.institute
         ↓
2-second delay between posts
         ↓
Commit news_data.json
         ↓
GitHub Pages deploys
```

## 🛡️ Rate Limiting

- **Posts per run**: 5 (to respect API limits)
- **Delay between posts**: 2 seconds
- **Frequency**: Every 6 hours (4 runs/day = 20 posts/day)
- **GoToSocial limit**: Typically 300 posts/hour (we're well under)

## 🎯 Faculty Attribution

Posts automatically mention interested faculty:

```
👥 Relevant for: Socrates, Plato, Aristotle
```

This is based on the `news_topics` in the faculty table:

```sql
-- Faculty with news interests will be mentioned
SELECT name, news_topics FROM faculty 
WHERE news_topics IS NOT NULL 
AND array_length(news_topics, 1) > 0;
```

## 📈 Monitoring

### Check Posted Articles

Visit: https://social.castalia.institute/@inquiryinstitute

### GitHub Actions Logs

```bash
# View workflow runs
gh run list --repo InquiryInstitute/news

# View specific run logs
gh run view <run-id> --repo InquiryInstitute/news --log
```

Look for:
- `✅ Posted to GoToSocial: <status URL>`
- `Posted 5/5 articles to GoToSocial`

### Troubleshooting

**"GoToSocial posting disabled"**
- Set `GOTOSOCIAL_API_TOKEN` in GitHub Secrets

**"GoToSocial API error: 401"**
- Token expired or invalid - regenerate token

**"GoToSocial API error: 422"**
- Post content invalid (usually too long or bad characters)

**"Posted 0/5 articles"**
- Check GitHub Actions logs for specific errors
- Verify token has `write:statuses` scope

## 🔐 Security

- API token stored securely in GitHub Secrets
- Token has limited scope (`write:statuses` only)
- Can't delete posts or modify account settings
- Revoke token anytime at: https://social.castalia.institute/settings/applications

## 🎨 Customization Ideas

### Add Images

```python
# In gotosocial_poster.py
# Upload media first, then attach to status
media_ids = upload_media(article['image_url'])
post_data = {
    'status': status_text,
    'media_ids': media_ids
}
```

### Filter by Faculty

```python
# Only post articles relevant to specific faculty
if 'John Dewey' in [f['name'] for f in article['metadata']['interested_faculty']]:
    poster.post_status(format_post(article))
```

### Custom Hashtags

```python
# In format_post()
post += "\n\n#CriticalThinking #HigherEd #AcademicTwitter"
```

## ✅ Status

- ✅ GoToSocial module created
- ✅ Integration with aggregation pipeline
- ✅ GitHub Actions workflow updated
- ⏳ **TODO**: Add `GOTOSOCIAL_API_TOKEN` to GitHub Secrets
- ⏳ **TODO**: Test first automated run

---

**Live Feed**: https://social.castalia.institute/@inquiryinstitute
**Repository**: https://github.com/InquiryInstitute/news
**Site**: https://inquiryinstitute.github.io/news/
