#!/usr/bin/env python3
"""
LINE Webhook Server for bidirectional communication
LINEからのメッセージを受信してプロジェクトの仕様変更に対応
"""

import os
import json
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify
import hashlib
import hmac
import base64

app = Flask(__name__)

# LINE Bot設定
CHANNEL_ACCESS_TOKEN = "FzpiO7StfY1GtQ1URU5um4IiwXipxgM+bZeuMd1h2b947eoy4doDrd96Sw9x8VKix/aYs4T3zkNL/vZRHo20bF28t35D1urum/WptrpnEthFZUFAR3NpBxc0kQ6U9Q2wXZ6422tOx/5nRCkn5qtsIAdB04t89/1O/w1cDnyilFU"
CHANNEL_SECRET = "your_channel_secret_here"  # 実際のChannel Secretに置き換えてください
DESTINATION_USER_ID = "U2f0d021267564d91134b178d7f65fc84"

# プロジェクトディレクトリ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELIVERABLES_DIR = os.path.join(BASE_DIR, "deliverables")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

def verify_signature(body, signature):
    """LINE Webhook署名検証"""
    if not CHANNEL_SECRET:
        return True  # 開発用（本番では必ず検証すること）
    
    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'), body, hashlib.sha256).digest()
    expected_signature = base64.b64encode(hash).decode()
    return hmac.compare_digest(expected_signature, signature.replace('sha256=', ''))

def send_line_reply(reply_token, message):
    """LINE返信メッセージ送信"""
    import requests
    
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending reply: {e}")
        return False

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
    idea_file = os.path.join(ideas_dir, f"{project_name}_from_line.txt")
    
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
*Added via LINE: {datetime.now().isoformat()}*
"""
    
    try:
        with open(spec_file, 'a', encoding='utf-8') as f:
            f.write(modification_entry)
        
        # Gitコミット
        subprocess.run(['git', 'add', 'SPEC.md'], cwd=project_dir)
        subprocess.run(['git', 'commit', '-m', f'Update spec via LINE: {modification_text[:50]}...'], cwd=project_dir)
        
        return True
    except Exception as e:
        print(f"Error modifying spec: {e}")
        return False

def process_line_message(message_text, reply_token):
    """LINEメッセージの処理"""
    text = message_text.strip()
    
    # コマンドパターンの解析
    if text.startswith("/create "):
        # 新規プロジェクト作成: /create プロジェクト名 アイデア説明
        parts = text[8:].split(" ", 1)
        if len(parts) >= 2:
            project_name, idea = parts
            if create_new_project(project_name, idea):
                reply_msg = f"🚀 新規プロジェクト '{project_name}' の作成を開始しました！\n完了時に通知します。"
            else:
                reply_msg = f"❌ プロジェクト '{project_name}' の作成に失敗しました。"
        else:
            reply_msg = "使用方法: /create プロジェクト名 アイデア説明"
    
    elif text.startswith("/modify "):
        # 仕様変更: /modify プロジェクト名 変更内容
        parts = text[8:].split(" ", 1)
        if len(parts) >= 2:
            project_name, modification = parts
            if modify_project_spec(project_name, modification):
                reply_msg = f"✅ プロジェクト '{project_name}' の仕様を更新しました！"
            else:
                reply_msg = f"❌ プロジェクト '{project_name}' が見つからないか、更新に失敗しました。"
        else:
            reply_msg = "使用方法: /modify プロジェクト名 変更内容"
    
    elif text in ["/list", "/projects"]:
        # プロジェクト一覧
        projects = get_active_projects()
        if projects:
            reply_msg = "📋 アクティブなプロジェクト:\n" + "\n".join([f"• {p}" for p in projects])
        else:
            reply_msg = "📋 現在アクティブなプロジェクトはありません。"
    
    elif text in ["/help", "/?"]:
        # ヘルプ
        reply_msg = """🤖 Claude Autodev コマンド:

/create <名前> <アイデア> - 新規プロジェクト作成
/modify <名前> <変更内容> - 仕様変更
/list - プロジェクト一覧
/help - このヘルプ

例:
/create todo-app TODOアプリをReactで作成
/modify todo-app ダークモード機能を追加"""
    
    else:
        # 自由入力はtodo-appプロジェクトの仕様変更として処理
        default_project = "default-project"
        if modify_project_spec(default_project, text):
            reply_msg = f"📝 '{default_project}' に仕様を追加しました: {text[:50]}..."
        else:
            reply_msg = "❓ 不明なコマンドです。/help でヘルプを確認してください。"
    
    # 返信送信
    send_line_reply(reply_token, reply_msg)

@app.route('/webhook', methods=['POST'])
def webhook():
    """LINE Webhook エンドポイント"""
    # 署名検証
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data()
    
    if not verify_signature(body, signature):
        return jsonify({"error": "Invalid signature"}), 403
    
    # イベント処理
    try:
        events = json.loads(body.decode('utf-8'))['events']
        
        for event in events:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                user_id = event['source']['userId']
                
                # 認証されたユーザーのみ処理
                if user_id == DESTINATION_USER_ID:
                    message_text = event['message']['text']
                    reply_token = event['replyToken']
                    
                    # メッセージログ記録
                    log_entry = f"{datetime.now().isoformat()}: Received from {user_id}: {message_text}\n"
                    os.makedirs(LOGS_DIR, exist_ok=True)
                    with open(os.path.join(LOGS_DIR, "line_messages.log"), "a", encoding="utf-8") as f:
                        f.write(log_entry)
                    
                    # メッセージ処理
                    process_line_message(message_text, reply_token)
                else:
                    send_line_reply(event['replyToken'], "🚫 認証されていないユーザーです。")
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"error": "Internal error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """ヘルスチェック"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_projects": len(get_active_projects())
    })

if __name__ == '__main__':
    print("🌐 Starting LINE Webhook Server...")
    print(f"📁 Base directory: {BASE_DIR}")
    print(f"🔗 Webhook URL: http://localhost:5000/webhook")
    print(f"🏥 Health check: http://localhost:5000/health")
    
    # ログディレクトリ作成
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)