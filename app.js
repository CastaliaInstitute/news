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

function createNewsCard(article) {
    const icon = getTypeIcon(article.type);
    const score = article.relevance_score;
    const scoreDisplay = score ? `<span class="score" title="Relevance Score">${(score * 100).toFixed(0)}%</span>` : '';
    const keywords = article.metadata?.matched_keywords;
    const keywordsDisplay = keywords && keywords.length > 0 
        ? `<div class="keywords">${keywords.map(k => `<span class="keyword">${k}</span>`).join('')}</div>`
        : '';
    
    return `
        <article class="news-card" data-type="${article.type}">
            <div class="card-header">
                <span class="type-icon">${icon}</span>
                ${scoreDisplay}
            </div>
            <h2>${article.title}</h2>
            <div class="meta">
                <span class="source">${article.source}</span>
                <span class="date">${formatDate(article.date)}</span>
            </div>
            <p class="description">${article.description}</p>
            ${keywordsDisplay}
            <a href="${article.url}" target="_blank" rel="noopener noreferrer">Read More</a>
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
