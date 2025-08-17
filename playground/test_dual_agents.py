#!/usr/bin/env python3
"""
Test script for dual AI agents

This script tests the dual agent setup (translate vs summary agents).
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_path)

from agents.news_handler import NewsHandler
from config.config_manager import ConfigManager


def test_config():
    """Test configuration for dual agents"""
    print("🧪 测试配置管理器...")
    
    config = ConfigManager()
    
    # Test translate agent config
    translate_config = config.get_translate_agent_config()
    print(f"翻译Agent配置:")
    print(f"  Agent ID: {translate_config.get('agent_id', 'N/A')}")
    print(f"  Auth Key: {'✅' if translate_config.get('personal_auth_key') else '❌'}")
    print(f"  Auth Secret: {'✅' if translate_config.get('personal_auth_secret') else '❌'}")
    
    # Test summary agent config
    summary_config = config.get_summary_agent_config()
    print(f"总结Agent配置:")
    print(f"  Agent ID: {summary_config.get('agent_id', 'N/A')}")
    print(f"  Auth Key: {'✅' if summary_config.get('personal_auth_key') else '❌'}")
    print(f"  Auth Secret: {'✅' if summary_config.get('personal_auth_secret') else '❌'}")


def test_dual_agents():
    """Test dual AI agent functionality"""
    print("\n🧪 测试双Agent功能...")
    
    try:
        handler = NewsHandler()
        
        # Test translate client
        print("🔧 初始化翻译客户端...")
        translate_client = handler.get_translate_client()
        print(f"✅ 翻译客户端初始化成功: {translate_client}")
        
        # Test summary client
        print("🔧 初始化总结客户端...")
        summary_client = handler.get_summary_client()
        print(f"✅ 总结客户端初始化成功: {summary_client}")
        
        # Test translate function
        print("🌍 测试标题翻译...")
        test_title = "AI-Powered Tools for Better Productivity"
        translated = handler.translate_title(test_title)
        print(f"  原文: {test_title}")
        print(f"  翻译: {translated}")
        
        # Test summarize function
        print("📝 测试内容总结...")
        test_content = "Artificial Intelligence has revolutionized the way we work and live. From machine learning algorithms to natural language processing, AI technologies are transforming industries across the globe. Companies are leveraging AI to improve efficiency, reduce costs, and enhance customer experiences."
        summary = handler.summarize_content(test_content)
        print(f"  原文: {test_content[:60]}...")
        print(f"  总结: {summary}")
        
    except Exception as e:
        print(f"❌ 双Agent测试失败: {e}")
        return False
    
    return True


def test_news_limit():
    """Test news limit functionality"""
    print("\n🧪 测试新闻数量限制...")
    
    try:
        handler = NewsHandler()
        
        # Test news fetching with limit
        print("📰 获取新闻列表（每个爬虫限制3条）...")
        all_news = handler.fetch_all_news()
        
        # Count news by source
        source_counts = {}
        for news in all_news:
            source = news.get('tag', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("📊 各来源新闻数量:")
        for source, count in source_counts.items():
            status = "✅" if count <= 3 else "⚠️"
            print(f"  {source}: {count} 条 {status}")
        
        total_news = len(all_news)
        expected_max = len(handler.scrapers) * 3
        print(f"总计: {total_news} 条新闻 (预期最多: {expected_max} 条)")
        
    except Exception as e:
        print(f"❌ 新闻限制测试失败: {e}")
        return False
    
    return True


def main():
    """Main test function"""
    print("🚀 开始双Agent和功能测试...")
    print("=" * 50)
    
    # Test configuration
    test_config()
    
    # Test dual agents
    agents_success = test_dual_agents()
    
    # Test news limit
    limit_success = test_news_limit()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 测试完成!")
    print(f"双Agent功能: {'✅ 成功' if agents_success else '❌ 失败'}")
    print(f"新闻限制功能: {'✅ 成功' if limit_success else '❌ 失败'}")
    
    if agents_success and limit_success:
        print("🎊 所有功能正常！")
    else:
        print("⚠️ 部分功能需要检查")


if __name__ == '__main__':
    main()
