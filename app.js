let newsData = [];
let generatedAt = null;

async function loadNewsData() {
    const response = await fetch('news_data.json', { cache: 'no-store' });
    if (!response.ok) {
        throw new Error(`Failed to load live feed: HTTP ${response.status}`);
    }

    const data = await response.json();
    newsData = Array.isArray(data.items) ? data.items : [];
    generatedAt = data.generated_at || null;
    return newsData;
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function formatTimestamp(dateString) {
    return new Date(dateString).toLocaleString();
}

function getTypeIcon(type) {
    const icons = {
        'github_trending': '🔥',
        'model_release': '🤖',
        'benchmark_update': '📊',
        'article': '📰'
    };
    return icons[type] || '📄';
}

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, character => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));
}

function createNewsCard(article) {
    const icon = getTypeIcon(article.type);
    const score = article.relevance_score;
    const scoreDisplay = score ? `<span class="score" title="Relevance Score">${(score * 100).toFixed(0)}%</span>` : '';
    const keywords = article.metadata?.matched_keywords;
    const keywordsDisplay = keywords && keywords.length > 0 
        ? `<div class="keywords">${keywords.map(k => `<span class="keyword">${k}</span>`).join('')}</div>`
        : '';
    const author = article.faculty_author?.name;
    const authorDisplay = author ? `<p class="faculty-author">Faculty analysis: ${escapeHtml(author)}</p>` : '';
    const summary = article.faculty_summary || article.description;
    const sources = Array.isArray(article.sources) ? article.sources : [];
    const sourceLinks = sources.length
        ? `<div class="source-links"><span>Sources:</span> ${sources.map(source => `<a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.publisher || source.title)}</a>`).join(', ')}</div>`
        : '';
    
    return `
        <article class="news-card" data-type="${article.type}">
            <div class="card-header">
                <span class="type-icon">${icon}</span>
                ${scoreDisplay}
            </div>
            <h2>${escapeHtml(article.title)}</h2>
            <div class="meta">
                <span class="source">${escapeHtml(article.source)}</span>
                <span class="date">${formatDate(article.date)}</span>
            </div>
            ${authorDisplay}
            <p class="description">${escapeHtml(summary)}</p>
            ${keywordsDisplay}
            ${sourceLinks}
            <a href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer">Read original source</a>
        </article>
    `;
}

async function renderNews() {
    const newsFeed = document.getElementById('news-feed');
    
    try {
        await loadNewsData();
        
        if (newsData.length === 0) {
            newsFeed.innerHTML = '<div class="no-data">No news available yet. Check back soon!</div>';
            return;
        }
        
        const newsHTML = newsData.map(article => createNewsCard(article)).join('');
        newsFeed.innerHTML = newsHTML;
        
        // Update last updated time
        const lastUpdated = document.getElementById('last-updated');
        if (lastUpdated) {
            if (generatedAt) {
                lastUpdated.textContent = `Last updated: ${formatTimestamp(generatedAt)}`;
            } else {
                lastUpdated.textContent = 'Last updated: waiting for first live aggregation run';
            }
        }
        
    } catch (error) {
        console.error('Error rendering news:', error);
        newsFeed.innerHTML = '<div class="error">Unable to load live news feed. Run the aggregation pipeline to generate news_data.json.</div>';
    }
}

document.addEventListener('DOMContentLoaded', renderNews);
