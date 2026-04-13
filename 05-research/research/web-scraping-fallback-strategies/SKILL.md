---
name: web-scraping-fallback-strategies
description: Systematic approach for handling failed web scraping attempts with fallback options
trigger: When web scraping fails due to anti-bot measures, dynamic content, or API restrictions
---

# Web Scraping Fallback Strategies

## Primary Approaches (in order of preference)

1. **RSS/API First**
   - Try RSSHub public instances
   - Try dedicated API services (Feeddd, etc.)
   - Check for rate limiting or authentication requirements

2. **Direct Scraping**
   - Attempt static HTML scraping with requests
   - Parse JavaScript-rendered content patterns
   - Handle cookie/session requirements

3. **Workaround Solutions** (when technical barriers persist)
   - Manual URL provision + automated processing
   - Browser automation (Selenium/Playwright)
   - Hybrid human-AI workflows

## Common Failure Patterns

| Service Type | Common Issues | Fallback |
|--------------|--------------|----------|
| RSSHub | 503 errors, requires cookies | Local deployment with auth |
| Search engines | JS-rendered, anti-bot | Headless browser |
| RSS APIs | JWT auth, redirects | Manual curation |
| Static sites | Blocked, rate limited | Proxy rotation |

## Decision Framework

When primary approaches fail:
1. Document what was tried and why it failed
2. Present 2-3 pragmatic alternatives
3. Let user choose based on their time/effort preference
4. Implement chosen solution without further deliberation