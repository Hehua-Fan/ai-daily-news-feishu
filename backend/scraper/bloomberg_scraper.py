"""
Bloomberg Technology news scraper

This module provides the BloombergScraper class for scraping tech news from Bloomberg.
"""

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any


class BloombergScraper:
    """Bloomberg Technology scraper for tech and AI news"""
    
    BASE_URL = "https://www.bloomberg.com"
    TECH_URL = "https://www.bloomberg.com/technology"
    SOURCE_TAG = "Bloomberg"
    
    def __init__(self):
        """Initialize the Bloomberg scraper"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.bloomberg.com/',
            'Connection': 'keep-alive',
        }
    
    @staticmethod
    def get_today_date() -> str:
        """Get yesterday's date in YYYY-MM-DD format"""
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    @staticmethod
    def get_recent_dates(days: int = 3) -> List[str]:
        """Get list of recent dates for news filtering"""
        today = datetime.now()
        return [
            (today - timedelta(days=i)).strftime("%Y-%m-%d") 
            for i in range(days)
        ]
    
    def get_title_and_link_list(self) -> List[Dict[str, Any]]:
        """Scrape technology news from Bloomberg"""
        news_list = []
        target_dates = self.get_recent_dates()
        print(f"🔍 Bloomberg: 查找日期 {target_dates}")
        
        try:
            response = requests.get(self.TECH_URL, headers=self.headers, timeout=30)
            
            if response.status_code == 403:
                print("⚠️  Bloomberg 访问被限制，尝试其他方法")
                return []
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Look for article links
            articles = soup.find_all('article') or soup.find_all('div', class_='story-package-module')
            if not articles:
                # Fallback: look for links in story containers
                articles = soup.find_all('a', href=True)
                articles = [a for a in articles if '/news/articles/' in a.get('href', '')]
            
            print(f"📋 找到 {len(articles)} 个潜在文章")
            
            found_articles = 0
            for article in articles:
                try:
                    # Extract link and title
                    if article.name == 'article':
                        link_elem = article.find('a', href=True)
                        if not link_elem:
                            continue
                        href = link_elem.get('href')
                        title_elem = link_elem.find('h3') or link_elem.find('h2') or link_elem
                        title = title_elem.text.strip() if title_elem else ""
                    else:  # article is already an 'a' tag
                        href = article.get('href')
                        title = article.text.strip()
                    
                    if not href or not title:
                        continue
                    
                    # Skip unwanted links
                    if any(skip in href for skip in ['#', 'mailto:', 'tel:', 'javascript:', '/authors/', '/terminal/']):
                        continue
                    
                    # Filter for AI/tech content
                    ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'tech', 'technology', 'startup', 'software', 'data', 'algorithm', 'automation', 'digital', 'innovation']
                    if not any(keyword in title.lower() for keyword in ai_keywords):
                        continue
                    
                    # Build full URL
                    if href.startswith('/'):
                        link = f'{self.BASE_URL}{href}'
                    elif href.startswith('http'):
                        link = href
                    else:
                        continue
                    
                    # Extract date from URL if possible
                    try:
                        # Bloomberg URLs often have date pattern like /2025/01/18/
                        import re
                        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', href)
                        if date_match:
                            year, month, day = date_match.groups()
                            article_date = f"{year}-{month}-{day}"
                        else:
                            # Use current date as fallback
                            article_date = self.get_today_date()
                    except:
                        article_date = self.get_today_date()
                    
                    # Check if in target date range
                    if article_date in target_dates:
                        print(f"✅ 找到文章: {article_date}, {title[:50]}...")
                        news_list.append({
                            'title': title,
                            'link': link,
                            'date': article_date,
                            'tag': self.SOURCE_TAG
                        })
                        found_articles += 1
                    
                    # Limit to prevent too many requests
                    if found_articles >= 8:
                        break
                        
                except Exception as e:
                    print(f"❌ 处理文章时出错: {e}")
                    continue
            
            print(f"📊 找到 {found_articles} 篇科技文章")
                
        except Exception as e:
            print(f"❌ 抓取Bloomberg页面时出错: {e}")
        
        print(f"🎯 总共找到 {len(news_list)} 篇 Bloomberg 文章")
        return news_list
    
    def get_news_content(self, news_link: str) -> str:
        """Extract content from a Bloomberg article"""
        try:
            response = requests.get(news_link, headers=self.headers, timeout=30)
            
            if response.status_code == 403:
                return "Bloomberg内容需要订阅访问"
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try multiple content selectors for Bloomberg
            content_div = soup.find('div', class_='body-content') or \
                         soup.find('div', class_='story-body') or \
                         soup.find('section', class_='content') or \
                         soup.find('article')
            
            if content_div:
                paragraphs = content_div.find_all('p')
            else:
                # Fallback to all paragraphs
                paragraphs = soup.find_all('p')
            
            contents = []
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                # Filter out ads, subscribe messages, etc.
                if text and len(text) > 20 and not any(skip in text.lower() for skip in ['subscribe', 'newsletter', 'advertisement', 'bloomberg terminal']):
                    contents.append(text)
            
            # Limit content length for processing
            full_content = "\n".join(contents)
            if len(full_content) > 2000:
                full_content = full_content[:2000] + "..."
            
            return full_content if full_content else "无法获取文章内容"
            
        except Exception as e:
            print(f"❌ 获取文章内容失败: {news_link}, 错误: {e}")
            return "无法获取文章内容"
    
    def get_news_list(self) -> List[Dict[str, Any]]:
        """Get complete news list with content"""
        news_list = self.get_title_and_link_list()
        news_content_list = []
        
        for news in tqdm(news_list, desc="📈 Getting Bloomberg content"):
            news_content = self.get_news_content(news['link'])
            news['content'] = news_content
            news_content_list.append(news)
        
        return news_content_list


def get_news_list():
    """Legacy function for backward compatibility"""
    scraper = BloombergScraper()
    return scraper.get_news_list()


if __name__ == '__main__':
    scraper = BloombergScraper()
    news = scraper.get_news_list()
    print(f"✅ 获取到 {len(news)} 篇文章")
    for item in news:
        print(f"  - {item['title']}")
