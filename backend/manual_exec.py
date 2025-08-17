#!/usr/bin/env python3
"""
Manual execution of AI news sending

Quick script to manually trigger news processing and sending.
"""

from agents.feishu_sender import request_feishu_all_groups

if __name__ == '__main__':
    print("🚀 手动执行AI新闻发送...")
    try:
        response = request_feishu_all_groups()
        if response and response.status_code == 200:
            print("✅ 新闻发送完成")
        else:
            print("❌ 新闻发送可能失败，请检查日志")
    except Exception as e:
        print(f"❌ 执行失败: {e}")

# 执行方式: python manual_exec.py
