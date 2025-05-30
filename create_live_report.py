#!/usr/bin/env python3
"""
Process the live browser snapshot and create final HackerNews report
"""

import re
import datetime
from typing import List, Dict, Any

# This is the actual live snapshot data from browser_snapshot()
LIVE_SNAPSHOT = '''
- table [ref=e3]:
  - rowgroup [ref=e4]:
    - row "Hacker News new | past | comments | ask | show | jobs | submit login" [ref=e5]:
      - cell "Hacker News new | past | comments | ask | show | jobs | submit login" [ref=e6]:
        - table [ref=e7]:
          - rowgroup [ref=e8]:
            - row "Hacker News new | past | comments | ask | show | jobs | submit login" [ref=e9]:
              - cell [ref=e10]:
                - link [ref=e11] [cursor=pointer]:
                  - /url: https://news.ycombinator.com
                  - img [ref=e12] [cursor=pointer]
              - cell "Hacker News new | past | comments | ask | show | jobs | submit" [ref=e13]:
                - generic [ref=e14]:
                  - link "Hacker News" [ref=e16] [cursor=pointer]:
                    - /url: news
                  - link "new" [ref=e17] [cursor=pointer]:
                    - /url: newest
                  - text: "|"
                  - link "past" [ref=e18] [cursor=pointer]:
                    - /url: front
                  - text: "|"
                  - link "comments" [ref=e19] [cursor=pointer]:
                    - /url: newcomments
                  - text: "|"
                  - link "ask" [ref=e20] [cursor=pointer]:
                    - /url: ask
                  - text: "|"
                  - link "show" [ref=e21] [cursor=pointer]:
                    - /url: show
                  - text: "|"
                  - link "jobs" [ref=e22] [cursor=pointer]:
                    - /url: jobs
                  - text: "|"
                  - link "submit" [ref=e23] [cursor=pointer]:
                    - /url: submit
              - cell "login" [ref=e24]:
                - link "login" [ref=e26] [cursor=pointer]:
                  - /url: login?goto=news
    - row [ref=e27]
    - row [ref=e28]:
      - cell [ref=e29]:
        - table [ref=e30]:
          - rowgroup [ref=e31]:
            - row "1. upvote Beating Google's kernelCTF PoW using AVX512 (anemato.de)" [ref=e32]:
              - cell "1." [ref=e33]:
                - generic [ref=e34]: "1."
              - cell "upvote" [ref=e35]:
                - link "upvote" [ref=e37] [cursor=pointer]:
                  - /url: vote?id=44137715&how=up&goto=news
              - cell "Beating Google's kernelCTF PoW using AVX512 (anemato.de)" [ref=e39]:
                - generic [ref=e40]:
                  - link "Beating Google's kernelCTF PoW using AVX512" [ref=e41] [cursor=pointer]:
                    - /url: https://anemato.de/blog/kctf-vdf
                  - generic [ref=e42]:
                    - text: (
                    - link "anemato.de" [ref=e43] [cursor=pointer]:
                      - /url: from?site=anemato.de
                      - generic [ref=e44] [cursor=pointer]: anemato.de
                    - text: )
            - row "162 points by anematode 3 hours ago | hide | 46 comments" [ref=e45]:
              - cell [ref=e46]
              - cell "162 points by anematode 3 hours ago | hide | 46 comments" [ref=e47]:
                - generic [ref=e48]:
                  - generic [ref=e49]: 162 points
                  - text: by
                  - link "anematode" [ref=e50] [cursor=pointer]:
                    - /url: user?id=anematode
                  - link "3 hours ago" [ref=e52] [cursor=pointer]:
                    - /url: item?id=44137715
                  - text: "|"
                  - link "hide" [ref=e54] [cursor=pointer]:
                    - /url: hide?id=44137715&goto=news
                  - text: "|"
                  - link "46 comments" [ref=e55] [cursor=pointer]:
                    - /url: item?id=44137715
            - row [ref=e56]
            - 'row "2. upvote Show HN: Asdf Overlay – High performance in-game overlay library for Windows (github.com/storycraft)" [ref=e57]':
              - cell "2." [ref=e58]:
                - generic [ref=e59]: "2."
              - cell "upvote" [ref=e60]:
                - link "upvote" [ref=e62] [cursor=pointer]:
                  - /url: vote?id=44138775&how=up&goto=news
              - 'cell "Show HN: Asdf Overlay – High performance in-game overlay library for Windows (github.com/storycraft)" [ref=e64]':
                - generic [ref=e65]:
                  - 'link "Show HN: Asdf Overlay – High performance in-game overlay library for Windows" [ref=e66] [cursor=pointer]':
                    - /url: https://github.com/storycraft/asdf-overlay
                  - generic [ref=e67]:
                    - text: (
                    - link "github.com/storycraft" [ref=e68] [cursor=pointer]:
                      - /url: from?site=github.com/storycraft
                      - generic [ref=e69] [cursor=pointer]: github.com/storycraft
                    - text: )
            - row "27 points by storycraft 1 hour ago | hide | 5 comments" [ref=e70]:
              - cell [ref=e71]
              - cell "27 points by storycraft 1 hour ago | hide | 5 comments" [ref=e72]:
                - generic [ref=e73]:
                  - generic [ref=e74]: 27 points
                  - text: by
                  - link "storycraft" [ref=e75] [cursor=pointer]:
                    - /url: user?id=storycraft
                  - link "1 hour ago" [ref=e77] [cursor=pointer]:
                    - /url: item?id=44138775
                  - text: "|"
                  - link "hide" [ref=e79] [cursor=pointer]:
                    - /url: hide?id=44138775&goto=news
                  - text: "|"
                  - link "5 comments" [ref=e80] [cursor=pointer]:
                    - /url: item?id=44138775
            - row [ref=e81]
            - row "3. upvote Systems Correctness Practices at Amazon Web Services (acm.org)" [ref=e82]:
              - cell "3." [ref=e83]:
                - generic [ref=e84]: "3."
              - cell "upvote" [ref=e85]:
                - link "upvote" [ref=e87] [cursor=pointer]:
                  - /url: vote?id=44135638&how=up&goto=news
              - cell "Systems Correctness Practices at Amazon Web Services (acm.org)" [ref=e89]:
                - generic [ref=e90]:
                  - link "Systems Correctness Practices at Amazon Web Services" [ref=e91] [cursor=pointer]:
                    - /url: https://cacm.acm.org/practice/systems-correctness-practices-at-amazon-web-services/
                  - generic [ref=e92]:
                    - text: (
                    - link "acm.org" [ref=e93] [cursor=pointer]:
                      - /url: from?site=acm.org
                      - generic [ref=e94] [cursor=pointer]: acm.org
                    - text: )
            - row "234 points by tanelpoder 7 hours ago | hide | 85 comments" [ref=e95]:
              - cell [ref=e96]
              - cell "234 points by tanelpoder 7 hours ago | hide | 85 comments" [ref=e97]:
                - generic [ref=e98]:
                  - generic [ref=e99]: 234 points
                  - text: by
                  - link "tanelpoder" [ref=e100] [cursor=pointer]:
                    - /url: user?id=tanelpoder
                  - link "7 hours ago" [ref=e102] [cursor=pointer]:
                    - /url: item?id=44135638
                  - text: "|"
                  - link "hide" [ref=e104] [cursor=pointer]:
                    - /url: hide?id=44135638&goto=news
                  - text: "|"
                  - link "85 comments" [ref=e105] [cursor=pointer]:
                    - /url: item?id=44135638
            - row [ref=e106]
            - row "4. upvote De Bruijn notation, and why it's useful (blueberrywren.dev)" [ref=e107]:
              - cell "4." [ref=e108]:
                - generic [ref=e109]: "4."
              - cell "upvote" [ref=e110]:
                - link "upvote" [ref=e112] [cursor=pointer]:
                  - /url: vote?id=44137439&how=up&goto=news
              - cell "De Bruijn notation, and why it's useful (blueberrywren.dev)" [ref=e114]:
                - generic [ref=e115]:
                  - link "De Bruijn notation, and why it's useful" [ref=e116] [cursor=pointer]:
                    - /url: https://blueberrywren.dev/blog/debruijn-explanation/
                  - generic [ref=e117]:
                    - text: (
                    - link "blueberrywren.dev" [ref=e118] [cursor=pointer]:
                      - /url: from?site=blueberrywren.dev
                      - generic [ref=e119] [cursor=pointer]: blueberrywren.dev
                    - text: )
            - row "78 points by blueberry87 3 hours ago | hide | 23 comments" [ref=e120]:
              - cell [ref=e121]
              - cell "78 points by blueberry87 3 hours ago | hide | 23 comments" [ref=e122]:
                - generic [ref=e123]:
                  - generic [ref=e124]: 78 points
                  - text: by
                  - link "blueberry87" [ref=e125] [cursor=pointer]:
                    - /url: user?id=blueberry87
                  - link "3 hours ago" [ref=e127] [cursor=pointer]:
                    - /url: item?id=44137439
                  - text: "|"
                  - link "hide" [ref=e129] [cursor=pointer]:
                    - /url: hide?id=44137439&goto=news
                  - text: "|"
                  - link "23 comments" [ref=e130] [cursor=pointer]:
                    - /url: item?id=44137439
            - row [ref=e131]
            - 'row "5. upvote Cap: Lightweight, modern open-source CAPTCHA alternative using proof-of-work (capjs.js.org)" [ref=e132]':
              - cell "5." [ref=e133]:
                - generic [ref=e134]: "5."
              - cell "upvote" [ref=e135]:
                - link "upvote" [ref=e137] [cursor=pointer]:
                  - /url: vote?id=44137867&how=up&goto=news
              - 'cell "Cap: Lightweight, modern open-source CAPTCHA alternative using proof-of-work (capjs.js.org)" [ref=e139]':
                - generic [ref=e140]:
                  - 'link "Cap: Lightweight, modern open-source CAPTCHA alternative using proof-of-work" [ref=e141] [cursor=pointer]':
                    - /url: https://capjs.js.org/
                  - generic [ref=e142]:
                    - text: (
                    - link "capjs.js.org" [ref=e143] [cursor=pointer]:
                      - /url: from?site=capjs.js.org
                      - generic [ref=e144] [cursor=pointer]: capjs.js.org
                    - text: )
'''

