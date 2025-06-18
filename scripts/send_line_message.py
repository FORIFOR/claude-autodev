#!/usr/bin/env python3
"""
Send LINE message using Messaging API for project completion notifications
"""

import requests
import json
import sys
from datetime import datetime

# LINE Bot Configuration
CHANNEL_ACCESS_TOKEN = "FzpiO7StfY1GtQ1URU5um4IiwXipxgM+bZeuMd1h2b947eoy4doDrd96Sw9x8VKix/aYs4T3zkNL/vZRHo20bF28t35D1urum/WptrpnEthFZUFAR3NpBxc0kQ6U9Q2wXZ6422tOx/5nRCkn5qtsIAdB04t89/1O/w1cDnyilFU"
DESTINATION_USER_ID = "U2f0d021267564d91134b178d7f65fc84"

def send_line_message(user_id, message):
    """Send message via LINE Messaging API"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            print(f"✅ LINE message sent successfully")
            return True
        elif response.status_code == 429:
            print(f"⚠️  月次制限に達しています。翌月のリセットをお待ちください。")
            # ログファイルに記録
            with open("/Users/horioshuuhei/Projects/claude-autodev/logs/notifications.log", "a") as f:
                f.write(f"{datetime.now().isoformat()}: LINE API月次制限 - メッセージ: {message[:50]}...\n")
            return False
        else:
            print(f"❌ LINE API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def send_project_completion(project_name, summary="プロジェクトが完了しました"):
    """Send project completion notification"""
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M")
    
    message = f"""🎉 Claude Autodev - プロジェクト完了

📋 プロジェクト: {project_name}
⏰ 完了時刻: {timestamp}

✅ {summary}

🔗 詳細: deliverables/{project_name}/

🤖 Generated with Claude Code"""
    
    return send_line_message(DESTINATION_USER_ID, message)

def send_test_message():
    """Send test message"""
    message = f"""🧪 Claude Autodev テスト

⏰ {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}

✅ LINE Messaging API接続確認
🔄 システム正常動作中

🤖 Generated with Claude Code"""
    
    return send_line_message(DESTINATION_USER_ID, message)

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
        print("  python3 send_line_message.py test                    # Send test message")
        print("  python3 send_line_message.py <project> [summary]     # Send completion notification")
        sys.exit(1)
    
    sys.exit(0 if success else 1)