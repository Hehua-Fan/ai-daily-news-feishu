#!/usr/bin/env python3
"""
Test script for Playwright-enhanced Product Hunt scraper

This script tests the new Playwright implementation for Product Hunt.
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_path)

from scraper.product_hunt_scraper import ProductHuntScraper


def test_playwright_method():
    """Test the Playwright method specifically"""
    print(f"\n{'='*60}")
    print(f"🎭 测试Playwright方法")
    print(f"{'='*60}")
    
    try:
        scraper = ProductHuntScraper()
        
        # Test the playwright method directly
        print("📋 测试Playwright专用方法...")
        news_list = scraper.get_title_and_link_list_with_playwright()
        
        if news_list:
            print(f"✅ Playwright方法成功!")
            print(f"📊 获取到 {len(news_list)} 个产品")
            
            # Show details
            for i, news in enumerate(news_list):
                print(f"   {i+1}. {news['title']}")
                print(f"      🔗 {news['link']}")
                print(f"      📅 {news['date']} | 🏷️ {news['tag']}")
                print()
                
        else:
            print("⚠️  Playwright方法没有找到产品")
            
    except Exception as e:
        print(f"❌ Playwright方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return len(news_list) > 0


def test_main_method():
    """Test the main method (which should use Playwright first)"""
    print(f"\n{'='*60}")
    print(f"🚀 测试主方法 (优先使用Playwright)")
    print(f"{'='*60}")
    
    try:
        scraper = ProductHuntScraper()
        
        # Test the main method
        print("📋 测试主方法...")
        news_list = scraper.get_title_and_link_list()
        
        if news_list:
            print(f"✅ 主方法成功!")
            print(f"📊 获取到 {len(news_list)} 个产品")
            
            # Show first few
            for i, news in enumerate(news_list[:3]):
                print(f"   {i+1}. {news['title'][:50]}...")
                print(f"      🔗 {news['link']}")
                print(f"      📅 {news['date']} | 🏷️ {news['tag']}")
            
            if len(news_list) > 3:
                print(f"   ... 还有 {len(news_list) - 3} 个产品")
                
        else:
            print("⚠️  主方法没有找到产品")
            
    except Exception as e:
        print(f"❌ 主方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return len(news_list) > 0


def test_content_extraction():
    """Test content extraction with Playwright results"""
    print(f"\n{'='*60}")
    print(f"📝 测试内容提取")
    print(f"{'='*60}")
    
    try:
        scraper = ProductHuntScraper()
        news_list = scraper.get_title_and_link_list()
        
        if news_list:
            print("📝 测试第一个产品的内容提取...")
            first_news = news_list[0]
            content = scraper.get_news_content(first_news['link'])
            
            if content and content != "无法获取产品描述":
                print(f"✅ 内容提取成功!")
                print(f"📊 内容长度: {len(content)} 字符")
                print(f"📖 内容预览: {content[:150]}...")
            else:
                print(f"⚠️ 内容提取失败或为空")
        else:
            print("⚠️ 没有产品可测试内容提取")
            
    except Exception as e:
        print(f"❌ 内容提取测试失败: {e}")


def test_full_integration():
    """Test full get_news_list method"""
    print(f"\n{'='*60}")
    print(f"🔄 测试完整集成 (包含内容提取)")
    print(f"{'='*60}")
    
    try:
        scraper = ProductHuntScraper()
        
        print("📋 运行完整的get_news_list方法...")
        # This will include content extraction for all items
        news_list = scraper.get_news_list()
        
        if news_list:
            print(f"✅ 完整集成测试成功!")
            print(f"📊 获取到 {len(news_list)} 个完整产品信息")
            
            # Show one complete example
            if news_list:
                example = news_list[0]
                print(f"\n📋 示例产品:")
                print(f"   标题: {example['title']}")
                print(f"   链接: {example['link']}")
                print(f"   日期: {example['date']}")
                print(f"   标签: {example['tag']}")
                print(f"   内容: {example.get('content', 'N/A')[:100]}...")
                
        else:
            print("⚠️ 完整集成测试没有获取到产品")
            
    except Exception as e:
        print(f"❌ 完整集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return len(news_list) > 0


def main():
    """Main test function"""
    print("🚀 开始测试Playwright增强的Product Hunt爬虫...")
    
    # Test individual methods
    playwright_success = test_playwright_method()
    main_method_success = test_main_method()
    
    # Test content extraction
    test_content_extraction()
    
    # Test full integration
    full_integration_success = test_full_integration()
    
    # Summary
    print(f"\n{'='*60}")
    print("🎉 测试完成!")
    print(f"{'='*60}")
    print(f"Playwright方法: {'✅ 成功' if playwright_success else '❌ 失败'}")
    print(f"主方法: {'✅ 成功' if main_method_success else '❌ 失败'}")
    print(f"完整集成: {'✅ 成功' if full_integration_success else '❌ 失败'}")
    
    if playwright_success and main_method_success and full_integration_success:
        print("🎊 所有测试通过！Product Hunt Playwright版本工作正常！")
    elif playwright_success or main_method_success:
        print("🔧 部分测试通过，Product Hunt爬虫基本可用")
    else:
        print("🛠️ 需要进一步调试Product Hunt爬虫")


if __name__ == '__main__':
    main()
