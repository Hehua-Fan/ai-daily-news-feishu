#!/usr/bin/env python3
"""
测试GitHub Trending scraper集成

测试GitHub热门仓库的抓取、翻译和发送功能
"""

import json
import sys
import os

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

def test_github_scraper():
    """测试GitHub Trending scraper"""
    print("=== 🚀 测试GitHub Trending Scraper ===")
    
    try:
        from scraper.github_trending_scraper import GitHubTrendingScraper
        
        scraper = GitHubTrendingScraper()
        
        # 测试不同时间范围
        time_ranges = ["daily", "weekly"]
        
        for time_range in time_ranges:
            print(f"\n📊 测试 {time_range} trending:")
            repos = scraper.get_trending_repositories(time_range=time_range, limit=3)
            
            if repos:
                for i, repo in enumerate(repos):
                    print(f"  {i+1}. {repo['title']}")
                    print(f"     链接: {repo['link']}")
                    print(f"     内容预览: {repo['content'][:100]}...")
                    print()
                print(f"✅ {time_range} trending 测试成功，获取到 {len(repos)} 个仓库")
            else:
                print(f"❌ {time_range} trending 测试失败，未获取到仓库")
        
        return True
        
    except Exception as e:
        print(f"❌ GitHub scraper 测试失败: {e}")
        return False

def test_news_handler_integration():
    """测试GitHub scraper与news handler的集成"""
    print("\n=== 🧠 测试News Handler集成 ===")
    
    try:
        from agents.news_handler import NewsHandler
        
        handler = NewsHandler()
        
        # 检查scraper是否已添加
        scraper_names = [scraper.__class__.__name__ for scraper in handler.scrapers]
        print(f"📋 已注册的scrapers: {', '.join(scraper_names)}")
        
        if "GitHubTrendingScraper" in scraper_names:
            print("✅ GitHub Trending Scraper 已成功集成到 News Handler")
            
            # 测试获取部分新闻 (只测试GitHub部分)
            print("\n🔍 测试GitHub新闻获取:")
            github_scraper = None
            for scraper in handler.scrapers:
                if scraper.__class__.__name__ == "GitHubTrendingScraper":
                    github_scraper = scraper
                    break
            
            if github_scraper:
                github_news = github_scraper.get_news_list()
                print(f"📰 获取到 {len(github_news)} 个GitHub热门仓库")
                
                if github_news:
                    # 显示第一个仓库的信息
                    first_repo = github_news[0]
                    print(f"\n📖 示例仓库:")
                    print(f"   标题: {first_repo['title']}")
                    print(f"   链接: {first_repo['link']}")
                    print(f"   标签: {first_repo['tag']}")
                    print(f"   日期: {first_repo['date']}")
                    print(f"   内容: {first_repo['content'][:200]}...")
                    
                    return True
                else:
                    print("❌ 未获取到GitHub仓库数据")
                    return False
            else:
                print("❌ 未找到GitHub scraper实例")
                return False
        else:
            print("❌ GitHub Trending Scraper 未集成到 News Handler")
            return False
            
    except Exception as e:
        print(f"❌ News Handler 集成测试失败: {e}")
        return False

def test_ai_processing():
    """测试AI处理GitHub仓库信息"""
    print("\n=== 🤖 测试AI处理功能 ===")
    
    try:
        from agents.news_handler import NewsHandler
        
        handler = NewsHandler()
        
        # 模拟一个GitHub仓库信息
        mock_repo = {
            'title': 'microsoft/TypeScript',
            'content': '''Repository: microsoft/TypeScript
Description: TypeScript is a superset of JavaScript that compiles to clean JavaScript output.
Programming Language: TypeScript
Total Stars: 99,999
Today's Growth: 50 stars today''',
            'tag': 'GitHub',
            'link': 'https://github.com/microsoft/TypeScript',
            'date': '2025-08-18'
        }
        
        print(f"🔍 测试AI翻译: {mock_repo['title']}")
        
        # 测试标题翻译
        zh_title = handler.translate_title(mock_repo['title'])
        print(f"📝 翻译结果: {zh_title}")
        
        # 测试内容总结
        print(f"🔍 测试AI总结...")
        summary = handler.summarize_content(mock_repo['content'])
        print(f"📝 总结结果: {summary}")
        
        if zh_title and summary:
            print("✅ AI处理功能正常")
            return True
        else:
            print("❌ AI处理功能异常")
            return False
            
    except Exception as e:
        print(f"❌ AI处理测试失败: {e}")
        return False

def test_feishu_card_creation():
    """测试飞书卡片创建 (模拟GitHub内容)"""
    print("\n=== 📱 测试飞书卡片创建 ===")
    
    try:
        from agents.feishu_sender import FeishuSender
        from config.config_manager import ConfigManager
        
        config = ConfigManager()
        feishu_sender = FeishuSender(config)
        
        # 模拟包含GitHub仓库的新闻列表
        mock_news_list = [
            {
                'zh_title': 'Microsoft TypeScript - JavaScript超集编程语言',
                'tag': 'GitHub',
                'summary': 'TypeScript是微软开发的JavaScript超集，提供静态类型检查和现代ECMAScript特性，编译为纯净的JavaScript代码。今日新增50个star。',
                'link': 'https://github.com/microsoft/TypeScript'
            },
            {
                'zh_title': 'OpenAI GPT-4 - 大型语言模型实现',
                'tag': 'GitHub', 
                'summary': '一个开源的GPT-4模型实现，提供强大的自然语言处理能力。项目包含训练代码、预训练模型和使用示例。',
                'link': 'https://github.com/openai/gpt-4'
            }
        ]
        
        print(f"🎨 创建包含 {len(mock_news_list)} 个GitHub仓库的卡片...")
        
        # 创建卡片 (不发送)
        card_data = feishu_sender.create_news_card(mock_news_list)
        
        print("✅ 卡片创建成功！")
        print(f"📋 卡片类型: {card_data['msg_type']}")
        print(f"🎯 标题: {card_data['card']['header']['title']['content']}")
        print(f"🎨 主题色: {card_data['card']['header']['template']}")
        print(f"📊 元素数量: {len(card_data['card']['elements'])}")
        
        # 保存卡片预览
        with open('github_card_preview.json', 'w', encoding='utf-8') as f:
            json.dump(card_data, f, ensure_ascii=False, indent=2)
        print("📄 卡片数据已保存到 github_card_preview.json")
        
        return True
        
    except Exception as e:
        print(f"❌ 飞书卡片创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 GitHub Trending Scraper 集成测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("GitHub Scraper", test_github_scraper()))
    test_results.append(("News Handler 集成", test_news_handler_integration()))
    test_results.append(("AI处理功能", test_ai_processing()))
    test_results.append(("飞书卡片创建", test_feishu_card_creation()))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("🎯 测试结果总结:")
    all_passed = True
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！GitHub Trending集成成功！")
        print("💡 现在可以在每日推送中看到热门GitHub仓库了")
    else:
        print("\n⚠️  部分测试失败，请检查相关配置和代码")

if __name__ == "__main__":
    main()
