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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
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
        """Scrape trending products from Product Hunt (main page)"""
        news_list = []
        target_dates = self.get_recent_dates(7)  # Check last 7 days
        print(f"🔍 Product Hunt: 查找日期 {target_dates}")
        
        # Try main page instead of leaderboard to avoid 403
        try:
            import time
            time.sleep(2)  # Add delay to avoid being blocked
            
            url = f'{self.BASE_URL}'
            print(f"📄 正在抓取主页: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 403:
                print("⚠️  Product Hunt 主页也被阻止，跳过此来源")
                return []
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Look for product links on main page
            product_links = soup.find_all('a', href=True)
            product_links = [link for link in product_links if '/posts/' in link.get('href', '')]
            
            print(f"📋 找到 {len(product_links)} 个产品链接")
            
            found_products = 0
            seen_titles = set()  # Avoid duplicates
            
            for link in product_links[:20]:  # Limit to first 20 links
                try:
                    href = link.get('href')
                    title = link.text.strip()
                    
                    if not title or len(title) < 3 or title in seen_titles:
                        continue
                    
                    seen_titles.add(title)
                    
                    # Build full URL
                    if href.startswith('/'):
                        full_link = f'{self.BASE_URL}{href}'
                    else:
                        full_link = href
                    
                    # Filter AI/tech related products
                    ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'automation', 'tech', 'saas', 'productivity', 'analytics', 'data', 'software', 'app', 'tool', 'platform', 'bot', 'assistant', 'smart']
                    if any(keyword in title.lower() for keyword in ai_keywords):
                        formatted_date = self.get_today_date()
                        print(f"✅ 找到AI/科技产品: {title[:50]}...")
                        news_list.append({
                            'title': title,
                            'link': full_link,
                            'date': formatted_date,
                            'tag': self.SOURCE_TAG
                        })
                        found_products += 1
                        
                        # Limit to 10 products to avoid too many
                        if found_products >= 10:
                            break
                        
                except Exception as e:
                    print(f"❌ 处理产品时出错: {e}")
                    continue
            
            print(f"📊 主页找到 {found_products} 个AI/科技产品")
                
        except Exception as e:
            print(f"❌ 抓取Product Hunt主页时出错: {e}")
            print("💡 Product Hunt可能有反爬虫机制，暂时跳过此来源")
        
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
