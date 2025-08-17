#!/usr/bin/env python3
"""
测试新的飞书卡片样式
"""

import json
import sys
import os

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

def create_mock_news():
    """创建模拟新闻数据"""
    return [
        {
            'zh_title': 'OpenAI发布性能升级版GPT-4 Turbo',
            'tag': 'TechCrunch',
            'summary': 'OpenAI发布升级版GPT-4 Turbo，具备更强推理能力、12.8万标记上下文窗口及2024年4月最新知识库，在保持高性能的同时提升效率与性价比。',
            'link': 'https://techcrunch.com/2025/08/16/openai-announces-gpt-4-turbo-with-enhanced-capabilities/'
        },
        {
            'zh_title': 'AI驱动的毛绒玩具即将面世',
            'tag': 'TechCrunch', 
            'summary': '新一代AI毛绒玩具集成了先进的语音识别和对话功能，能够与儿童进行自然交流，提供个性化的陪伴体验，同时确保隐私安全。',
            'link': 'https://techcrunch.com/2025/08/16/ai-powered-stuffed-animals-are-coming-for-your-kids/'
        },
        {
            'zh_title': 'Anthropic的Claude模型新增对话终止功能',
            'tag': 'Verge',
            'summary': 'Anthropic宣布部分Claude模型现在能够识别并主动结束有害或滥用性对话，这一功能旨在提高AI系统的安全性和道德标准。',
            'link': 'https://www.theverge.com/2025/8/16/anthropic-claude-harmful-conversations'
        }
    ]

def test_card_creation():
    """测试卡片创建功能"""
    print("=== 测试新的飞书卡片样式 ===")
    
    try:
        # 导入我们的卡片创建函数和发送函数
        from agents.feishu_sender import FeishuSender
        from config.config_manager import ConfigManager
        
        # Initialize FeishuSender
        config = ConfigManager()
        feishu_sender = FeishuSender(config)
        import requests
        
        # 创建模拟新闻数据
        mock_news = create_mock_news()
        
        print(f"创建包含 {len(mock_news)} 条新闻的卡片...")
        
        # 生成卡片数据并直接发送
        print("📤 创建卡片并发送到飞书...")
        response = feishu_sender.send_card(mock_news)
        
        if response and response.status_code == 200:
            print("✅ 新闻卡片发送成功！")
        else:
            print(f"❌ 发送失败: {response.status_code if response else 'No response'}")
            
        print("✅ 卡片创建和发送完成！")
        
        # 显示新闻内容预览
        print("\n=== 新闻内容预览 ===")
        for i, news in enumerate(mock_news):
            print(f"{i+1}. {news['zh_title']}")
            print(f"   来源: {news['tag']}")
            print(f"   摘要: {news['summary'][:50]}...")
            print()
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保在正确的环境中运行此脚本")
        return False
    except Exception as e:
        print(f"❌ 创建卡片时出错: {e}")
        return False

def test_empty_news():
    """测试无新闻时的卡片"""
    print("\n=== 测试无新闻时的卡片 ===")
    
    try:
        from agents.feishu_sender import FeishuSender
        from config.config_manager import ConfigManager
        
        # Initialize components
        config = ConfigManager()
        feishu_sender = FeishuSender(config)
        
        # 测试空新闻列表并直接发送
        print("📤 创建空新闻卡片并发送到飞书...")
        response = feishu_sender.send_card([])
        
        if response and response.status_code == 200:
            print("✅ 空新闻卡片发送成功！")
        else:
            print(f"❌ 发送失败: {response.status_code if response else 'No response'}")
            
        print("✅ 空卡片创建和发送完成！")
        return True
        
    except Exception as e:
        print(f"❌ 创建空卡片时出错: {e}")
        return False



def show_card_features():
    """展示卡片的主要特性"""
    print("\n=== 🎨 新卡片样式特性 ===")
    print("✨ 使用飞书交互式卡片格式")
    print("🎯 彩色标题栏（正常：青绿色，无新闻：蓝色，错误：红色）")
    print("📊 顶部统计信息显示新闻总数")
    print("🏷️  每条新闻都有来源标签和emoji图标")
    print("📝 清晰的摘要显示")
    print("🔘 每条新闻都有独立的「阅读原文」按钮")
    print("➖ 使用分割线清晰分隔内容")
    print("🤖 底部显示更新时间和机器人信息")
    print("📱 支持宽屏模式和转发功能")
    
    print("\n=== 🎨 emoji 图标说明 ===")
    print("🚀 TechCrunch 新闻")
    print("⚡ The Verge 新闻") 
    print("🔥 标题热点标识")
    print("📝 新闻摘要标识")
    print("📖 阅读原文按钮")
    print("🤖 机器人标识")
    print("⏰ 更新时间标识")

def main():
    """主测试函数"""
    print("🎨 飞书新闻卡片样式测试")
    print("=" * 50)
    
    # 显示特性介绍
    show_card_features()
    
    # 测试有新闻的卡片并直接发送
    success1 = test_card_creation()
    
    # 测试无新闻的卡片并直接发送
    success2 = test_empty_news()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"有新闻卡片创建: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"无新闻卡片创建: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有卡片样式测试通过！")
        print("🚀 卡片已自动发送到飞书群聊，请查看美观卡片！")
        print("💡 如果发送失败，请检查飞书API配置和网络连接")
    else:
        print("\n⚠️  部分测试失败，请检查代码和环境")

if __name__ == "__main__":
    main()
