#!/usr/bin/env python3
"""
Send Slack message for project completion notifications
"""

import requests
import json
import sys
import os
from datetime import datetime

def send_slack_message(webhook_url, message, channel=None):
    """Send message via Slack webhook"""
    payload = {
        "text": message,
        "username": "Claude Autodev Bot",
        "icon_emoji": ":robot_face:"
    }
    
    if channel:
        payload["channel"] = channel
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        if response.status_code == 200:
            print(f"✅ Slack message sent successfully")
            return True
        else:
            print(f"❌ Slack webhook error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def send_slack_rich_message(webhook_url, project_name, summary, channel=None):
    """Send rich formatted Slack message"""
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M")
    
    # Rich message with blocks
    payload = {
        "username": "Claude Autodev Bot",
        "icon_emoji": ":robot_face:",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎉 プロジェクト完了通知"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*プロジェクト:*\n{project_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*完了時刻:*\n{timestamp}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ {summary}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📁 *詳細:* `deliverables/{project_name}/`"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 Generated with Claude Code"
                    }
                ]
            }
        ]
    }
    
    if channel:
        payload["channel"] = channel
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        if response.status_code == 200:
            print(f"✅ Slack rich message sent successfully")
            return True
        else:
            print(f"❌ Slack webhook error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def get_slack_config():
    """Get Slack configuration from environment or config file"""
    # Check environment variables
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    channel = os.environ.get('SLACK_CHANNEL')
    
    # If not found, try config file
    if not webhook_url:
        config_paths = [
            "/Users/horioshuuhei/Projects/claude-autodev/config/slack_config.json",
            "/Users/horioshuuhei/.claude-autodev/slack_config.json"
        ]
        
        for config_path in config_paths:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    webhook_url = config.get('webhook_url')
                    channel = config.get('channel')
                    if webhook_url:
                        break
            except:
                continue
    
    return webhook_url, channel

def send_project_completion(project_name, summary="プロジェクトが完了しました"):
    """Send project completion notification to Slack"""
    webhook_url, channel = get_slack_config()
    
    if not webhook_url:
        print("❌ Slack webhook URL not found")
        print("Please set SLACK_WEBHOOK_URL environment variable or configure in config file")
        return False
    
    # Try rich message first, fallback to simple message
    if send_slack_rich_message(webhook_url, project_name, summary, channel):
        return True
    else:
        # Fallback to simple message
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M")
        simple_message = f"""🎉 Claude Autodev - プロジェクト完了

📋 プロジェクト: {project_name}
⏰ 完了時刻: {timestamp}

✅ {summary}

📁 詳細: deliverables/{project_name}/

🤖 Generated with Claude Code"""
        
        return send_slack_message(webhook_url, simple_message, channel)

def send_test_message():
    """Send test message to Slack"""
    webhook_url, channel = get_slack_config()
    
    if not webhook_url:
        print("❌ Slack webhook URL not found")
        return False
    
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    test_message = f"""🧪 Claude Autodev テスト

⏰ {timestamp}

✅ Slack Bot接続確認
🔄 システム正常動作中

💬 双方向通信コマンド:
• `claude new project-name description` - 新規プロジェクト
• `claude modify project-name changes` - 仕様変更  
• `claude projects` - プロジェクト一覧
• `claude help` - ヘルプ表示

🤖 Generated with Claude Code"""
    
    return send_slack_message(webhook_url, test_message, channel)

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "test":
        # Test mode
        success = send_test_message()
    elif len(sys.argv) >= 2:
        # Project completion mode
        project_name = sys.argv[1]
        summary = sys.argv[2] if len(sys.argv) > 2 else "プロジェクトが完了しました"
        success = send_project_completion(project_name, summary)
    else:
        print("Usage:")
        print("  python3 send_slack_message.py test                    # Send test message")
        print("  python3 send_slack_message.py <project> [summary]     # Send completion notification")
        sys.exit(1)
    
    sys.exit(0 if success else 1)