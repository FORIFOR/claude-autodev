#!/usr/bin/env bash

# マスターモニター起動スクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$BASE_DIR/logs"

echo "🎛️  Claude Autodev Master Monitor"
echo "=================================="
echo ""
echo "このスクリプトは以下の機能を提供します："
echo "• プロジェクト完了の自動監視"
echo "• 完了時のLINE通知送信"
echo "• 成果物レポートの自動生成"
echo ""

# 使用方法の選択
echo "起動方法を選択してください："
echo "1) フォアグラウンドで実行（ターミナルで監視）"
echo "2) バックグラウンドで実行（デーモン化）"
echo "3) テスト実行（既存プロジェクトで通知テスト）"
read -p "選択 (1-3): " choice

case $choice in
    1)
        echo "🚀 フォアグラウンドでマスターモニターを開始..."
        exec "$SCRIPT_DIR/master_monitor.sh"
        ;;
    2)
        echo "🔄 バックグラウンドでマスターモニターを開始..."
        mkdir -p "$LOGS_DIR"
        nohup "$SCRIPT_DIR/master_monitor.sh" > "$LOGS_DIR/master_monitor.log" 2>&1 &
        MONITOR_PID=$!
        echo "✅ マスターモニターが起動しました (PID: $MONITOR_PID)"
        echo "📋 停止方法: kill $MONITOR_PID"
        echo "📄 ログ確認: tail -f $LOGS_DIR/master_monitor.log"
        echo "$MONITOR_PID" > "$LOGS_DIR/master_monitor.pid"
        ;;
    3)
        echo "🧪 テスト実行を開始..."
        echo "既存プロジェクトの一覧:"
        ls -1 "$BASE_DIR/deliverables/" 2>/dev/null || echo "プロジェクトが見つかりません"
        echo ""
        read -p "テスト対象のプロジェクト名: " test_project
        
        if [ -d "$BASE_DIR/deliverables/$test_project" ]; then
            echo "📊 レポート生成テスト..."
            "$SCRIPT_DIR/generate_completion_report.sh" "$test_project"
            echo ""
            echo "📱 LINE通知テスト..."
            "$SCRIPT_DIR/send_line_notification.sh" "$test_project"
        else
            echo "❌ プロジェクト '$test_project' が見つかりません"
        fi
        ;;
    *)
        echo "❌ 無効な選択です"
        exit 1
        ;;
esac