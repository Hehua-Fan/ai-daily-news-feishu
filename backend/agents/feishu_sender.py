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
    """Feishu message sender for AI news cards (supports multiple groups)"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize Feishu sender with configuration"""
        if config_manager is None:
            config_manager = ConfigManager()
        
        self.config = config_manager
        
        # 获取所有飞书配置
        self.lark_configs = self.config.get_all_lark_configs()
        
        if not self.lark_configs:
            raise ValueError("至少需要配置一个有效的飞书机器人在 config.yml 中")
        
        # 主要配置（向后兼容）
        primary_config = self.config.get_lark_config()
        self.api_url = primary_config['api_url']
        self.api_secret = primary_config['api_secret']
        
        print(f"🚀 初始化飞书发送器：找到 {len(self.lark_configs)} 个群组配置")
        for config in self.lark_configs:
            print(f"   📱 {config['name']} ({config['key']})")
    
    def generate_signature(self, api_secret: str = None) -> tuple[int, str]:
        """Generate timestamp and signature for Feishu API"""
        if api_secret is None:
            api_secret = self.api_secret
            
        timestamp = int(time.time())
        string_to_sign = f'{timestamp}\n{api_secret}'
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
                        "content": f"🔥 {today_date} 每日AI新闻速览",
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
        """Send news card to primary Feishu group (backward compatibility)"""
        return self.send_card_to_group(news_list, self.api_url, self.api_secret, '主群组')
    
    def send_card_to_group(self, news_list: List[Dict[str, Any]], api_url: str, api_secret: str, group_name: str) -> requests.Response:
        """Send news card to specific Feishu group"""
        try:
            timestamp, sign = self.generate_signature(api_secret)
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
        
        response = requests.post(api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ 新闻卡片发送成功 → {group_name}")
        else:
            print(f"❌ 发送失败 → {group_name}: {response.status_code}, {response.text}")
        
        return response
    
    def send_card_to_all_groups(self, news_list: List[Dict[str, Any]]) -> Dict[str, requests.Response]:
        """Send news card to all configured Feishu groups"""
        results = {}
        
        print(f"📤 开始向 {len(self.lark_configs)} 个群组发送新闻...")
        
        for config in self.lark_configs:
            group_name = config['name']
            api_url = config['api_url']
            api_secret = config['api_secret']
            
            print(f"📱 正在发送到 {group_name}...")
            
            try:
                response = self.send_card_to_group(news_list, api_url, api_secret, group_name)
                results[config['key']] = response
                
                # 在发送之间添加短暂延迟，避免过于频繁的请求
                if len(self.lark_configs) > 1:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ 发送到 {group_name} 失败: {e}")
                # 创建一个模拟的错误响应
                class ErrorResponse:
                    def __init__(self, error_message):
                        self.status_code = 500
                        self.text = error_message
                
                results[config['key']] = ErrorResponse(str(e))
        
        # 统计发送结果
        success_count = sum(1 for r in results.values() if hasattr(r, 'status_code') and r.status_code == 200)
        print(f"📊 发送完成：{success_count}/{len(self.lark_configs)} 个群组发送成功")
        
        return results
    
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
    """Legacy function for sending news to primary Feishu group"""
    from .news_handler import NewsHandler
    
    sender = FeishuSender()
    handler = NewsHandler()
    return sender.send_news(handler.process_news)

def request_feishu_all_groups():
    """Send news to all configured Feishu groups"""
    from .news_handler import NewsHandler
    
    sender = FeishuSender()
    handler = NewsHandler()
    
    try:
        news_list = handler.process_news()
        if not news_list:
            print("📰 今日无新闻内容")
            news_list = []
        
        results = sender.send_card_to_all_groups(news_list)
        
        # 返回主群组的响应（向后兼容）
        primary_result = None
        for key, response in results.items():
            if key == 'primary' or primary_result is None:
                primary_result = response
        
        return primary_result
        
    except Exception as e:
        print(f"❌ 获取新闻时发生错误: {e}")
        # 发送错误卡片到所有群组
        error_card_data = FeishuSender().create_error_card(f"获取新闻失败: {str(e)}")
        
        sender = FeishuSender()
        results = {}
        for config in sender.lark_configs:
            try:
                timestamp, sign = sender.generate_signature(config['api_secret'])
                data = {
                    "timestamp": timestamp,
                    "sign": sign,
                    **error_card_data
                }
                response = requests.post(config['api_url'], json=data, headers={"Content-Type": "application/json"})
                results[config['key']] = response
            except Exception as send_error:
                print(f"❌ 发送错误卡片到 {config['name']} 失败: {send_error}")
        
        # 返回任意一个响应
        return list(results.values())[0] if results else None


if __name__ == '__main__':
    # Set scheduled task for 9:00 AM Beijing time
    schedule.every().day.at("05:02").do(request_feishu)

    print("🕘 定时任务已启动，将在每天早上9点（北京时间）执行...")
    print("📱 AI新闻卡片将自动推送到飞书群聊")
    print("⏹️  按 Ctrl+C 停止定时任务")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
