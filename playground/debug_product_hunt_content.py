#!/usr/bin/env python3
"""
Debug script to examine Product Hunt page content

This script helps us understand the actual page structure.
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_path)

from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def debug_product_hunt_page():
    """Debug Product Hunt weekly page content"""
    print("🕵️ 调试Product Hunt页面结构...")
    
    current_year = datetime.now().year
    current_week = datetime.now().isocalendar()[1]
    prev_week = current_week - 1 if current_week > 1 else 52
    prev_year = current_year if current_week > 1 else current_year - 1
    
    url = f"https://www.producthunt.com/leaderboard/weekly/{prev_year}/{prev_week}"
    print(f"📄 调试URL: {url}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-dev-shm-usage'
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            page = context.new_page()
            
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            print("🌐 正在访问页面...")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            print("⏳ 等待Cloudflare验证...")
            page.wait_for_timeout(5000)
            
            # Check for Cloudflare
            initial_content = page.content()
            if "Just a moment" in initial_content:
                print("🔄 检测到Cloudflare，等待更长时间...")
                page.wait_for_timeout(10000)
                page.reload(wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(3000)
            
            # Get page content
            content = page.content()
            browser.close()
            print(content)
            
            print(f"📄 页面内容长度: {len(content)} 字符")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'lxml')
            
            # Debug: Show first 2000 characters of text
            text_content = soup.get_text()
            print(f"\n📖 页面文本内容预览 (前500字符):")
            print("=" * 60)
            print(text_content[:500])
            print("=" * 60)
            
            # Look for all links
            all_links = soup.find_all('a', href=True)
            print(f"\n🔗 找到 {len(all_links)} 个链接")
            
            # Analyze link patterns
            link_patterns = {}
            product_links = []
            
            for link in all_links:
                href = link.get('href', '')
                text = link.text.strip()
                
                # Categorize links
                if '/posts/' in href:
                    product_links.append((text, href))
                
                # Count patterns
                if href.startswith('/'):
                    pattern = href.split('/')[1] if len(href.split('/')) > 1 else 'root'
                    link_patterns[pattern] = link_patterns.get(pattern, 0) + 1
            
            print(f"\n📊 链接模式统计:")
            for pattern, count in sorted(link_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  /{pattern}/: {count} 个链接")
            
            print(f"\n🎯 找到 {len(product_links)} 个产品链接:")
            for i, (text, href) in enumerate(product_links[:10]):
                print(f"  {i+1}. {text[:30]}... -> {href}")
            
            # Look for specific product names we know should be there
            known_products = ['Recall', 'Macaron AI', 'nFactorial AI', 'Autumn', 'Anything']
            print(f"\n🔍 查找已知产品:")
            for product in known_products:
                if product.lower() in text_content.lower():
                    print(f"  ✅ 找到: {product}")
                    
                    # Try to find the associated link
                    for link in all_links:
                        if product.lower() in link.text.lower():
                            print(f"     🔗 链接: {link.get('href', 'N/A')}")
                            break
                else:
                    print(f"  ❌ 未找到: {product}")
            
            # Check for any AI-related content
            ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'automation']
            ai_content = []
            lines = text_content.split('\n')
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ai_keywords) and len(line) > 5 and len(line) < 100:
                    ai_content.append(line)
            
            print(f"\n🤖 AI相关内容:")
            for content_line in ai_content[:10]:
                print(f"  - {content_line}")
            
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    debug_product_hunt_page()
