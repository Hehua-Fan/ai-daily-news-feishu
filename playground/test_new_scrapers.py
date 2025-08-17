#!/usr/bin/env python3
"""
Test script for new scrapers

This script tests the new scrapers: Product Hunt, a16z, Bloomberg, and 36kr.
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_path)

from scraper.product_hunt_scraper import ProductHuntScraper
from scraper.a16z_scraper import A16zScraper
from scraper.bloomberg_scraper import BloombergScraper
from scraper.kr36_scraper import Kr36Scraper


def test_scraper(scraper, name):
    """Test a single scraper"""
    print(f"\n{'='*50}")
    print(f"🧪 测试 {name} 爬虫")
    print(f"{'='*50}")
    
    try:
        # Only test title and link extraction (faster)
        news_list = scraper.get_title_and_link_list()
        print(f"✅ {name} 爬虫测试成功!")
        print(f"📊 获取到 {len(news_list)} 条新闻标题")
        
        # Show first few items
        for i, news in enumerate(news_list[:3]):
            print(f"   {i+1}. {news['title'][:60]}...")
            print(f"      🔗 {news['link']}")
            print(f"      📅 {news['date']} | 🏷️ {news['tag']}")
        
        if len(news_list) > 3:
            print(f"   ... 还有 {len(news_list) - 3} 条新闻")
            
    except Exception as e:
        print(f"❌ {name} 爬虫测试失败: {e}")


def main():
    """Main test function"""
    print("🚀 开始测试新增的爬虫...")
    
    # Test each scraper
    scrapers = [
        (ProductHuntScraper(), "Product Hunt"),
        (A16zScraper(), "a16z"),
        (BloombergScraper(), "Bloomberg"),
        (Kr36Scraper(), "36kr")
    ]
    
    for scraper, name in scrapers:
        test_scraper(scraper, name)
    
    print(f"\n{'='*50}")
    print("🎉 所有爬虫测试完成!")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
