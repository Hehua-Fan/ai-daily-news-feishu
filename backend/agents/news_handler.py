"""
News handler

This module provides the NewsHandler class for processing news data.
"""

import time
import re
import json
from tqdm import tqdm
from autoagentsai.client import ChatClient
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import NewsDatabase
from config.config_manager import ConfigManager
from scraper.techcrunch_scraper import TechCrunchScraper
from scraper.verge_scraper import VergeScraper
from scraper.github_trending_scraper import GitHubTrendingScraper
from scraper.product_hunt_scraper import ProductHuntScraper
from scraper.a16z_scraper import A16zScraper
from scraper.kr36_scraper import Kr36Scraper


class NewsHandler:
    """Handler for processing news from multiple sources"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize news handler"""
        if config_manager is None:
            config_manager = ConfigManager()
        
        self.config = config_manager
        self.database = NewsDatabase()
        
        # Initialize scrapers
        self.scrapers = [
            TechCrunchScraper(),
            VergeScraper(),
            GitHubTrendingScraper(),
            ProductHuntScraper(),
            A16zScraper(),
            Kr36Scraper()
        ]
        
        # Initialize AI client (unified for JSON processing)
        self._ai_client = None
        
    def get_ai_client(self) -> ChatClient:
        """Get unified AI client instance with lazy initialization"""
        if self._ai_client is None:
            try:
                ai_config = self.config.get_ai_agent_config()
                self._ai_client = ChatClient(
                    agent_id=ai_config["agent_id"],
                    personal_auth_key=ai_config["personal_auth_key"],
                    personal_auth_secret=ai_config["personal_auth_secret"]
                )
            except Exception as e:
                print(f"❌ AI 客户端初始化失败: {e}")
                print("💡 请检查 config.yml 中的 ai_agent 配置")
                raise e
        return self._ai_client
    
    @staticmethod
    def get_target_date() -> str:
        """Get target date for news (yesterday)"""
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    def translate_title(self, title: str) -> str:
        """Translate English title to Chinese using unified AI client"""
        prompt = f"请将以下英文新闻标题翻译成中文，只返回翻译结果，不要其他内容：\n\n{title}"
        
        try:
            client = self.get_ai_client()
            print(f"🌍 使用统一AI翻译标题")
            content = ""
            for event in client.invoke(prompt):
                if event['type'] == 'token':
                    content += event['content']
            return content.strip()
        except Exception as e:
            print(f"⚠️  标题翻译失败: {e}")
            return title  # Return original title if translation fails
    
    def summarize_content(self, content: str) -> str:
        """Summarize news content using unified AI client"""
        prompt = f"请对以下英文新闻内容用中文进行总结，总结内容不超过100个汉字，只返回总结结果：\n\n{content}"
        
        try:
            client = self.get_ai_client()
            print(f"📝 使用统一AI总结内容")
            summary = ""
            for event in client.invoke(prompt):
                if event['type'] == 'token':
                    summary += event['content']
            return summary.strip()
        except Exception as e:
            print(f"⚠️  内容总结失败: {e}")
            return "新闻内容总结失败"
    
    def fetch_all_news(self) -> List[Dict[str, Any]]:
        """Fetch news from all configured scrapers (limit 3 per scraper)"""
        all_news = []
        
        for scraper in self.scrapers:
            try:
                scraper_name = scraper.__class__.__name__
                print(f"📰 开始获取 {scraper_name} 新闻...")
                news_list = scraper.get_news_list()
                
                # Limit to 3 news items per scraper
                limited_news = news_list[:3]
                all_news.extend(limited_news)
                
                print(f"✅ {scraper_name} 获取到 {len(news_list)} 篇新闻，选取前 {len(limited_news)} 篇")
            except Exception as e:
                print(f"❌ {scraper_name} 获取新闻失败: {e}")
                continue
        
        print(f"🎯 总共获取到 {len(all_news)} 篇新闻")
        return all_news
    
    def process_news_item(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single news item with translation and summarization"""
        try:
            title = news_item['title']
            content = news_item['content']
            tag = news_item.get('tag', '')
            
            # Skip title translation for GitHub and Product Hunt (they are usually in English already)
            skip_translation_tags = ['GitHub', 'Product Hunt']
            
            if tag in skip_translation_tags:
                print(f"⏭️ 跳过 {tag} 标题翻译（已为英文）")
                zh_title = title  # Use original title
                
                # Still summarize content with a shorter delay
                print(f"⏳ 跳过翻译，等待5秒后进行总结...")
                time.sleep(5)
            else:
                # Translate title for other sources
                zh_title = self.translate_title(title)
                
                # Add 20 second delay between translation and summarization
                print(f"⏳ 翻译完成，等待20秒后进行总结...")
                time.sleep(20)
            
            summary = self.summarize_content(content)
            
            return {
                "date": self.get_target_date(),
                "title": title,
                "zh_title": zh_title,
                "link": news_item['link'],
                "content": content,
                "summary": summary,
                "tag": news_item['tag']
            }
        except Exception as e:
            print(f"❌ 处理新闻项目失败: {e}")
            return None
    
    def batch_process_news_with_ai(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process all news items with AI to get JSON format results"""
        print(f"🤖 批量处理 {len(news_items)} 篇新闻（JSON格式）")
        
        try:
            # Prepare news data for AI processing
            news_data = []
            for i, news_item in enumerate(news_items):
                item_data = {
                    "id": i + 1,
                    "source_name": news_item.get('tag', 'Unknown'),
                    "original_title": news_item.get('title', ''),
                    "content": news_item.get('content', '')[:1000]  # Limit content length
                }
                news_data.append(item_data)
            
            # Create AI query for JSON processing
            query = f"""请处理以下{len(news_data)}篇新闻，对每篇新闻进行翻译和总结。

要求：
1. 对于source_name为"GitHub"或"Product Hunt"的新闻，标题不需要翻译，直接使用原标题
2. 对于其他来源的英文标题，翻译成中文
3. 对所有内容进行总结，控制在80字左右，不少于60字，不够的就扩写，够的就精简
4. 严格按照JSON格式返回，不要添加任何其他文本

返回格式（JSON数组）：
[
  {{
    "id": 1,
    "source_name": "来源名称",
    "title": "处理后的标题（中文或原文）",
    "summary": "内容总结"
  }},
  ...
]

新闻数据：
"""
            
            for item in news_data:
                query += f"""
新闻 {item['id']}:
- 来源: {item['source_name']}
- 标题: {item['original_title']}
- 内容: {item['content']}
"""
            
            # Send to AI for processing
            print("🤖 发送AI处理请求...")
            ai_result = self.summarize_content(query)
            
            print(f"🔍 AI返回长度: {len(ai_result)} 字符")
            print(f"📋 AI返回示例: {ai_result[:200]}...")
            
            # Parse JSON result
            try:
                # Extract JSON from AI response
                
                # Find JSON array in response
                start_idx = ai_result.find('[')
                end_idx = ai_result.rfind(']') + 1
                
                if start_idx == -1 or end_idx == 0:
                    raise ValueError("未找到JSON数组")
                
                json_str = ai_result[start_idx:end_idx]
                parsed_results = json.loads(json_str)
                
                print(f"✅ 成功解析 {len(parsed_results)} 条结果")
                
                # Convert to final format
                processed_news = []
                for result in parsed_results:
                    news_id = result.get('id', 0) - 1  # Convert to 0-based index
                    if 0 <= news_id < len(news_items):
                        original_item = news_items[news_id]
                        processed_item = {
                            "date": self.get_target_date(),
                            "title": original_item.get('title', ''),
                            "zh_title": result.get('title', original_item.get('title', '')),
                            "link": original_item.get('link', ''),
                            "content": original_item.get('content', ''),
                            "summary": result.get('summary', '无总结'),
                            "tag": result.get('source_name', original_item.get('tag', ''))
                        }
                        processed_news.append(processed_item)
                
                return processed_news
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"📄 原始返回: {ai_result}")
                
                # Fallback: create basic results
                return self._create_fallback_results(news_items)
                
        except Exception as e:
            print(f"❌ AI处理失败: {e}")
            return self._create_fallback_results(news_items)
    
    def _create_fallback_results(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create fallback results when AI processing fails"""
        print("🔄 使用备用方案处理新闻")
        processed_news = []
        
        for news_item in news_items:
            processed_item = {
                "date": self.get_target_date(),
                "title": news_item.get('title', ''),
                "zh_title": news_item.get('title', ''),  # Use original title as fallback
                "link": news_item.get('link', ''),
                "content": news_item.get('content', ''),
                "summary": "AI处理失败，无法生成总结",
                "tag": news_item.get('tag', '')
            }
            processed_news.append(processed_item)
        
        return processed_news
    


    def process_news(self) -> List[Dict[str, Any]]:
        """Main method to process all news with JSON-based AI processing"""
        target_date = self.get_target_date()
        print(f"🚀 开始处理 {target_date} 的新闻")
        
        # Step 1: Fetch all raw news
        print("📥 阶段1：获取所有新闻内容")
        raw_news = self.fetch_all_news()
        
        if not raw_news:
            print("📭 没有获取到新闻数据")
            return []
        
        print(f"✅ 成功获取 {len(raw_news)} 条新闻")
        
        # Step 2: AI批量处理（JSON格式）- 包含翻译和总结
        print("\n🤖 阶段2：AI批量处理（翻译 + 总结）")
        processed_news = self.batch_process_news_with_ai(raw_news)
        
        if not processed_news:
            print("❌ AI处理失败，没有获得有效结果")
            return []
        
        print(f"✅ AI处理完成，得到 {len(processed_news)} 条结果")
        
        # Step 3: Save to database
        print("\n💾 阶段3：保存到数据库")
        if processed_news:
            try:
                success_count = self.database.insert_news_batch(processed_news)
                print(f"💾 成功保存 {success_count}/{len(processed_news)} 条新闻到数据库")
            except Exception as e:
                print(f"❌ 数据库保存失败: {e}")
        
        print(f"✅ 新闻处理完成，共处理 {len(processed_news)} 条新闻")
        return processed_news


# Legacy functions for backward compatibility
def get_today_date():
    """Legacy function for getting target date"""
    return NewsHandler.get_target_date()

def translate_news_title(title: str) -> str:
    """Legacy function for translating news title"""
    handler = NewsHandler()
    return handler.translate_title(title)

def summarize_news_content(content: str) -> str:
    """Legacy function for summarizing news content"""
    handler = NewsHandler()
    return handler.summarize_content(content)

def news_run():
    """Legacy function for running news processing"""
    handler = NewsHandler()
    return handler.process_news()


if __name__ == "__main__":
    handler = NewsHandler()
    news_list = handler.process_news()
    print(f"🎉 处理完成，共 {len(news_list)} 条新闻")
