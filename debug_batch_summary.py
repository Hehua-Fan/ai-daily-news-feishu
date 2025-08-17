#!/usr/bin/env python3
"""
调试批量总结功能，模拟真实的18篇新闻内容
"""

import sys
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from agents.news_handler import NewsHandler

def debug_batch_summary_with_real_data():
    """使用真实的复杂英文内容测试批量总结"""
    print("🧪 调试批量总结 - 使用类似真实数据")
    
    # 模拟真实的18篇新闻内容（长度和复杂度类似）
    test_news = [
        {
            'title': 'GPT-5 Failed the Hype Test',
            'content': 'OpenAI\'s highly anticipated GPT-5 model has been released to mixed reviews from the AI community. While the company promised significant improvements over GPT-4, early testing suggests that the gains are more incremental than revolutionary. Users report that GPT-5 shows better performance in specific tasks like code generation and mathematical reasoning, but falls short of the dramatic leap that was expected. The model still struggles with certain types of logical reasoning and factual accuracy, leading some experts to question whether we\'re approaching the limits of current transformer architectures. Despite these limitations, GPT-5 represents important progress in AI development.'
        },
        {
            'title': 'Anthropic New Rules for AI Safety',
            'content': 'Anthropic has announced comprehensive new safety guidelines for AI development, responding to growing concerns about the potential risks of advanced AI systems. The new framework requires all AI models to undergo rigorous safety testing before deployment, including assessments for potential misuse in areas like cybersecurity, misinformation generation, and autonomous weapons development. The company has also established a new oversight board comprising experts from academia, industry, and civil society to review high-risk AI applications. These measures represent one of the most stringent self-regulatory approaches in the AI industry and may influence future government regulations.'
        },
        {
            'title': 'AI Companies Chase Government Contracts',
            'content': 'Major AI companies are increasingly competing for lucrative government contracts, offering steep discounts to win business from federal agencies. Companies like Microsoft, Google, and Amazon are bidding aggressively on projects ranging from defense applications to administrative automation. The trend reflects both the growing demand for AI solutions in government and the companies\' desire to establish long-term relationships with public sector clients. However, this has raised concerns about data privacy, vendor lock-in, and the potential for conflicts of interest. Some agencies are developing procurement guidelines specifically for AI services to address these challenges.'
        },
        {
            'title': 'Recall AI Memory Assistant',
            'content': 'A new AI-powered personal assistant called Recall promises to revolutionize how we manage and retrieve information. Unlike traditional note-taking apps, Recall uses advanced natural language processing to understand context and relationships between different pieces of information. Users can ask questions in plain English and receive relevant information from their entire digital history, including emails, documents, and web browsing. The system learns from user behavior to improve its recommendations over time. Privacy advocates have raised concerns about the extensive data collection required for the service to function effectively.'
        },
        {
            'title': 'Macaron AI Personal Assistant',
            'content': 'Macaron AI has launched a new personal assistant that aims to provide more personalized and contextual responses than existing solutions. The system builds detailed user profiles based on interaction history, preferences, and behavioral patterns to deliver tailored assistance. Unlike generic AI assistants, Macaron remembers previous conversations and can maintain context across multiple sessions. The platform supports integration with popular productivity tools and can automate routine tasks based on user habits. The company emphasizes privacy protection, with all personal data processed locally rather than in the cloud.'
        }
    ]
    
    # 扩展到18篇（复制并修改）
    extended_news = []
    for i in range(18):
        base_item = test_news[i % len(test_news)].copy()
        base_item['title'] = f"{base_item['title']} - Variant {i+1}"
        extended_news.append(base_item)
    
    handler = NewsHandler()
    
    print(f"📝 模拟 {len(extended_news)} 篇新闻内容")
    
    # 调用批量总结并打印详细过程
    print("\n📝 开始批量总结...")
    
    try:
        # 准备批量内容
        batch_content_parts = []
        valid_items = []
        
        for i, news_item in enumerate(extended_news):
            content = news_item.get('content', '')
            if content and content.strip():
                batch_content_parts.append(f"文章{i+1}:\n{content}\n")
                valid_items.append(i)
        
        print(f"🔍 有效内容数量: {len(valid_items)}")
        
        # 创建批量查询
        batch_query = f"请对以下{len(valid_items)}篇文章分别进行总结，保持编号顺序，每个总结控制在100字以内：\n\n"
        batch_query += "\n".join(batch_content_parts)
        batch_query += "\n请按照 '文章1总结: ...', '文章2总结: ...', '文章3总结: ...' 的格式返回结果"
        
        print(f"📏 批量查询长度: {len(batch_query)} 字符")
        print(f"📋 查询示例 (前500字符):\n{batch_query[:500]}...")
        
        # 发送API请求
        print("\n📝 发送API请求...")
        batch_result = handler.summarize_content(batch_query)
        
        print(f"\n📥 API返回结果长度: {len(batch_result)} 字符")
        print(f"📋 返回结果示例 (前1000字符):\n{batch_result[:1000]}...")
        
        # 调试解析过程
        print(f"\n🔍 开始解析返回结果...")
        summaries = {}
        
        result_parts = batch_result.split('文章')
        print(f"📊 分割后部分数量: {len(result_parts)}")
        
        for idx, part in enumerate(result_parts):
            print(f"\n--- 部分 {idx} ---")
            print(f"内容: {part[:200]}...")
            
            if '总结:' in part and idx > 0:  # Skip the first empty part
                try:
                    # Extract article number and summary
                    article_num_match = re.match(r'(\d+)总结:\s*(.*)', part.strip(), re.DOTALL)
                    if article_num_match:
                        article_num = int(article_num_match.group(1))
                        summary_text = article_num_match.group(2).strip()
                        
                        print(f"✅ 成功解析: 文章{article_num}")
                        print(f"   总结: {summary_text[:100]}...")
                        
                        # Map back to original index
                        if article_num <= len(valid_items):
                            original_index = valid_items[article_num - 1]
                            summaries[original_index] = summary_text
                    else:
                        print(f"❌ 正则匹配失败")
                except Exception as e:
                    print(f"❌ 解析失败: {e}")
                    continue
        
        print(f"\n📊 成功解析总结数量: {len(summaries)}/{len(valid_items)}")
        
        # 显示解析结果
        for i in range(min(5, len(extended_news))):  # 只显示前5个
            summary = summaries.get(i, "总结生成失败")
            print(f"\n新闻{i+1}: {extended_news[i]['title'][:50]}...")
            print(f"总结: {summary}")
            
    except Exception as e:
        print(f"❌ 调试过程失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_batch_summary_with_real_data()
