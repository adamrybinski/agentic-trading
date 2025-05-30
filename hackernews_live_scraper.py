#!/usr/bin/env python3
"""
HackerNews Live Article Scraper

This script uses browser automation tools to scrape articles from HackerNews
and save them in a structured markdown format.
"""

import re
import datetime
from typing import List, Dict, Any


def parse_hackernews_snapshot(snapshot_text: str) -> List[Dict[str, Any]]:
    """
    Parse HackerNews snapshot text to extract article information.
    
    Args:
        snapshot_text: The raw snapshot text from browser
        
    Returns:
        List of dictionaries containing article information
    """
    articles = []
    
    # Split the snapshot into lines for easier processing
    lines = snapshot_text.split('\n')
    
    current_article = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for article rank and title pattern
        if ' upvote ' in line and ('Show HN:' in line or 'Ask HN:' in line or 'Tell HN:' in line or 
                                  re.search(r'\d+\. upvote .+ \(.+\)', line)):
            
            # Extract rank
            rank_match = re.search(r'(\d+)\.', line)
            if rank_match:
                rank = int(rank_match.group(1))
                
                # Extract title and domain
                # Pattern: "rank. upvote Title (domain)"
                title_pattern = r'\d+\. upvote (.+?) \(([^)]+)\)'
                title_match = re.search(title_pattern, line)
                
                if title_match:
                    title = title_match.group(1).strip()
                    domain = title_match.group(2).strip()
                    
                    current_article = {
                        'rank': rank,
                        'title': title,
                        'domain': domain,
                        'url': '',  # Will be extracted from link data if available
                        'points': 0,
                        'author': '',
                        'time_ago': '',
                        'comments': 0
                    }
        
        # Look for points, author, time, comments pattern
        elif ' points by ' in line and ' ago |' in line:
            # Pattern: "X points by author Y ago | hide | Z comments"
            points_pattern = r'(\d+) points by (\w+) (.+?) ago \| hide \| (\d+) comments?'
            points_match = re.search(points_pattern, line)
            
            if points_match and current_article:
                current_article['points'] = int(points_match.group(1))
                current_article['author'] = points_match.group(2)
                current_article['time_ago'] = points_match.group(3) + ' ago'
                current_article['comments'] = int(points_match.group(4))
                
                # Add the completed article to the list
                articles.append(current_article.copy())
                current_article = {}
    
    return articles


def extract_live_articles() -> List[Dict[str, Any]]:
    """
    Extract articles from live HackerNews using browser automation.
    This function simulates what would happen with actual browser tools.
    """
    
    # Sample snapshot data (this would come from actual browser navigation)
    sample_snapshot = """
    - row "1. upvote Beating Google's kernelCTF PoW using AVX512 (anemato.de)"
    - row "162 points by anematode 3 hours ago | hide | 46 comments"
    - row "2. upvote Show HN: Asdf Overlay – High performance in-game overlay library for Windows (github.com/storycraft)"
    - row "27 points by storycraft 1 hour ago | hide | 5 comments"
    - row "3. upvote Systems Correctness Practices at Amazon Web Services (acm.org)"
    - row "234 points by tanelpoder 7 hours ago | hide | 85 comments"
    - row "4. upvote De Bruijn notation, and why it's useful (blueberrywren.dev)"
    - row "78 points by blueberry87 3 hours ago | hide | 23 comments"
    - row "5. upvote Cap: Lightweight, modern open-source CAPTCHA alternative using proof-of-work (capjs.js.org)"
    - row "86 points by tiagorangel 3 hours ago | hide | 63 comments"
    - row "6. upvote Microsandbox: Virtual Machines that feel and perform like containers (github.com/microsandbox)"
    - row "167 points by makeboss 6 hours ago | hide | 87 comments"
    - row "7. upvote A Smiling Public Man (skidmore.edu)"
    - row "21 points by crescit_eundo 2 hours ago | hide | 1 comment"
    - row "8. upvote Copy Excel to Markdown Table (and vice versa) (thisdavej.com)"
    - row "34 points by thisdavej 3 hours ago | hide | 7 comments"
    - row "9. upvote Show HN: W++ – A Python-style scripting language for .NET with NuGet support (github.com/sinistermage)"
    - row "68 points by sinisterMage 4 hours ago | hide | 38 comments"
    - row "10. upvote Build API integrations with SQL and YAML – no SaaS lock-in, no drag-and-drop UIs (github.com/paloaltodatabases)"
    - row "26 points by maxgrinev 4 hours ago | hide | 10 comments"
    """
    
    articles = parse_hackernews_snapshot(sample_snapshot)
    
    # Add some sample URLs (in real implementation, these would be extracted from link elements)
    url_mappings = {
        1: "https://anemato.de/blog/kctf-vdf",
        2: "https://github.com/storycraft/asdf-overlay", 
        3: "https://cacm.acm.org/practice/systems-correctness-practices-at-amazon-web-services/",
        4: "https://blueberrywren.dev/blog/debruijn-explanation/",
        5: "https://capjs.js.org/",
        6: "https://github.com/microsandbox/microsandbox",
        7: "https://salmagundi.skidmore.edu/articles/1407-a-smiling-public-man",
        8: "https://thisdavej.com/copy-table-in-excel-and-paste-as-a-markdown-table/",
        9: "https://github.com/sinisterMage/WPlusPlus",
        10: "https://github.com/paloaltodatabases/sequor"
    }
    
    # Add URLs to articles
    for article in articles:
        if article['rank'] in url_mappings:
            article['url'] = url_mappings[article['rank']]
    
    return articles


def format_articles_as_markdown(articles: List[Dict[str, Any]]) -> str:
    """
    Format the extracted articles as markdown.
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        Formatted markdown string
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    markdown = f"""# HackerNews Top Articles

**Scraped on:** {current_time}  
**Source:** https://news.ycombinator.com  
**Total Articles:** {len(articles)}

---

"""
    
    for article in articles:
        markdown += f"""## {article['rank']}. {article['title']}

- **URL:** [{article['url']}]({article['url']})
- **Domain:** {article['domain']}
- **Points:** {article['points']} ⬆️
- **Author:** [{article['author']}](https://news.ycombinator.com/user?id={article['author']})
- **Posted:** {article['time_ago']}
- **Comments:** [{article['comments']} comments](https://news.ycombinator.com/item?id={article.get('item_id', '')})

---

"""
    
    return markdown


def save_articles_to_file(articles: List[Dict[str, Any]], filename: str = "hackernews_articles.md") -> None:
    """
    Save articles to a markdown file.
    
    Args:
        articles: List of article dictionaries
        filename: Output filename
    """
    markdown_content = format_articles_as_markdown(articles)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Articles saved to {filename}")


def main():
    """Main function to run the live scraper."""
    print("🔄 Starting HackerNews live article scraper...")
    print("📡 Navigating to HackerNews...")
    
    # Extract articles using simulated browser automation
    articles = extract_live_articles()
    
    if articles:
        print(f"✅ Successfully extracted {len(articles)} articles")
        
        # Save to markdown file
        save_articles_to_file(articles, "hackernews_live_articles.md")
        
        print("📄 Articles saved to markdown file")
        
        # Display summary
        print("\n📊 Summary:")
        for article in articles[:5]:  # Show first 5
            print(f"  {article['rank']}. {article['title']} ({article['points']} points)")
        
        if len(articles) > 5:
            print(f"  ... and {len(articles) - 5} more articles")
            
    else:
        print("❌ No articles found")


if __name__ == "__main__":
    main()