#!/usr/bin/env /Users/horioshuuhei/Projects/claude-autodev/slack_socket_env/bin/python
"""
Slack Socket Mode Server for Claude Autodev
リアルタイムWebSocket通信で双方向制御
"""

import os
import json
import subprocess
import asyncio
from datetime import datetime
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

# Slack App設定
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'YOUR_SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN', 'YOUR_SLACK_APP_TOKEN')

# プロジェクトディレクトリ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELIVERABLES_DIR = os.path.join(BASE_DIR, "deliverables")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Slack Bolt App初期化
app = AsyncApp(token=SLACK_BOT_TOKEN)

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
*Added via Slack Socket Mode: {datetime.now().isoformat()}*
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

def get_project_readme(project_name):
    """プロジェクトのREADMEを取得"""
    project_dir = os.path.join(DELIVERABLES_DIR, project_name)
    if not os.path.exists(project_dir):
        return None
    
    # README.mdを探す
    readme_file = os.path.join(project_dir, "README.md")
    if os.path.exists(readme_file):
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading README: {e}")
            return None
    
    # README.mdがない場合はSPEC.mdを試す
    spec_file = os.path.join(project_dir, "SPEC.md")
    if os.path.exists(spec_file):
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading SPEC: {e}")
            return None
    
    return None

