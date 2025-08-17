"""
The Verge news scraper

This module provides the VergeScraper class for scraping AI news from The Verge.
"""

import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any


class VergeScraper:
    """The Verge news scraper for AI-related articles"""
    
    BASE_URL = "https://www.theverge.com"
    AI_ARCHIVES_URL = "https://www.theverge.com/ai-artificial-intelligence/archives"
    SOURCE_TAG = "Verge"
    
    def __init__(self):
        """Initialize the Verge scraper"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
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
        """Scrape news titles and links from The Verge"""
        news_list = []
        target_dates = self.get_recent_dates()
        print(f"🔍 The Verge: 查找日期 {target_dates}")
        
        for page in range(1, 5):  # Limit pages due to potential rate limiting
            url = f'{self.AI_ARCHIVES_URL}/{page}'
            print(f"📄 正在抓取页面: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                print(f"📡 响应状态码: {response.status_code}")
                
                if response.status_code == 403:
                    print("⚠️  The Verge 禁止访问，跳过")
                    break
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Try multiple selectors
                cards = soup.find_all('div', attrs={"class": re.compile(r".*duet--content-cards--content-card.*")})
                if not cards:
                    # Fallback selector
                    cards = soup.find_all('article')
                    print(f"📋 使用备用选择器找到 {len(cards)} 个文章")
                else:
                    print(f"📋 页面 {page} 找到 {len(cards)} 个卡片")
                
                found_in_page = 0
                for card in cards:
                    try:
                        link_block = card.find('a')
                        if not link_block:
                            continue
                            
                        title = link_block.text.strip()
                        href = link_block.get('href')
                        
                        # Find time element
                        time_elem = card.find('time')
                        if not time_elem:
                            continue
                            
                        news_time = time_elem.get('datetime')
                        if not news_time:
                            continue
                        
                        # Parse time format
                        try:
                            # Support multiple time formats
                            if 'T' in news_time:
                                news_date = datetime.strptime(news_time.split('T')[0], "%Y-%m-%d").strftime("%Y-%m-%d")
                            else:
                                news_date = datetime.strptime(news_time, "%Y-%m-%d").strftime("%Y-%m-%d")
                        except:
                            print(f"⚠️  无法解析时间格式: {news_time}")
                            continue
                        
                        # Check if in target date range
                        if news_date in target_dates and title and href:
                            print(f"✅ 找到文章: {news_date}, {title[:50]}...")
                            news_list.append({
                                'title': title,
                                'href': href,
                                'news_time': news_time,
                                'date': news_date,
                                'tag': self.SOURCE_TAG
                            })
                            found_in_page += 1
                            
                    except Exception as e:
                        print(f"❌ 处理文章时出错: {e}")
                        continue
                
                print(f"📊 页面 {page} 找到 {found_in_page} 篇目标日期的文章")
                
                if found_in_page == 0 and page > 1:
                    break
                    
            except Exception as e:
                print(f"❌ 抓取页面 {page} 时出错: {e}")
                continue

        print(f"🎯 总共找到 {len(news_list)} 篇 The Verge 文章")
        return news_list
    
    def get_news_content(self, news_href: str) -> str:
        """Extract content from a news article"""
        total_url = f'{self.BASE_URL}{news_href}'
        
        try:
            response = requests.get(total_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try multiple content selectors
            paragraphs = soup.find_all('div', class_='duet--article--article-body-component')
            if not paragraphs:
                # Fallback selector
                paragraphs = soup.find_all('p')
                
            contents = []
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if text and len(text) > 10:  # Filter out short text
                    contents.append(text)
            
            return "\n".join(contents)
        except Exception as e:
            print(f"❌ 获取文章内容失败: {total_url}, 错误: {e}")
            return "无法获取文章内容"
    
    def get_news_list(self) -> List[Dict[str, Any]]:
        """Get complete news list with content"""
        news_list = self.get_title_and_link_list()
        news_content_list = []
        
        for news in tqdm(news_list, desc="⚡ Getting Verge news content"):
            news_content = self.get_news_content(news['href'])
            news['link'] = f'{self.BASE_URL}{news["href"]}'
            news['content'] = news_content
            news_content_list.append(news)
        
        return news_content_list


def get_news_list():
    """Legacy function for backward compatibility"""
    scraper = VergeScraper()
    return scraper.get_news_list()


if __name__ == "__main__":
    scraper = VergeScraper()
    news = scraper.get_news_list()
    print(f"✅ 获取到 {len(news)} 篇新闻")
    for item in news:
        print(f"  - {item['title']}")
