#!/usr/bin/env bash

# ローカル通知システム（macOS用）

if [ $# -lt 1 ]; then
    echo "Usage: $0 <project_name> [summary]"
    exit 1
fi

PROJECT_NAME=$1
SUMMARY=${2:-"プロジェクトが完了しました"}

# macOS通知を送信
if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"$SUMMARY\" with title \"🎉 Claude Autodev\" subtitle \"プロジェクト: $PROJECT_NAME\""
    echo "✅ macOS notification sent"
fi

# ターミナル通知
echo ""
echo "🎉====================================🎉"
echo "   Claude Autodev - プロジェクト完了"
echo "🎉====================================🎉"
echo ""
echo "📋 プロジェクト: $PROJECT_NAME"
echo "⏰ 完了時刻: $(date '+%Y/%m/%d %H:%M:%S')"
echo "✅ $SUMMARY"
echo ""
echo "🔗 詳細: deliverables/$PROJECT_NAME/"
echo ""

# ログファイルに記録
LOGS_DIR="$(dirname "$(dirname "$0")")/logs"
echo "$(date): PROJECT COMPLETED - $PROJECT_NAME - $SUMMARY" >> "$LOGS_DIR/notifications.log"

# 音で通知（オプション）
if command -v afplay >/dev/null 2>&1; then
    afplay /System/Library/Sounds/Glass.aiff 2>/dev/null &
fi