"""
Feishu message sender

This module provides the FeishuSender class for sending messages to Feishu groups.
"""

import hashlib
import base64
import hmac
import time
import requests
import schedule
from datetime import datetime
from typing import List, Dict, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config_manager import ConfigManager


class FeishuSender:
    """Feishu message sender for AI news cards"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize Feishu sender with configuration"""
        if config_manager is None:
            config_manager = ConfigManager()
        
        self.config = config_manager
        lark_config = self.config.get_lark_config()
        
        self.api_url = lark_config['api_url']
        self.api_secret = lark_config['api_secret']
        
        if not self.api_url or self.api_url.startswith('YOUR_'):
            raise ValueError("Feishu API URL must be configured in config.yml")
        if not self.api_secret or self.api_secret.startswith('YOUR_'):
            raise ValueError("Feishu API Secret must be configured in config.yml")
    
    def generate_signature(self) -> tuple[int, str]:
        """Generate timestamp and signature for Feishu API"""
        timestamp = int(time.time())
        string_to_sign = f'{timestamp}\n{self.api_secret}'
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), 
            digestmod=hashlib.sha256
        ).digest()
        
        signature = base64.b64encode(hmac_code).decode('utf-8')
        return timestamp, signature
    
    def create_news_card(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create beautiful news card for Feishu"""
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        if not news_list:
            # Empty news card
            return {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True,
                        "enable_forward": True
                    },
                    "header": {
                        "template": "blue",
                        "title": {
                            "content": f"📱 {today_date} AI新闻播报",
                            "tag": "plain_text"
                        }
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "content": "😴 今日暂无AI新闻更新\n\n请稍后再来查看最新资讯",
                                "tag": "lark_md"
                            }
                        }
                    ]
                }
            }
        
        # Build news card elements
        elements = []
        
        # Group news by source
        news_by_source = {}
        for news in news_list:
            source = news['tag']
            if source not in news_by_source:
                news_by_source[source] = []
            news_by_source[source].append(news)
        
        # Define source info with real website icons and homepage URLs
        source_info = {
            'TechCrunch': {
                'emoji': '🗞️',
                'name': 'TechCrunch',
                'homepage': 'https://techcrunch.com'
            },
            'Verge': {
                'emoji': '🔺',
                'name': 'The Verge',
                'homepage': 'https://www.theverge.com'
            },
            'GitHub': {
                'emoji': '🐙',
                'name': 'GitHub Trending',
                'homepage': 'https://github.com/trending'
            },
            'ProductHunt': {
                'emoji': '🚀',
                'name': 'Product Hunt',
                'homepage': 'https://www.producthunt.com'
            },
            'a16z': {
                'emoji': '💡',
                'name': 'Andreessen Horowitz',
                'homepage': 'https://a16z.com/news-content/'
            },
            'Bloomberg': {
                'emoji': '📈',
                'name': 'Bloomberg Technology',
                'homepage': 'https://www.bloomberg.com/technology'
            },
            '36kr': {
                'emoji': '🏢',
                'name': '36氪',
                'homepage': 'https://36kr.com'
            }
        }
        
        # Create elements for each source group
        first_source = True
        for source, news_items in news_by_source.items():
            # Add separator between sources (except for first source)
            if not first_source:
                elements.append({"tag": "hr"})
            first_source = False
            
            # Add source header
            source_data = source_info.get(source, {'emoji': '📰', 'name': source, 'homepage': '#'})
            elements.append({
                "tag": "div",
                "text": {
                    "content": f"{source_data['emoji']} **{source_data['name']}**",
                    "tag": "lark_md"
                }
            })
            
            # Add news items for this source
            for i, news in enumerate(news_items):
                # News title and summary combined in one div (no empty lines)
                elements.append({
                    "tag": "div",
                    "text": {
                        "content": f"**{i+1}. {news['zh_title']}**\n{news['summary']}",
                        "tag": "lark_md"
                    }
                })
                
                # Read more button
                elements.append({
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "📖 阅读原文",
                                "tag": "plain_text"
                            },
                            "url": news['link'],
                            "type": "default"
                        }
                    ]
                })
            
            # Add homepage link for this source
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "content": f"🔗 查看更多{source_data['name']}资讯",
                            "tag": "plain_text"
                        },
                        "url": source_data['homepage'],
                        "type": "primary"
                    }
                ]
            })
        
        # Add footer
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {
                "content": f"🤖 *由AI新闻机器人自动播报* | ⏰ {datetime.now().strftime('%H:%M')} 更新",
                "tag": "lark_md"
            }
        })
        
        return {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True,
                    "enable_forward": True
                },
                "header": {
                    "template": "turquoise",
                    "title": {
                        "content": f"🔥 {today_date} AI新闻速报",
                        "tag": "plain_text"
                    }
                },
                "elements": elements
            }
        }
    
    def create_error_card(self, error_message: str = "新闻服务暂时不可用") -> Dict[str, Any]:
        """Create error card for failure cases"""
        timestamp, sign = self.generate_signature()
        
        return {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True,
                    "enable_forward": True
                },
                "header": {
                    "template": "red",
                    "title": {
                        "content": "⚠️ AI新闻获取失败",
                        "tag": "plain_text"
                    }
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": f"🔧 {error_message}\n\n请稍后重试或联系管理员检查服务状态",
                            "tag": "lark_md"
                        }
                    }
                ]
            }
        }
    
    def send_card(self, news_list: List[Dict[str, Any]]) -> requests.Response:
        """Send news card to Feishu group"""
        try:
            timestamp, sign = self.generate_signature()
            card_data = self.create_news_card(news_list)
            
            # Add signature to card data
            data = {
                "timestamp": timestamp,
                "sign": sign,
                **card_data
            }
            
        except Exception as e:
            print(f"🔥 创建卡片时发生错误: {e}")
            data = self.create_error_card(str(e))

        headers = {"Content-Type": "application/json"}
        
        response = requests.post(self.api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            print("✅ 新闻卡片发送成功")
        else:
            print(f"❌ 发送失败: {response.status_code}, {response.text}")
        
        return response
    
    def send_news(self, news_handler_func) -> requests.Response:
        """Send news using provided news handler function"""
        try:
            news_list = news_handler_func()
            if not news_list:
                print("📰 今日无新闻内容")
            return self.send_card(news_list)
            
        except Exception as e:
            print(f"❌ 获取新闻时发生错误: {e}")
            data = self.create_error_card(f"获取新闻失败: {str(e)}")
            
            headers = {"Content-Type": "application/json"}
            return requests.post(self.api_url, json=data, headers=headers)


# Legacy functions for backward compatibility
def gen_sign():
    """Legacy function for generating signature"""
    sender = FeishuSender()
    return sender.generate_signature()

def create_news_card(news_list):
    """Legacy function for creating news card"""
    sender = FeishuSender()
    return sender.create_news_card(news_list)

def request_feishu():
    """Legacy function for sending news to Feishu"""
    from .news_handler import NewsHandler
    
    sender = FeishuSender()
    handler = NewsHandler()
    return sender.send_news(handler.process_news)


if __name__ == '__main__':
    # Set scheduled task for 9:00 AM Beijing time
    schedule.every().day.at("09:00").do(request_feishu)

    print("🕘 定时任务已启动，将在每天早上9点（北京时间）执行...")
    print("📱 AI新闻卡片将自动推送到飞书群聊")
    print("⏹️  按 Ctrl+C 停止定时任务")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
