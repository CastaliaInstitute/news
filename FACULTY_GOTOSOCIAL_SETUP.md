# Faculty GoToSocial Posting Setup

## Overview

Articles are now posted under **faculty member accounts** based on their interests! When an article is relevant to Tesla, it posts as `@a.Tesla@social.inquiry.institute`.

## 🔧 Setup Steps

### 1. Run Database Migration

First, add the GoToSocial fields to the faculty table:

```bash
# Run the migration in Supabase SQL Editor
cat supabase_migration_faculty_gotosocial.sql
```

Or via CLI:
```bash
psql "postgresql://postgres.pilmscrodlitdrygabvo:..." < supabase_migration_faculty_gotosocial.sql
```

This adds:
- `gotosocial_handle` - The faculty's handle (e.g., "a.Tesla")
- `gotosocial_api_token` - Their API token for posting
- `fediverse_enabled` - Whether posting is enabled

### 2. Get API Tokens for Each Faculty

For each faculty member who should post:

1. **Log in as faculty** at: https://social.castalia.institute
   - Username: `a.Tesla` (or their handle)
   - Password: (their password)

2. **Create Application Token**:
   - Go to: https://social.castalia.institute/settings/applications
   - Click "New Application"
   - Name: "Inquiry Institute News Aggregator"
   - Scopes: `write:statuses`
   - Click "Submit"
   - **Copy the token** (you'll only see it once!)

3. **Store in Supabase**:
   ```sql
   UPDATE faculty 
   SET 
     gotosocial_handle = 'a.Tesla',
     gotosocial_api_token = 'your_actual_token_here',
     fediverse_enabled = true
   WHERE slug = 'nikola-tesla';
   ```

### 3. Repeat for Multiple Faculty

Do this for each faculty member:
- `a.Tesla` (Nikola Tesla)
- `a.Edison` (Thomas Edison)
- `a.Curie` (Marie Curie)
- `a.Einstein` (Albert Einstein)
- etc.

## 🎯 How It Works

### Article Assignment

1. **Aggregation runs** every 6 hours
2. **RAG system scores** articles for relevance
3. **Tracks interested faculty** for each article
4. **Posts under faculty accounts** who are interested
5. **Limit**: Max 3 posts per faculty per run

### Example Flow

```
Article: "New Breakthrough in Electrical Engineering"
           ↓
Interested Faculty: [Tesla, Edison, Faraday]
           ↓
Post as: @a.Tesla (first match with GoToSocial account)
           ↓
Appears on: social.castalia.institute/@a.Tesla
```

### Post Format

```
🔥 New Breakthrough in Electrical Engineering

Researchers at MIT develop revolutionary method for
wireless power transmission at scale...

🔗 https://example.com/article

#ElectricalEngineering #AI #Systems
```

## 📊 Faculty Account Management

### View Configured Accounts

```sql
SELECT 
  name,
  gotosocial_handle,
  fediverse_enabled,
  news_topics
FROM faculty 
WHERE fediverse_enabled = true
ORDER BY name;
```

### Enable/Disable Faculty Posting

```sql
-- Enable
UPDATE faculty 
SET fediverse_enabled = true 
WHERE slug = 'nikola-tesla';

-- Disable
UPDATE faculty 
SET fediverse_enabled = false 
WHERE slug = 'thomas-edison';
```

### Update Token (if expired)

```sql
UPDATE faculty 
SET gotosocial_api_token = 'new_token_here'
WHERE slug = 'nikola-tesla';
```

## 🔐 Security

- **Tokens encrypted at rest** in Supabase
- **Limited scope**: `write:statuses` only
- **Per-faculty control**: Each faculty can revoke their token
- **No secrets in GitHub**: Tokens stored in database only

## 📱 Testing Locally

```bash
# Set up environment (tokens from Supabase)
python gotosocial_poster.py

# Run full aggregation (will post to social.castalia.institute!)
python aggregate.py
```

## 🎨 Example Posts

### GitHub Trending (posted by relevant faculty)
```
🔥 Trending: AI/awesome-ml-framework

A comprehensive toolkit for machine learning research
with automated testing and evaluation...

🔗 https://github.com/example/awesome-ml-framework

#MachineLearning #AI #Research
```

### New Model (posted by AI researchers)
```
🤖 New Model: GPT-4-Turbo

Enhanced version with improved reasoning and
reduced hallucinations...

🔗 https://openai.com/gpt-4-turbo

#AI #LanguageModels #Research
```

### Research Article (posted by domain experts)
```
📰 Critical Thinking in AI Education

Stanford researchers develop new framework
for teaching analytical skills...

🔗 https://example.com/article

#CriticalThinking #Education #AI
```

## 📊 Post Distribution

Each faculty member posts articles **relevant to their interests**:

- **Tesla**: Electrical engineering, energy, systems
- **Curie**: Physics, radioactivity, research methodology
- **Turing**: Computer science, AI, cryptography
- **Dewey**: Education, pedagogy, critical thinking

Articles are assigned to the **most interested faculty member** who:
1. Has `fediverse_enabled = true`
2. Has a valid `gotosocial_api_token`
3. Hasn't exceeded their post limit (3 per run)

## 🔄 Automation

### GitHub Actions

The workflow now:
1. Aggregates news (every 6 hours)
2. Scores by faculty relevance
3. Posts under faculty accounts
4. Commits results

**No GitHub Secrets needed** - All tokens in Supabase!

### Rate Limiting

- **Posts per faculty**: 3 per run (every 6 hours)
- **Total posts**: ~30-50 per day (across all faculty)
- **Delay between posts**: 2 seconds
- **Well under** GoToSocial rate limits

## 🛠️ Troubleshooting

### "No faculty accounts configured"
- Run the SQL migration
- Add `gotosocial_api_token` for at least one faculty
- Set `fediverse_enabled = true`

### "API error 401"
- Token expired - get new token from faculty account
- Update in database

### "Posted 0 articles"
- Check that faculty have `news_topics` configured
- Verify articles match faculty interests
- Check GitHub Actions logs

## 📈 Monitoring

### Check Posts

Visit faculty profiles:
- https://social.castalia.institute/@a.Tesla
- https://social.castalia.institute/@a.Curie
- https://social.castalia.institute/@a.Turing

### Database Query

```sql
-- See post distribution
SELECT 
  f.name,
  f.gotosocial_handle,
  COUNT(*) FILTER (WHERE a.posted_at > NOW() - INTERVAL '1 day') as posts_today
FROM faculty f
LEFT JOIN article_posts a ON a.faculty_id = f.id
WHERE f.fediverse_enabled = true
GROUP BY f.id, f.name, f.gotosocial_handle
ORDER BY posts_today DESC;
```

## ✅ Advantages of Faculty Posting

1. **Authentic Voice**: Posts from subject matter experts
2. **Distributed Reach**: Multiple accounts = more visibility
3. **Interest Alignment**: Faculty share what they care about
4. **Engagement**: Followers interested in specific topics
5. **Credibility**: Posts come from recognized scholars

## 🚀 Next Steps

1. ✅ Run migration
2. ⏳ Get tokens for 5-10 key faculty members
3. ⏳ Test with `python gotosocial_poster.py`
4. ⏳ Deploy and monitor first automated run
5. ⏳ Gradually add more faculty accounts

---

**Example Faculty**: Tesla, Curie, Turing, Dewey, Russell, Chomsky, hooks, Nussbaum, Sen, Freire
**Platform**: https://social.castalia.institute
**Repository**: https://github.com/InquiryInstitute/news
