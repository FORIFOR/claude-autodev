#!/usr/bin/env bash

echo "🔐 ngrok Authentication Setup"
echo "============================"
echo ""
echo "📋 手順:"
echo "1. https://dashboard.ngrok.com/signup でアカウント作成"
echo "2. ログイン後、authtokenをコピー"
echo "3. 以下にauthtokenを貼り付けてください"
echo ""

read -p "Authtoken を入力: " authtoken

if [ -z "$authtoken" ]; then
    echo "❌ Authtokenが入力されていません"
    exit 1
fi

echo ""
echo "🔧 Configuring ngrok..."
ngrok config add-authtoken "$authtoken"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ngrok認証設定完了！"
    echo ""
    echo "次のステップ:"
    echo "1. ./start_ngrok_tunnel.sh を実行"
    echo "2. 表示されるHTTPS URLをコピー"
    echo "3. LINE Developer ConsoleでWebhook URLを更新"
else
    echo "❌ 設定に失敗しました"
    exit 1
fi