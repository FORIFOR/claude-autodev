#!/usr/bin/env python3
"""
Simple LINE Notify sender for project completion notifications
"""

import requests
import sys
import json
from datetime import datetime

def send_line_notify(token, message):
    """Send message via LINE Notify API"""
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        if response.status_code == 200:
            print(f"✅ LINE Notify sent successfully")
            return True
        else:
            print(f"❌ LINE Notify failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ LINE Notify error: {e}")
        return False

def send_project_completion(project_name, summary="プロジェクトが完了しました"):
    """Send project completion notification"""
    # Try to get token from environment or config
    import os
    
    # Check environment variable first
    token = os.environ.get('LINE_NOTIFY_TOKEN')
    
    # If not found, try to read from config file
    if not token:
        config_paths = [
            "/Users/horioshuuhei/.keiba_ai/line_config.json",
            "/Users/horioshuuhei/Projects/claude-autodev/config/line_notify.json"
        ]
        
        for config_path in config_paths:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    token = config.get('notify_token')
                    if token:
                        break
            except:
                continue
    
    if not token:
        print("❌ LINE Notify token not found")
        print("Please set LINE_NOTIFY_TOKEN environment variable or configure in config file")
        return False
    
    # Format message
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M")
    message = f"""🎉 Claude Autodev - プロジェクト完了

📋 プロジェクト: {project_name}
⏰ 完了時刻: {timestamp}

✅ {summary}

🔗 詳細は deliverables/{project_name}/ をご確認ください。"""
    
    return send_line_notify(token, message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 line_notify_sender.py <project_name> [summary]")
        sys.exit(1)
    
    project_name = sys.argv[1]
    summary = sys.argv[2] if len(sys.argv) > 2 else "プロジェクトが完了しました"
    
    success = send_project_completion(project_name, summary)
    sys.exit(0 if success else 1)