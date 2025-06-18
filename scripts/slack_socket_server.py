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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Slack App設定
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'YOUR_SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN', 'YOUR_SLACK_APP_TOKEN')

# プロジェクトディレクトリ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELIVERABLES_DIR = os.path.join(BASE_DIR, "deliverables")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# キャッシュ用グローバル変数
_project_cache = {}
_cache_timestamp = {}

# Slack Bolt App初期化
app = AsyncApp(token=SLACK_BOT_TOKEN)

def get_active_projects():
    """アクティブなプロジェクトを取得（キャッシュ対応）"""
    cache_key = 'active_projects'
    current_time = datetime.now().timestamp()
    
    # 30秒キャッシュ
    if (cache_key in _project_cache and 
        cache_key in _cache_timestamp and 
        current_time - _cache_timestamp[cache_key] < 30):
        return _project_cache[cache_key]
    
    projects = []
    if os.path.exists(DELIVERABLES_DIR):
        for item in os.listdir(DELIVERABLES_DIR):
            project_path = os.path.join(DELIVERABLES_DIR, item)
            if os.path.isdir(project_path):
                projects.append(item)
    
    _project_cache[cache_key] = projects
    _cache_timestamp[cache_key] = current_time
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
    """プロジェクトのREADMEを取得（キャッシュ対応）"""
    cache_key = f'readme_{project_name}'
    current_time = datetime.now().timestamp()
    
    # 5分キャッシュ
    if (cache_key in _project_cache and 
        cache_key in _cache_timestamp and 
        current_time - _cache_timestamp[cache_key] < 300):
        return _project_cache[cache_key]
    
    project_dir = os.path.join(DELIVERABLES_DIR, project_name)
    if not os.path.exists(project_dir):
        return None
    
    content = None
    # README.mdを探す
    readme_file = os.path.join(project_dir, "README.md")
    if os.path.exists(readme_file):
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            pass
    
    # README.mdがない場合はSPEC.mdを試す
    if not content:
        spec_file = os.path.join(project_dir, "SPEC.md")
        if os.path.exists(spec_file):
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                pass
    
    _project_cache[cache_key] = content
    _cache_timestamp[cache_key] = current_time
    return content

def summarize_readme(content):
    """READMEの内容を要約（最適化版）"""
    if not content:
        return "プロジェクトの詳細情報が見つかりませんでした。"
    
    lines = content.split('\n', 50)  # 最初の50行のみ処理
    
    # タイトル抽出
    title = next((line[2:].strip() for line in lines if line.startswith('# ')), "Unknown Project")
    
    # 概要抽出（簡略化）
    description = ""
    for i, line in enumerate(lines[:20]):  # 最初の20行のみ
        if line.strip() and not line.startswith('#') and not line.startswith('-'):
            description = line.strip()[:200]
            break
    
    # 機能抽出（最大3個）
    features = []
    for line in lines[:30]:  # 最初の30行のみ
        if line.strip().startswith(('-', '*')) and len(features) < 3:
            feature = line.strip()[1:].strip()[:100]
            if feature and '機能' not in feature.lower():
                features.append(feature)
    
    # 要約構築
    parts = [f"📋 **{title}**"]
    if description:
        parts.append(f"🔍 {description}")
    if features:
        parts.append("✨ **主要機能**:")
        parts.extend([f"• {f}" for f in features])
    
    return "\n\n".join(parts)[:800] + ("..." if len("\n\n".join(parts)) > 800 else "")

def get_claude_autodev_summary():
    """Claude Autodev自体の説明を返す"""
    return """🤖 **Claude Autodev - AI自動開発システム**

🔍 **概要**: AIを活用した自動開発・プロジェクト管理システムです。Slack連携により、リアルタイムでプロジェクトの作成、管理、監視が可能です。

✨ **主要機能**:
• プロジェクト自動生成・管理
• リアルタイムSlack通知
• Socket Mode による双方向通信
• CI/CD統合監視
• 進捗自動追跡

🛠 **利用可能コマンド**:
• `/claude new` - 新規プロジェクト作成
• `/claude describe` - プロジェクト詳細表示
• `/claude showToDo` - 進捗確認
• `/claude ccusage` - コード複雑度分析
• `/claude projects` - プロジェクト一覧

💡 詳細は `/claude help` で確認できます。"""

def get_project_todos(project_name=None):
    """プロジェクトのToDo情報を取得（最適化版）"""
    cache_key = f'todos_{project_name or "all"}'
    current_time = datetime.now().timestamp()
    
    # 2分キャッシュ
    if (cache_key in _project_cache and 
        cache_key in _cache_timestamp and 
        current_time - _cache_timestamp[cache_key] < 120):
        return _project_cache[cache_key]
    
    todos_info = []
    
    if project_name:
        todo_file = os.path.join(DELIVERABLES_DIR, project_name, "TODO.md")
        if os.path.exists(todo_file):
            try:
                with open(todo_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)  # 最初の500文字のみ
                    todos_info.append(f"📋 **{project_name}**\n{parse_todo_content(content)}")
            except:
                todos_info.append(f"❌ {project_name}: エラー")
        else:
            todos_info.append(f"📋 **{project_name}**: ToDoなし")
    else:
        projects = get_active_projects()[:10]  # 最大10プロジェクト
        for proj in projects:
            todo_file = os.path.join(DELIVERABLES_DIR, proj, "TODO.md")
            if os.path.exists(todo_file):
                try:
                    with open(todo_file, 'r', encoding='utf-8') as f:
                        content = f.read(200)  # 最初の200文字のみ
                        summary = parse_todo_content(content, brief=True)
                        todos_info.append(f"📋 **{proj}**: {summary}")
                except:
                    todos_info.append(f"❌ **{proj}**: エラー")
    
    result = "\n\n".join(todos_info) if todos_info else "📋 ToDoが見つかりませんでした。"
    _project_cache[cache_key] = result
    _cache_timestamp[cache_key] = current_time
    return result

