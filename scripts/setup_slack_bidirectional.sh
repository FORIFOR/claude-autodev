#!/usr/bin/env bash

echo "🤖 Slack Bidirectional Communication Setup"
echo "=========================================="
echo ""
echo "📋 双方向通信の設定手順:"
echo ""
echo "1. https://api.slack.com/apps にアクセス"
echo "2. 'Create New App' → 'From scratch'"
echo "3. App Name: Claude Autodev Bot"
echo "4. ワークスペースを選択"
echo ""
echo "5. OAuth & Permissions設定:"
echo "   - Bot Token Scopes に以下を追加:"
echo "     • chat:write"
echo "     • channels:read"
echo "     • groups:read"
echo "     • im:read"
echo "     • mpim:read"
echo "   - 'Install to Workspace' をクリック"
echo "   - Bot User OAuth Token をコピー"
echo ""
echo "6. Event Subscriptions設定:"
echo "   - Enable Events を ON"
echo "   - Request URL: https://your-ngrok-url.ngrok-free.app/slack/events"
echo "   - Subscribe to bot events に 'message.channels' を追加"
echo ""
echo "7. Slash Commands設定 (オプション):"
echo "   - Create New Command"
echo "   - Command: /claude"
echo "   - Request URL: https://your-ngrok-url.ngrok-free.app/slack/commands"
echo "   - Description: Claude Autodev コマンド"
echo ""

# ngrok の起動確認
if ! pgrep -f "ngrok.*5002" > /dev/null; then
    echo "8. ngrok tunnel 起動:"
    echo "   ngrok http 5002"
    echo ""
    read -p "ngrok を起動してから Enter を押してください..."
fi

echo ""
read -p "Bot User OAuth Token を入力してください (xoxb-...): " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Bot Token が入力されていません"
    exit 1
fi

echo ""
read -p "Signing Secret を入力してください (オプション): " SIGNING_SECRET

echo ""
read -p "Channel ID を入力してください (オプション): " CHANNEL_ID

echo ""
echo "🧪 環境変数設定とテスト..."

# Export variables
export SLACK_BOT_TOKEN="$BOT_TOKEN"
if [ -n "$SIGNING_SECRET" ]; then
    export SLACK_SIGNING_SECRET="$SIGNING_SECRET"
fi

# 設定ファイルを更新
CONFIG_DIR="$(dirname "$(dirname "$0")")/config"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/slack_bidirectional_config.json" << EOF
{
    "bot_token": "$BOT_TOKEN",
    "signing_secret": "$SIGNING_SECRET",
    "channel_id": "$CHANNEL_ID",
    "commands": {
        "new": "claude new <project-name> <description>",
        "modify": "claude modify <project-name> <changes>",
        "projects": "claude projects",
        "help": "claude help"
    }
}
EOF

echo ""
echo "✅ 設定完了！"
echo ""
echo "📁 設定ファイル: $CONFIG_DIR/slack_bidirectional_config.json"
echo ""
echo "🚀 サーバー起動方法:"
echo "export SLACK_BOT_TOKEN=\"$BOT_TOKEN\""
if [ -n "$SIGNING_SECRET" ]; then
    echo "export SLACK_SIGNING_SECRET=\"$SIGNING_SECRET\""
fi
echo "python3 slack_webhook_server.py"
echo ""
echo "💬 Slackでのコマンド例:"
echo "claude new todo-app TODOアプリをReactで作成"
echo "claude modify todo-app ダークモード機能を追加"
echo "claude projects"
echo "claude help"
echo ""
echo "⚡ スラッシュコマンド例 (設定した場合):"
echo "/claude new mobile-app 天気予報アプリを作成"
echo "/claude projects"