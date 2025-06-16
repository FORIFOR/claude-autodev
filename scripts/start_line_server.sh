#!/usr/bin/env bash

# LINE Webhook Server 起動スクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "🌐 LINE Webhook Server 起動"
echo "========================="
echo ""

# Python依存関係のチェック
echo "📦 依存関係をチェック中..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask が見つかりません。インストールしますか？ (y/n)"
    read -r install_flask
    if [ "$install_flask" = "y" ]; then
        pip3 install flask requests
    else
        echo "❌ Flask が必要です。手動でインストールしてください: pip3 install flask requests"
        exit 1
    fi
fi

if ! python3 -c "import requests" 2>/dev/null; then
    echo "Requests が見つかりません。インストール中..."
    pip3 install requests
fi

echo "✅ 依存関係OK"
echo ""

# 起動方法の選択
echo "起動方法を選択してください："
echo "1) 開発モード（フォアグラウンド・デバッグ有効）"
echo "2) 本番モード（バックグラウンド）"
echo "3) ngrok トンネル付き起動（外部アクセス対応）"
read -p "選択 (1-3): " choice

case $choice in
    1)
        echo "🚀 開発モードで起動中..."
        echo "📝 Webhook URL: http://localhost:5000/webhook"
        echo "🏥 Health check: http://localhost:5000/health"
        python3 "$SCRIPT_DIR/line_webhook_server.py"
        ;;
    
    2)
        echo "🔄 本番モードで起動中..."
        nohup python3 "$SCRIPT_DIR/line_webhook_server.py" > "$BASE_DIR/logs/line_server.log" 2>&1 &
        SERVER_PID=$!
        echo "✅ LINE Webhook Server が起動しました (PID: $SERVER_PID)"
        echo "📋 停止方法: kill $SERVER_PID"
        echo "📄 ログ確認: tail -f $BASE_DIR/logs/line_server.log"
        echo "$SERVER_PID" > "$BASE_DIR/logs/line_server.pid"
        ;;
    
    3)
        echo "🌍 ngrok トンネル付きで起動中..."
        
        # ngrokのチェック
        if ! command -v ngrok >/dev/null 2>&1; then
            echo "❌ ngrok が見つかりません。インストールしてください："
            echo "   brew install ngrok  # macOS"
            echo "   または https://ngrok.com/download からダウンロード"
            exit 1
        fi
        
        # バックグラウンドでFlaskサーバー起動
        python3 "$SCRIPT_DIR/line_webhook_server.py" &
        FLASK_PID=$!
        
        # 少し待ってからngrok起動
        sleep 3
        echo "🌐 ngrok トンネルを作成中..."
        ngrok http 5000 &
        NGROK_PID=$!
        
        echo "✅ サーバー起動完了"
        echo "📋 Flask Server PID: $FLASK_PID"
        echo "📋 ngrok PID: $NGROK_PID"
        echo ""
        echo "🔗 ngrok の公開URLを確認："
        echo "   http://localhost:4040"
        echo ""
        echo "📝 LINE Developer Console で Webhook URL を更新してください："
        echo "   https://xxxxx.ngrok.io/webhook"
        echo ""
        echo "停止方法: kill $FLASK_PID $NGROK_PID"
        
        # PIDを保存
        echo "$FLASK_PID" > "$BASE_DIR/logs/line_server.pid"
        echo "$NGROK_PID" > "$BASE_DIR/logs/ngrok.pid"
        
        wait
        ;;
    
    *)
        echo "❌ 無効な選択です"
        exit 1
        ;;
esac