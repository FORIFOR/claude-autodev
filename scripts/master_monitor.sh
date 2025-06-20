#!/usr/bin/env bash

# マスタータスク監視システム
# プロジェクトの完了を監視し、LINE通知を送信

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DELIVERABLES_DIR="$BASE_DIR/deliverables"
LOGS_DIR="$BASE_DIR/logs"
COMPLETED_DIR="$LOGS_DIR/completed"

# ログディレクトリ作成
mkdir -p "$LOGS_DIR" "$COMPLETED_DIR"

echo "🚀 Master Monitor System Started"
echo "Monitoring: $DELIVERABLES_DIR"
echo "Press Ctrl+C to stop"
echo ""

# 完了済みプロジェクトリストを読み込み
if [ -f "$LOGS_DIR/completed_projects.txt" ]; then
    completed_projects=$(cat "$LOGS_DIR/completed_projects.txt")
else
    completed_projects=""
fi

# 監視ループ
while true; do
    # 全プロジェクトをチェック
    for project_dir in "$DELIVERABLES_DIR"/*; do
        if [ -d "$project_dir" ]; then
            project_name=$(basename "$project_dir")
            
            # 既に通知済みかチェック
            if echo "$completed_projects" | grep -q "^$project_name$"; then
                continue
            fi
            
            # 厳密な完了判定
            if "$SCRIPT_DIR/check_project_completion.sh" "$project_name"; then
                echo "✅ Project completed: $project_name"
                
                # 完了レポート生成
                "$SCRIPT_DIR/generate_completion_report.sh" "$project_name"
                
                # LINE通知送信
                "$SCRIPT_DIR/send_line_notification.sh" "$project_name"
                
                # Slack通知送信
                python3 "$SCRIPT_DIR/send_slack_message.py" "$project_name" "プロジェクトが完了しました"
                
                # 完了リストに追加（重複チェック付き）
                if ! grep -q "^$project_name$" "$LOGS_DIR/completed_projects.txt" 2>/dev/null; then
                    echo "$project_name" >> "$LOGS_DIR/completed_projects.txt"
                    echo "$(date): $project_name completed and notified" >> "$LOGS_DIR/monitor.log"
                else
                    echo "$(date): $project_name already completed, skipping notification" >> "$LOGS_DIR/monitor.log"
                fi
                
                # メモリ内リストを更新
                completed_projects=$(cat "$LOGS_DIR/completed_projects.txt" 2>/dev/null || echo "")
            fi
        fi
    done
    
    # 30秒待機
    sleep 30
done