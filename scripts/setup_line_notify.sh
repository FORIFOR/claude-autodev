#!/usr/bin/env bash

echo "🔔 LINE Notify Setup for Claude Autodev"
echo "======================================"
echo ""
echo "📋 手順:"
echo "1. https://notify-bot.line.me/ にアクセス"
echo "2. LINEアカウントでログイン"
echo "3. 'トークンを発行する'をクリック"
echo "4. トークン名: Claude Autodev"
echo "5. 送信先を選択(個人またはグループ)"
echo "6. 発行されたトークンをコピー"
echo ""

read -p "LINE Notifyトークンを入力してください: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ トークンが入力されていません"
    exit 1
fi

echo ""
echo "🧪 テスト送信中..."

# Export token
export LINE_NOTIFY_TOKEN="$TOKEN"

# Test notification
python3 "$(dirname "$0")/line_notify_sender.py" "setup-test" "LINE Notify設定完了テスト"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ LINE Notify設定完了！"
    echo ""
    echo "環境変数に設定する場合:"
    echo "export LINE_NOTIFY_TOKEN=\"$TOKEN\""
    echo ""
    echo "~/.bashrc または ~/.zshrc に追加してください"
else
    echo ""
    echo "❌ 設定に失敗しました"
    echo "トークンを再確認してください"
fi