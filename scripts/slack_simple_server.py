#!/usr/bin/env python3
"""
Slack Simple Webhook Server for Claude Autodev
Webhookベースのシンプルな双方向通信
"""

import os
import json
import subprocess
import hashlib
import hmac
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Slack設定
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'YOUR_SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET', '')

# プロジェクトディレクトリ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELIVERABLES_DIR = os.path.join(BASE_DIR, "deliverables")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

def verify_slack_signature(body, timestamp, signature):
    """Slack署名検証"""
    if not SLACK_SIGNING_SECRET:
        print("⚠️  Slack Signing Secret not configured, skipping signature verification")
        return True
    
    sig_basestring = f"v0:{timestamp}:{body}"
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, signature)

def send_slack_message(channel, text, thread_ts=None):
    """Slackにメッセージを送信"""
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    data = {
        "channel": channel,
        "text": text
    }
    if thread_ts:
        data["thread_ts"] = thread_ts
        
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

def get_active_projects():
    """アクティブなプロジェクトを取得"""
    projects = []
    if os.path.exists(DELIVERABLES_DIR):
        for item in os.listdir(DELIVERABLES_DIR):
            project_path = os.path.join(DELIVERABLES_DIR, item)
            if os.path.isdir(project_path):
                projects.append(item)
    return projects

def create_new_project(project_name, idea_text):
    """新しいプロジェクトを作成"""
    script_dir = os.path.join(BASE_DIR, "scripts")
    
    # アイデアファイルを作成
    ideas_dir = os.path.join(BASE_DIR, "ideas")
    os.makedirs(ideas_dir, exist_ok=True)
    idea_file = os.path.join(ideas_dir, f"{project_name}_from_slack.txt")
    
    with open(idea_file, 'w', encoding='utf-8') as f:
        f.write(idea_text)
    
    # プロジェクト開始
    try:
        cmd = [
            os.path.join(script_dir, "start_project_file.sh"),
            project_name,
            idea_file
        ]
        subprocess.Popen(cmd, cwd=script_dir)
        return True
    except Exception as e:
        print(f"Error starting project: {e}")
        return False

def modify_project_spec(project_name, modification_text):
    """プロジェクトの仕様を変更"""
    project_dir = os.path.join(DELIVERABLES_DIR, project_name)
    if not os.path.exists(project_dir):
        return False
    
    # 仕様変更をSPEC.mdに追記
    spec_file = os.path.join(project_dir, "SPEC.md")
    modification_entry = f"""
## 📝 仕様変更 - {datetime.now().strftime('%Y/%m/%d %H:%M')}

{modification_text}

---
*Added via Slack: {datetime.now().isoformat()}*
"""
    
    try:
        with open(spec_file, 'a', encoding='utf-8') as f:
            f.write(modification_entry)
        
        # Gitコミット
        subprocess.run(['git', 'add', 'SPEC.md'], cwd=project_dir)
        subprocess.run(['git', 'commit', '-m', f'Update spec via Slack: {modification_text[:50]}...'], cwd=project_dir)
        
        return True
    except Exception as e:
        print(f"Error modifying spec: {e}")
        return False