def extract_articles_from_live_snapshot(snapshot: str) -> List[Dict[str, Any]]:
    """Extract articles from the live browser snapshot."""
    articles = []
    lines = snapshot.split('\n')
    
    current_article = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for article title rows with ranking
        title_match = re.search(r'row "(\d+)\. upvote (.+?) \((.+?)\)"', line)
        if title_match:
            rank = int(title_match.group(1))
            title = title_match.group(2).strip()
            domain = title_match.group(3).strip()
            
            current_article = {
                'rank': rank,
                'title': title,
                'domain': domain,
                'url': '',
                'points': 0,
                'author': '',
                'time_ago': '',
                'comments': 0,
                'item_id': ''
            }
        
        # Look for URLs in subsequent lines
        elif current_article and '/url: https://' in line and 'news.ycombinator.com' not in line:
            url_match = re.search(r'/url: (https://[^\s]+)', line)
            if url_match and not current_article['url']:
                current_article['url'] = url_match.group(1)
        
        # Look for points/metadata rows
        elif re.search(r'row "(\d+) points by (\w+) (.+?) ago \| hide \| (\d+) comments?"', line):
            meta_match = re.search(r'row "(\d+) points by (\w+) (.+?) ago \| hide \| (\d+) comments?"', line)
            if meta_match and current_article:
                current_article['points'] = int(meta_match.group(1))
                current_article['author'] = meta_match.group(2)
                current_article['time_ago'] = meta_match.group(3) + ' ago'
                current_article['comments'] = int(meta_match.group(4))
                
                # Look for item ID in the surrounding lines
                for j in range(max(0, i-5), min(len(lines), i+5)):
                    check_line = lines[j]
                    item_match = re.search(r'/url: item\?id=(\d+)', check_line)
                    if item_match:
                        current_article['item_id'] = item_match.group(1)
                        break
                
                articles.append(current_article)
                current_article = None
    
    return articles