# メンション処理
@app.event("app_mention")
async def handle_app_mention(event, say, logger):
    """@Claude Autodev でのメンション処理"""
    user = event.get('user', '')
    text = event.get('text', '')
    channel = event.get('channel', '')
    
    # Botメンションを除去してコマンドを抽出
    cleaned_text = text.split('>', 1)[-1].strip() if '>' in text else text.strip()
    
    logger.info(f"📥 App mention from {user}: {cleaned_text}")
    
    # ログ記録
    log_entry = f"{datetime.now().isoformat()}: Slack mention from {user} in {channel}: {cleaned_text}\n"
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(os.path.join(LOGS_DIR, "slack_socket_messages.log"), "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    await process_claude_command(cleaned_text, say)

# ダイレクトメッセージ処理
@app.event("message")
async def handle_direct_message(event, say, logger):
    """DMでのメッセージ処理"""
    if event.get('channel_type') == 'im' and not event.get('bot_id'):
        user = event.get('user', '')
        text = event.get('text', '')
        
        logger.info(f"📥 Direct message from {user}: {text}")
        
        # ログ記録
        log_entry = f"{datetime.now().isoformat()}: Slack DM from {user}: {text}\n"
        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(os.path.join(LOGS_DIR, "slack_socket_messages.log"), "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        await process_claude_command(text, say)

# スラッシュコマンド処理
@app.command("/claude")
async def handle_claude_slash_command(ack, respond, command, logger):
    """Slash command /claude の処理"""
    await ack()
    
    user = command.get('user_id', '')
    text = command.get('text', '')
    
    logger.info(f"📥 Slash command from {user}: /claude {text}")
    
    # ログ記録
    log_entry = f"{datetime.now().isoformat()}: Slack slash command from {user}: /claude {text}\n"
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(os.path.join(LOGS_DIR, "slack_socket_messages.log"), "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    async def say_response(message):
        await respond(message)
    
    await process_claude_command(f"claude {text}", say_response)

async def process_claude_command(command_text, say):
    """Claude Autodev コマンドの処理"""
    text = command_text.strip()
    
    try:
        if text.startswith("claude new ") or text.startswith("new "):
            # 新規プロジェクト作成
            parts = text.replace("claude new ", "").replace("new ", "").split(" ", 1)
            if len(parts) >= 2:
                project_name, idea = parts
                if create_new_project(project_name, idea):
                    await say(f"🚀 新規プロジェクト `{project_name}` の作成を開始しました！\n完了時に通知します。")
                else:
                    await say(f"❌ プロジェクト `{project_name}` の作成に失敗しました。")
            else:
                await say("使用方法: `claude new project-name description`")
        
        elif text.startswith("claude modify ") or text.startswith("modify "):
            # 仕様変更
            parts = text.replace("claude modify ", "").replace("modify ", "").split(" ", 1)
            if len(parts) >= 2:
                project_name, modification = parts
                if modify_project_spec(project_name, modification):
                    await say(f"✅ プロジェクト `{project_name}` の仕様を更新しました！")
                else:
                    await say(f"❌ プロジェクト `{project_name}` が見つからないか、更新に失敗しました。")
            else:
                await say("使用方法: `claude modify project-name changes`")
        
        elif text.startswith("claude describe ") or text.startswith("describe ") or text.startswith("/slack describe "):
            # プロジェクトの説明を表示
            project_name = text.replace("claude describe ", "").replace("describe ", "").replace("/slack describe ", "").strip()
            if project_name:
                readme_content = get_project_readme(project_name)
                if readme_content:
                    # Slackのメッセージ制限を考慮して長さを調整
                    if len(readme_content) > 3000:
                        readme_content = readme_content[:2900] + "\n\n... (以下省略)"
                    await say(f"📄 プロジェクト `{project_name}` の説明:\n\n```\n{readme_content}\n```")
                else:
                    await say(f"❌ プロジェクト `{project_name}` のREADMEが見つかりませんでした。")
            else:
                await say("使用方法: `claude describe project-name` または `/slack describe project-name`")
        
        elif text in ["claude projects", "projects", "claude status", "status"]:
            # プロジェクト一覧
            projects = get_active_projects()
            if projects:
                project_list = "\n".join([f"• `{p}`" for p in projects])
                await say(f"📋 アクティブなプロジェクト:\n{project_list}")
            else:
                await say("📋 現在アクティブなプロジェクトはありません。")
        
        elif text in ["claude help", "help", "claude ?", "?"]:
            # ヘルプ
            help_message = """🤖 **Claude Autodev - AI自動開発システム**

## 📋 利用可能なコマンド

### プロジェクト管理
• `/claude new <名前> <アイデア>` - 新規プロジェクト作成
• `/claude modify <名前> <変更内容>` - 仕様変更
• `/claude describe <名前>` - プロジェクトの詳細表示
• `/claude projects` - アクティブなプロジェクト一覧

### システム情報
• `/claude help` - このヘルプ表示

## 🔧 使用方法
1. **スラッシュコマンド**: `/claude [コマンド]`
2. **@メンション**: `@Claude Autodev [コマンド]`
3. **ダイレクトメッセージ**: `[コマンド]`

## 💡 使用例
```
/claude new weather-app 天気予報アプリをNext.jsで作成
/claude projects
/claude describe perfect-keiba-AI
/claude modify weather-app レスポンシブ対応を追加
```

## 📊 現在の監視状況
✅ **完了監視システム**: 稼働中
✅ **自動通知**: 有効
✅ **プロジェクト管理**: アクティブ

_AI自動開発で効率的なプロジェクト管理を実現！_"""
            await say(help_message)
        
        else:
            # 不明なコマンド
            await say("❓ 不明なコマンドです。`claude help` でヘルプを確認してください。")
    
    except Exception as e:
        print(f"Error processing command: {e}")
        await say(f"❌ コマンド処理中にエラーが発生しました: {str(e)}")

async def main():
    """メインの実行関数"""
    print("🤖 Starting Claude Autodev Slack Socket Mode Server...")
    print(f"📁 Base directory: {BASE_DIR}")
    print(f"🔌 Socket Mode: Enabled")
    print(f"📱 App Token: {SLACK_APP_TOKEN[:20]}...")
    print(f"🤖 Bot Token: {SLACK_BOT_TOKEN[:20] if SLACK_BOT_TOKEN else 'Not configured'}...")
    
    if not SLACK_BOT_TOKEN:
        print("❌ SLACK_BOT_TOKEN not found. Please set environment variable.")
        return
    
    # ログディレクトリ作成
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Socket Mode ハンドラー開始
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    # 依存関係チェック
    try:
        import slack_bolt
        print(f"✅ slack-bolt imported successfully")
    except ImportError:
        print("❌ slack-bolt not installed. Run: pip install slack-bolt")
        exit(1)
    
    asyncio.run(main())