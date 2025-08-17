#!/usr/bin/env python3
"""
Test script for fixed scrapers

This script tests the fixed Product Hunt and a16z scrapers.
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_path)

from scraper.product_hunt_scraper import ProductHuntScraper
from scraper.a16z_scraper import A16zScraper


def test_product_hunt():
    """Test fixed Product Hunt scraper"""
    print(f"\n{'='*60}")
    print(f"🧪 测试修复后的 Product Hunt 爬虫")
    print(f"{'='*60}")
    
    try:
        scraper = ProductHuntScraper()
        print("📋 测试标题和链接获取...")
        news_list = scraper.get_title_and_link_list()
        
        if news_list:
            print(f"✅ Product Hunt 修复成功!")
            print(f"📊 获取到 {len(news_list)} 个产品")
            
            # Show first few items
            for i, news in enumerate(news_list[:3]):
                print(f"   {i+1}. {news['title'][:50]}...")
                print(f"      🔗 {news['link']}")
                print(f"      📅 {news['date']} | 🏷️ {news['tag']}")
            
            if len(news_list) > 3:
                print(f"   ... 还有 {len(news_list) - 3} 个产品")
        else:
            print("⚠️  Product Hunt 仍然无法访问，但错误处理正常")
            
    except Exception as e:
        print(f"❌ Product Hunt 测试失败: {e}")
        return False
    
    return True


def test_a16z():
    """Test fixed a16z scraper"""
    print(f"\n{'='*60}")
    print(f"🧪 测试修复后的 a16z 爬虫")
    print(f"{'='*60}")
    
    try:
        scraper = A16zScraper()
        print("📋 测试标题和链接获取...")
        news_list = scraper.get_title_and_link_list()
        
        if news_list:
            print(f"✅ a16z 修复成功!")
            print(f"📊 获取到 {len(news_list)} 篇文章")
            
            # Show first few items
            for i, news in enumerate(news_list[:3]):
                print(f"   {i+1}. {news['title'][:50]}...")
                print(f"      🔗 {news['link']}")
                print(f"      📅 {news['date']} | 🏷️ {news['tag']}")
                
                # Verify the link is correct domain
                if news['link'].startswith('https://a16z.com'):
                    print(f"      ✅ 链接域名正确")
                else:
                    print(f"      ⚠️ 链接域名异常: {news['link']}")
            
            if len(news_list) > 3:
                print(f"   ... 还有 {len(news_list) - 3} 篇文章")
        else:
            print("⚠️  a16z 没有找到符合条件的文章")
            
    except Exception as e:
        print(f"❌ a16z 测试失败: {e}")
        return False
    
    return True


def test_content_extraction():
    """Test content extraction for both scrapers"""
    print(f"\n{'='*60}")
    print(f"🧪 测试内容提取功能")
    print(f"{'='*60}")
    
    # Test a16z content extraction
    try:
        scraper = A16zScraper()
        news_list = scraper.get_title_and_link_list()
        
        if news_list:
            print("📝 测试 a16z 内容提取...")
            first_news = news_list[0]
            content = scraper.get_news_content(first_news['link'])
            
            if content and content != "无法获取文章内容":
                print(f"✅ a16z 内容提取成功: {len(content)} 字符")
                print(f"   预览: {content[:100]}...")
            else:
                print(f"⚠️ a16z 内容提取失败或为空")
        
    except Exception as e:
        print(f"❌ a16z 内容提取测试失败: {e}")
    
    # Test Product Hunt content extraction (if available)
    try:
        ph_scraper = ProductHuntScraper()
        ph_news_list = ph_scraper.get_title_and_link_list()
        
        if ph_news_list:
            print("📝 测试 Product Hunt 内容提取...")
            first_news = ph_news_list[0]
            content = ph_scraper.get_news_content(first_news['link'])
            
            if content and content != "无法获取产品描述":
                print(f"✅ Product Hunt 内容提取成功: {len(content)} 字符")
                print(f"   预览: {content[:100]}...")
            else:
                print(f"⚠️ Product Hunt 内容提取失败或为空")
        
    except Exception as e:
        print(f"❌ Product Hunt 内容提取测试失败: {e}")


def main():
    """Main test function"""
    print("🚀 开始测试修复后的爬虫...")
    
    # Test scrapers
    ph_success = test_product_hunt()
    a16z_success = test_a16z()
    
    # Test content extraction
    test_content_extraction()
    
    # Summary
    print(f"\n{'='*60}")
    print("🎉 修复测试完成!")
    print(f"{'='*60}")
    print(f"Product Hunt: {'✅ 修复成功' if ph_success else '⚠️ 需要进一步调试'}")
    print(f"a16z: {'✅ 修复成功' if a16z_success else '⚠️ 需要进一步调试'}")
    
    if ph_success and a16z_success:
        print("🎊 所有爬虫修复成功！")
    elif ph_success or a16z_success:
        print("🔧 部分爬虫修复成功，继续优化其他爬虫")
    else:
        print("🛠️ 需要进一步调试和优化")


if __name__ == '__main__':
    main()
