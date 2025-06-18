#!/usr/bin/env bash

echo "🤖 Slack Bot Setup for Claude Autodev"
echo "====================================="
echo ""
echo "📋 手順:"
echo "1. https://api.slack.com/apps にアクセス"
echo "2. 'Create New App' → 'From scratch'"
echo "3. App Name: Claude Autodev Bot"
echo "4. ワークスペースを選択"
echo "5. 'Incoming Webhooks' を有効化"
echo "6. 'Add New Webhook to Workspace'"
echo "7. 通知を送信したいチャンネルを選択"
echo "8. Webhook URLをコピー"
echo ""

read -p "Slack Webhook URLを入力してください: " WEBHOOK_URL

if [ -z "$WEBHOOK_URL" ]; then
    echo "❌ Webhook URLが入力されていません"
    exit 1
fi

# オプション: チャンネル指定
read -p "特定のチャンネルに送信しますか？ (チャンネル名 or Enter): " CHANNEL

echo ""
echo "🧪 テスト送信中..."

# Export variables
export SLACK_WEBHOOK_URL="$WEBHOOK_URL"
if [ -n "$CHANNEL" ]; then
    export SLACK_CHANNEL="$CHANNEL"
fi

# Test notification
python3 "$(dirname "$0")/send_slack_message.py" test

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Slack Bot設定完了！"
    echo ""
    
    # 設定ファイルを作成
    CONFIG_DIR="$(dirname "$(dirname "$0")")/config"
    mkdir -p "$CONFIG_DIR"
    
    cat > "$CONFIG_DIR/slack_config.json" << EOF
{
    "webhook_url": "$WEBHOOK_URL",
    "channel": "$CHANNEL",
    "bot_name": "Claude Autodev Bot",
    "icon_emoji": ":robot_face:"
}
EOF
    
    echo "📁 設定ファイル作成: $CONFIG_DIR/slack_config.json"
    echo ""
    echo "環境変数で設定する場合:"
    echo "export SLACK_WEBHOOK_URL=\"$WEBHOOK_URL\""
    if [ -n "$CHANNEL" ]; then
        echo "export SLACK_CHANNEL=\"$CHANNEL\""
    fi
    echo ""
    echo "~/.bashrc または ~/.zshrc に追加してください"
else
    echo ""
    echo "❌ 設定に失敗しました"
    echo "Webhook URLを再確認してください"
fi