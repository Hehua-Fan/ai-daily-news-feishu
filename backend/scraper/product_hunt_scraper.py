"""
Product Hunt news scraper

This module provides the ProductHuntScraper class for scraping trending products from Product Hunt.
"""

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any


class ProductHuntScraper:
    """Product Hunt scraper for trending AI and tech products"""
    
    BASE_URL = "https://www.producthunt.com"
    SOURCE_TAG = "ProductHunt"
    
    def __init__(self):
        """Initialize the Product Hunt scraper"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.producthunt.com/',
        }
    
    @staticmethod
    def get_today_date() -> str:
        """Get yesterday's date in YYYY-MM-DD format"""
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    @staticmethod
    def get_recent_dates(days: int = 3) -> List[str]:
        """Get list of recent dates for product filtering"""
        today = datetime.now()
        return [
            (today - timedelta(days=i)).strftime("%Y-%m-%d") 
            for i in range(days)
        ]
    
    def get_title_and_link_list(self) -> List[Dict[str, Any]]:
        """Scrape trending products from Product Hunt"""
        news_list = []
        target_dates = self.get_recent_dates()
        print(f"🔍 Product Hunt: 查找日期 {target_dates}")
        
        # Check today and recent days
        for days_ago in range(3):
            target_date = datetime.now() - timedelta(days=days_ago)
            date_str = target_date.strftime("%Y/%m/%d")
            formatted_date = target_date.strftime("%Y-%m-%d")
            
            if formatted_date not in target_dates:
                continue
            
            url = f'{self.BASE_URL}/leaderboard/daily/{date_str}'
            print(f"📄 正在抓取页面: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Look for product cards
                products = soup.find_all('div', {'data-test': 'post-item'})
                if not products:
                    # Fallback selector
                    products = soup.find_all('li', class_='styles_item__1t9xF')
                
                print(f"📋 找到 {len(products)} 个产品")
                
                found_in_page = 0
                for product in products:
                    try:
                        # Find product title link
                        title_link = product.find('a', href=True)
                        if not title_link:
                            continue
                        
                        title = title_link.text.strip()
                        href = title_link.get('href')
                        
                        if not title or not href:
                            continue
                        
                        # Build full URL
                        if href.startswith('/'):
                            link = f'{self.BASE_URL}{href}'
                        else:
                            link = href
                        
                        # Filter AI/tech related products (simple keyword filter)
                        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'automation', 'tech', 'saas', 'productivity', 'analytics', 'data']
                        if any(keyword in title.lower() for keyword in ai_keywords):
                            print(f"✅ 找到AI/科技产品: {formatted_date}, {title[:50]}...")
                            news_list.append({
                                'title': title,
                                'link': link,
                                'date': formatted_date,
                                'tag': self.SOURCE_TAG
                            })
                            found_in_page += 1
                            
                    except Exception as e:
                        print(f"❌ 处理产品时出错: {e}")
                        continue
                
                print(f"📊 {formatted_date} 找到 {found_in_page} 个AI/科技产品")
                    
            except Exception as e:
                print(f"❌ 抓取页面 {url} 时出错: {e}")
                continue
        
        print(f"🎯 总共找到 {len(news_list)} 个 Product Hunt 产品")
        return news_list
    
    def get_news_content(self, news_link: str) -> str:
        """Extract content from a product page"""
        try:
            response = requests.get(news_link, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try to find product description
            description_elem = soup.find('div', {'data-test': 'post-description'})
            if not description_elem:
                # Fallback selectors
                description_elem = soup.find('div', class_='styles_htmlText__3lSgj') or \
                                  soup.find('p', class_='styles_postTagline__3o6_Z')
            
            if description_elem:
                description = description_elem.text.strip()
            else:
                description = "产品描述暂无"
            
            # Try to get maker info
            maker_info = soup.find('div', {'data-test': 'makers-list'})
            maker_text = ""
            if maker_info:
                makers = maker_info.find_all('a')
                if makers:
                    maker_names = [maker.text.strip() for maker in makers]
                    maker_text = f"开发者: {', '.join(maker_names)}"
            
            # Combine information
            content_parts = [description]
            if maker_text:
                content_parts.append(maker_text)
            
            return "\n".join(content_parts)
            
        except Exception as e:
            print(f"❌ 获取产品内容失败: {news_link}, 错误: {e}")
            return "无法获取产品描述"
    
    def get_news_list(self) -> List[Dict[str, Any]]:
        """Get complete product list with content"""
        news_list = self.get_title_and_link_list()
        news_content_list = []
        
        for news in tqdm(news_list, desc="🚀 Getting Product Hunt content"):
            news_content = self.get_news_content(news['link'])
            news['content'] = news_content
            news_content_list.append(news)
        
        return news_content_list


def get_news_list():
    """Legacy function for backward compatibility"""
    scraper = ProductHuntScraper()
    return scraper.get_news_list()


if __name__ == '__main__':
    scraper = ProductHuntScraper()
    news = scraper.get_news_list()
    print(f"✅ 获取到 {len(news)} 个产品")
    for item in news:
        print(f"  - {item['title']}")
