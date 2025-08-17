"""
News handler

This module provides the NewsHandler class for processing news data.
"""

import time
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
from scraper.bloomberg_scraper import BloombergScraper
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
            BloombergScraper(),
            Kr36Scraper()
        ]
        
        # Initialize AI clients (lazy loading)
        self._translate_client = None
        self._summary_client = None
        
    def get_translate_client(self) -> ChatClient:
        """Get translate AI client instance with lazy initialization"""
        if self._translate_client is None:
            try:
                translate_config = self.config.get_translate_agent_config()
                self._translate_client = ChatClient(
                    agent_id=translate_config["agent_id"],
                    personal_auth_key=translate_config["personal_auth_key"],
                    personal_auth_secret=translate_config["personal_auth_secret"]
                )
            except Exception as e:
                print(f"❌ 初始化翻译 AI 客户端失败: {e}")
                print("💡 请检查 config.yml 中的 translate_agent 配置")
                raise e
        return self._translate_client
    
    def get_summary_client(self) -> ChatClient:
        """Get summary AI client instance with lazy initialization"""
        if self._summary_client is None:
            try:
                summary_config = self.config.get_summary_agent_config()
                self._summary_client = ChatClient(
                    agent_id=summary_config["agent_id"],
                    personal_auth_key=summary_config["personal_auth_key"],
                    personal_auth_secret=summary_config["personal_auth_secret"]
                )
            except Exception as e:
                print(f"❌ 初始化总结 AI 客户端失败: {e}")
                print("💡 请检查 config.yml 中的 summary_agent 配置")
                raise e
        return self._summary_client
    
    @staticmethod
    def get_target_date() -> str:
        """Get target date for news (yesterday)"""
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    def translate_title(self, title: str) -> str:
        """Translate news title to Chinese using translate AI client"""
        prompt = f"请将以下英文新闻标题翻译成中文，只返回翻译结果，不要其他内容：\n\n{title}"
        
        try:
            client = self.get_translate_client()
            content = ""
            for event in client.invoke(prompt):
                if event['type'] == 'token':
                    content += event['content']
            return content.strip()
        except Exception as e:
            print(f"⚠️  标题翻译失败: {e}")
            return title  # Return original title if translation fails
    
    def summarize_content(self, content: str) -> str:
        """Summarize news content in Chinese using summary AI client"""
        prompt = f"请对以下英文新闻内容用中文进行总结，总结内容不超过100个汉字，只返回总结结果：\n\n{content}"
        
        try:
            client = self.get_summary_client()
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
            
            # Translate title and summarize content
            zh_title = self.translate_title(title)
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
    
    def process_news(self) -> List[Dict[str, Any]]:
        """Main method to process all news"""
        target_date = self.get_target_date()
        print(f"🚀 开始处理 {target_date} 的新闻")
        
        # Fetch raw news
        raw_news = self.fetch_all_news()
        
        if not raw_news:
            print("📭 没有获取到新闻数据")
            return []
        
        # Process news items with AI
        processed_news = []
        for i, news in enumerate(tqdm(raw_news, desc="🧠 Processing news with AI")):
            processed_item = self.process_news_item(news)
            if processed_item:
                processed_news.append(processed_item)
            
            # Add 10 second delay between news items to avoid server overload
            # Skip delay after the last item
            if i < len(raw_news) - 1:
                print(f"⏳ 等待10秒以避免访问过快...")
                time.sleep(10)
        
        # Save to database
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
