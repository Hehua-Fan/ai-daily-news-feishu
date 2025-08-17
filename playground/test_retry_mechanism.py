#!/usr/bin/env python3
"""
测试Product Hunt产品重试机制
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_path)

from scraper.product_hunt_scraper import ProductHuntScraper


def test_retry_mechanism():
    """测试重试机制的效果"""
    print("🔄 测试Product Hunt产品重试机制...")
    
    scraper = ProductHuntScraper()
    
    # 先获取产品列表
    print("📋 获取产品列表...")
    products = scraper.get_title_and_link_list()
    
    if not products:
        print("❌ 没有获取到产品列表")
        return
    
    print(f"✅ 获取到 {len(products)} 个产品")
    
    # 测试前2个产品的重试机制
    print(f"\n🔄 测试前2个产品的重试机制：")
    
    for i, product in enumerate(products[:2]):
        print(f"\n{'='*60}")
        print(f"产品 {i+1}: {product['title']}")
        print(f"链接: {product['link']}")
        print(f"{'='*60}")
        
        # 获取详细内容（现在有重试机制）
        detailed_content = scraper.get_news_content(product['link'])
        
        print(f"最终结果: {detailed_content}")
        
        # 分析结果
        if ("Verifying you are human" in detailed_content or 
            "Just a moment" in detailed_content or
            "www.producthunt.com" in detailed_content):
            print("❌ 仍然是Cloudflare页面")
        elif "Product Hunt 产品" in detailed_content:
            print("⚠️ 使用了备选方案（URL提取）")
        else:
            print("✅ 成功获取到真实产品信息！")


if __name__ == '__main__':
    test_retry_mechanism()