def process_claude_command(command_text, channel, thread_ts=None):
    """Claude Autodev コマンドの処理"""
    text = command_text.strip()
    
    try:
        if text.startswith("claude new "):
            # 新規プロジェクト作成
            parts = text[11:].split(" ", 1)
            if len(parts) >= 2:
                project_name, idea = parts
                if create_new_project(project_name, idea):
                    reply_msg = f"🚀 新規プロジェクト `{project_name}` の作成を開始しました！\n完了時に通知します。"
                else:
                    reply_msg = f"❌ プロジェクト `{project_name}` の作成に失敗しました。"
            else:
                reply_msg = "使用方法: `claude new project-name description`"
        
        elif text.startswith("claude modify "):
            # 仕様変更
            parts = text[14:].split(" ", 1)
            if len(parts) >= 2:
                project_name, modification = parts
                if modify_project_spec(project_name, modification):
                    reply_msg = f"✅ プロジェクト `{project_name}` の仕様を更新しました！"
                else:
                    reply_msg = f"❌ プロジェクト `{project_name}` が見つからないか、更新に失敗しました。"
            else:
                reply_msg = "使用方法: `claude modify project-name changes`"
        
        elif text in ["claude projects", "claude status"]:
            # プロジェクト一覧
            projects = get_active_projects()
            if projects:
                project_list = "\n".join([f"• `{p}`" for p in projects])
                reply_msg = f"📋 アクティブなプロジェクト:\n{project_list}"
            else:
                reply_msg = "📋 現在アクティブなプロジェクトはありません。"
        
        elif text in ["claude help", "claude ?"]:
            # ヘルプ
            reply_msg = """🤖 Claude Autodev コマンド:

`claude new <名前> <アイデア>` - 新規プロジェクト作成
`claude modify <名前> <変更内容>` - 仕様変更
`claude projects` - プロジェクト一覧
`claude help` - このヘルプ

💬 使用方法:
• チャンネルでメンション: `@Claude Autodev claude new todo-app TODOアプリを作成`
• スラッシュコマンド: `/claude new mobile-app 天気アプリ作成`

例:
`claude new todo-app TODOアプリをReactで作成`
`claude modify todo-app ダークモード機能を追加`"""
        
        else:
            # 不明なコマンド
            reply_msg = "❓ 不明なコマンドです。`claude help` でヘルプを確認してください。"
        
        # 返信送信
        send_slack_message(channel, reply_msg, thread_ts)
        
    except Exception as e:
        print(f"Error processing command: {e}")
        send_slack_message(channel, f"❌ コマンド処理中にエラーが発生しました: {str(e)}", thread_ts)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    """Slack Events API エンドポイント"""
    print(f"📥 Received Slack event from {request.remote_addr}")
    
    # 署名検証
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    signature = request.headers.get('X-Slack-Signature', '')
    body = request.get_data().decode('utf-8')
    
    if not verify_slack_signature(body, timestamp, signature):
        print("❌ Slack signature verification failed")
        return jsonify({"error": "Invalid signature"}), 403
    
    print("✅ Slack signature verification passed")
    
    # イベント処理
    try:
        event_data = json.loads(body)
        
        # URL verification challenge
        if event_data.get('type') == 'url_verification':
            return jsonify({"challenge": event_data.get('challenge')})
        
        # メッセージイベント処理
        event = event_data.get('event', {})
        if event.get('type') == 'app_mention' and not event.get('bot_id'):
            text = event.get('text', '')
            channel = event.get('channel', '')
            thread_ts = event.get('thread_ts')
            user = event.get('user', '')
            
            # Botメンションを除去してコマンドを抽出
            cleaned_text = text.split('>', 1)[-1].strip() if '>' in text else text.strip()
            
            print(f"💬 Processing app_mention: {cleaned_text}")
            
            # メッセージログ記録
            log_entry = f"{datetime.now().isoformat()}: Slack app_mention from {user} in {channel}: {cleaned_text}\n"
            os.makedirs(LOGS_DIR, exist_ok=True)
            with open(os.path.join(LOGS_DIR, "slack_simple_messages.log"), "a", encoding="utf-8") as f:
                f.write(log_entry)
            
            # コマンド処理
            process_claude_command(cleaned_text, channel, thread_ts)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Slack webhook error: {e}")
        return jsonify({"error": "Internal error"}), 500

@app.route('/slack/commands', methods=['POST'])
def slack_slash_commands():
    """Slack Slash Commands エンドポイント"""
    print(f"📥 Received Slack slash command from {request.remote_addr}")
    
    # 署名検証
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    signature = request.headers.get('X-Slack-Signature', '')
    body = request.get_data().decode('utf-8')
    
    if not verify_slack_signature(body, timestamp, signature):
        print("❌ Slack signature verification failed")
        return "Invalid signature", 403
    
    # スラッシュコマンド処理
    command = request.form.get('command', '')
    text = request.form.get('text', '')
    channel_id = request.form.get('channel_id', '')
    user_id = request.form.get('user_id', '')
    
    if command == '/claude':
        print(f"💬 Processing slash command: {command} {text}")
        
        # ログ記録
        log_entry = f"{datetime.now().isoformat()}: Slack slash command from {user_id}: {command} {text}\n"
        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(os.path.join(LOGS_DIR, "slack_simple_messages.log"), "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # コマンド処理
        process_claude_command(f"claude {text}", channel_id)
        
        return "コマンドを実行中です...", 200
    
    return "Unknown command", 404

@app.route('/health', methods=['GET'])
def health():
    """ヘルスチェック"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_projects": len(get_active_projects()),
        "slack_mode": "webhook"
    })

if __name__ == '__main__':
    print("🤖 Starting Slack Simple Webhook Server for Claude Autodev...")
    print(f"📁 Base directory: {BASE_DIR}")
    print(f"🔗 Events endpoint: http://localhost:5003/slack/events")
    print(f"⚡ Commands endpoint: http://localhost:5003/slack/commands")
    print(f"🏥 Health check: http://localhost:5003/health")
    print(f"🤖 Bot Token: {SLACK_BOT_TOKEN[:20]}...")
    
    # ログディレクトリ作成
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5003, debug=True)