#!/usr/bin/env bash

echo "🚀 Slack Socket Mode Setup for Claude Autodev"
echo "============================================="
echo ""

# 依存関係インストール
echo "📦 Installing dependencies..."
pip3 install slack-bolt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install slack-bolt"
    echo "Try: pip3 install --user slack-bolt"
    exit 1
fi

echo ""
echo "📋 Slack App設定手順:"
echo ""
echo "1. https://api.slack.com/apps にアクセス"
echo "2. 'Create New App' → 'From scratch'"
echo "3. App Name: Claude Autodev Bot"
echo "4. ワークスペースを選択"
echo ""
echo "5. Socket Mode を有効化:"
echo "   - 'Socket Mode' → Enable Socket Mode を ON"
echo "   - App-Level Token を生成 (connections:write scope)"
echo ""
echo "6. OAuth & Permissions設定:"
echo "   - Bot Token Scopes に以下を追加:"
echo "     • app_mentions:read"
echo "     • chat:write"
echo "     • channels:read"
echo "     • im:read"
echo "     • im:write"
echo "   - 'Install to Workspace' をクリック"
echo "   - Bot User OAuth Token (xoxb-...) をコピー"
echo ""
echo "7. Event Subscriptions設定:"
echo "   - Enable Events を ON"
echo "   - Subscribe to bot events に以下を追加:"
echo "     • app_mention"
echo "     • message.im"
echo ""
echo "8. Slash Commands設定 (オプション):"
echo "   - Create New Command"
echo "   - Command: /claude"
echo "   - Description: Claude Autodev コマンド"
echo ""

read -p "Bot User OAuth Token (xoxb-...) を入力してください: " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Bot Token が入力されていません"
    exit 1
fi

if [[ ! "$BOT_TOKEN" =~ ^xoxb- ]]; then
    echo "❌ Bot Token は xoxb- で始まる必要があります"
    exit 1
fi

# App Token は既に提供されている
APP_TOKEN="YOUR_SLACK_APP_TOKEN"

echo ""
echo "🧪 テスト起動..."

# Export variables
export SLACK_BOT_TOKEN="$BOT_TOKEN"
export SLACK_APP_TOKEN="$APP_TOKEN"

# 設定ファイルを作成
CONFIG_DIR="$(dirname "$(dirname "$0")")/config"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/slack_socket_config.json" << EOF
{
    "bot_token": "$BOT_TOKEN",
    "app_token": "$APP_TOKEN",
    "socket_mode": true,
    "commands": {
        "new": "claude new <project-name> <description>",
        "modify": "claude modify <project-name> <changes>",
        "projects": "claude projects",
        "help": "claude help"
    },
    "usage": [
        "@Claude Autodev claude new todo-app TODOアプリを作成",
        "DM: claude projects",
        "/claude new mobile-app 天気アプリ作成"
    ]
}
EOF

echo ""
echo "✅ 設定完了！"
echo ""
echo "📁 設定ファイル: $CONFIG_DIR/slack_socket_config.json"
echo ""
echo "🚀 サーバー起動方法:"
echo "export SLACK_BOT_TOKEN=\"$BOT_TOKEN\""
echo "export SLACK_APP_TOKEN=\"$APP_TOKEN\""
echo "python3 slack_socket_server.py"
echo ""
echo "💬 Slackでの使用方法:"
echo "1. @Claude Autodev claude new todo-app TODOアプリを作成"
echo "2. DMで直接: claude projects"
echo "3. スラッシュコマンド: /claude help"
echo ""
echo "🔌 Socket Modeの利点:"
echo "• ngrok不要 (WebSocketで直接接続)"
echo "• リアルタイム通信"
echo "• ファイアウォール問題なし"