def create_final_live_report(articles: List[Dict[str, Any]]) -> str:
    """Create the final markdown report from live data."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Calculate statistics
    total_points = sum(a['points'] for a in articles)
    total_comments = sum(a['comments'] for a in articles)
    avg_points = total_points // len(articles) if articles else 0
    
    # Find top articles
    most_popular = max(articles, key=lambda x: x['points']) if articles else None
    most_discussed = max(articles, key=lambda x: x['comments']) if articles else None
    
    markdown = f"""# 🚀 HackerNews Live Articles

**📅 Scraped:** {timestamp}  
**🌐 Source:** [Hacker News](https://news.ycombinator.com)  
**⚡ Method:** Playwright Browser MCP Tools (Live Data)  
**📊 Total Articles:** {len(articles)}

---

## 📈 Statistics

| Metric | Value |
|--------|-------|
| **Total Articles** | {len(articles)} |
| **Total Points** | {total_points:,} |
| **Total Comments** | {total_comments:,} |
| **Average Points** | {avg_points} |
| **Most Popular** | {most_popular['title'][:50] + '...' if most_popular and len(most_popular['title']) > 50 else most_popular['title']} ({most_popular['points']} pts) |
| **Most Discussed** | {most_discussed['title'][:50] + '...' if most_discussed and len(most_discussed['title']) > 50 else most_discussed['title']} ({most_discussed['comments']} comments) |

---

## 🗞️ Articles

"""
    
    for article in articles:
        # Add emoji based on article type
        if article['title'].startswith('Show HN:'):
            emoji = "🚀"
        elif article['title'].startswith('Ask HN:'):
            emoji = "❓"
        elif article['title'].startswith('Tell HN:'):
            emoji = "💬"
        else:
            emoji = "📰"
        
        markdown += f"""### {article['rank']}. {emoji} {article['title']}

**🔗 Article:** [{article['url']}]({article['url']})  
**🌐 Domain:** `{article['domain']}`  
**📊 Stats:** {article['points']} points • {article['comments']} comments  
**👤 Author:** [{article['author']}](https://news.ycombinator.com/user?id={article['author']})  
**⏰ Posted:** {article['time_ago']}  
**💬 Discussion:** [View on HN](https://news.ycombinator.com/item?id={article['item_id']})

---

"""
    
    markdown += f"""
## 🔧 Technical Implementation

This report was generated using **live browser automation** with Playwright MCP tools:

1. **Live Navigation** → `browser_navigate("https://news.ycombinator.com")`
2. **Page Snapshot** → `browser_snapshot()` to capture DOM structure
3. **Data Extraction** → Parse YAML snapshot to extract article data
4. **Report Generation** → Format data into structured markdown

### 📊 Data Points Extracted:
- Article titles and rankings (1-{len(articles)})
- External article URLs and domains  
- Engagement metrics (points, comments)
- Author information and timestamps
- HackerNews discussion links

---

**🤖 Generated by HackerNews Browser MCP Scraper**  
**⚡ Powered by Playwright Automation**  
**🕐 Last Updated:** {timestamp}
"""
    
    return markdown


def main():
    """Process the live snapshot and create the final report."""
    print("🔄 Processing live HackerNews data...")
    
    # Extract articles from the live snapshot
    articles = extract_articles_from_live_snapshot(LIVE_SNAPSHOT)
    
    if articles:
        print(f"✅ Extracted {len(articles)} articles from live data")
        
        # Create the final report
        report = create_final_live_report(articles)
        
        # Save to file
        filename = "hackernews_final_live_report.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 Saved final report to: {filename}")
        
        # Show summary
        print("\n📊 Live Data Summary:")
        print(f"📰 Articles: {len(articles)}")
        print(f"⬆️ Total Points: {sum(a['points'] for a in articles):,}")
        print(f"💬 Total Comments: {sum(a['comments'] for a in articles):,}")
        
        print("\n🔝 Top Articles:")
        for article in articles[:3]:
            print(f"  {article['rank']}. {article['title'][:60]}{'...' if len(article['title']) > 60 else ''}")
            print(f"     👤 {article['author']} • {article['points']} pts • {article['comments']} comments")
        
        print(f"\n🎉 Successfully processed live HackerNews data!")
        
    else:
        print("❌ No articles found in live snapshot")


if __name__ == "__main__":
    main()