def parse_todo_content(content, brief=False):
    """ToDoファイルの内容を解析（最適化版）"""
    if not content:
        return "ToDoが空です"
    
    lines = content.split('\n', 50)  # 最大50行まで処理
    pending = sum(1 for line in lines if line.strip().startswith(('- [ ]', '* [ ]')))
    completed = sum(1 for line in lines if line.strip().startswith(('- [x]', '* [x]')))
    
    if brief:
        total = pending + completed
        return f"{completed}/{total} 完了 ({int(completed/total*100) if total > 0 else 0}%)"
    
    result = []
    if pending > 0:
        result.append(f"🔲 未完了: {pending}件")
    if completed > 0:
        result.append(f"✅ 完了: {completed}件")
    
    return " | ".join(result) if result else "ToDoなし"

def get_ccusage_report():
    """npx ccusage@latestの結果を実行して返す"""
    try:
        result = subprocess.run(['npx', 'ccusage@latest'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout
            return format_ccusage_output(output)
        else:
            return f"❌ ccusage実行エラー: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "⏱️ ccusage実行がタイムアウトしました"
    except Exception as e:
        return f"❌ ccusage実行中にエラーが発生: {str(e)}"

def format_ccusage_output(output):
    """ccusageの出力を整形"""
    if not output:
        return "📊 ccusage結果が空でした"
    
    lines = output.split('\n')
    summary_lines = []
    
    # 重要な統計情報を抽出
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['total', 'average', 'complexity', 'files', 'lines']):
            summary_lines.append(line)
    
    formatted = "📊 **コード複雑度分析結果**\n\n"
    
    if summary_lines:
        formatted += "\n".join([f"• {line}" for line in summary_lines[:10]])
    else:
        # フォールバック: 最初の10行を表示
        formatted += "\n".join(lines[:10])
    
    return formatted

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
    
    # 簡略ログ記録
    if len(cleaned_text) < 100:  # 短いコマンドのみログ
        log_entry = f"{datetime.now().strftime('%H:%M')}: {user}: {cleaned_text[:50]}\n"
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
        
        # 簡略ログ記録
        if len(text) < 100:  # 短いコマンドのみログ
            log_entry = f"{datetime.now().strftime('%H:%M')}: DM {user}: {text[:50]}\n"
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
    
    # 簡略ログ記録
    if len(text) < 100:  # 短いコマンドのみログ
        log_entry = f"{datetime.now().strftime('%H:%M')}: /{user}: {text[:50]}\n"
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
                # Claude Autodev自体の説明
                if project_name.lower() in ['claude-autodev', 'claude_autodev', 'autodev']:
                    summary = get_claude_autodev_summary()
                    await say(summary)
                else:
                    # 他のプロジェクトの説明
                    readme_content = get_project_readme(project_name)
                    if readme_content:
                        summary = summarize_readme(readme_content)
                        await say(f"📄 プロジェクト `{project_name}` の概要:\n\n{summary}")
                    else:
                        await say(f"❌ プロジェクト `{project_name}` のREADMEが見つかりませんでした。")
            else:
                await say("使用方法: `claude describe project-name` または `/slack describe project-name`")
        
        elif text.startswith("claude showToDo") or text.startswith("showToDo"):
            # ToDo進捗表示
            parts = text.replace("claude showToDo", "").replace("showToDo", "").strip()
            project_name = parts if parts else None
            
            todo_info = get_project_todos(project_name)
            await say(f"📋 **ToDo進捗状況**\n\n{todo_info}")
        
        elif text.startswith("claude ccusage") or text.startswith("ccusage"):
            # コード複雑度分析
            await say("🔄 コード複雑度分析を実行中...")
            ccusage_report = get_ccusage_report()
            await say(ccusage_report)
        
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
• `/claude describe <名前>` - プロジェクトの概要表示（要約版）
• `/claude projects` - アクティブなプロジェクト一覧

### 進捗管理・分析
• `/claude showToDo [プロジェクト名]` - ToDo進捗確認
• `/claude ccusage` - コード複雑度分析レポート

### システム情報
• `/claude help` - このヘルプ表示

## 🔧 使用方法
1. **スラッシュコマンド**: `/claude [コマンド]`
2. **@メンション**: `@Claude Autodev [コマンド]`
3. **ダイレクトメッセージ**: `[コマンド]`

## 💡 使用例
```
/claude new weather-app 天気予報アプリをNext.jsで作成
/claude describe claude-autodev
/claude showToDo perfect-keiba-AI
/claude showToDo （全プロジェクト一覧）
/claude ccusage
/claude modify weather-app レスポンシブ対応を追加
```

## 📊 現在の監視状況
✅ **完了監視システム**: 稼働中
✅ **自動通知**: 有効
✅ **プロジェクト管理**: アクティブ
✅ **進捗追跡**: 対応済み

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