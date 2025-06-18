#!/usr/bin/env bash

# 引数チェック
if [ $# -lt 2 ]; then
    echo "Usage: $0 <project_name> <idea_file>"
    echo "Example: $0 my-app ../ideas/my_app_idea.txt"
    echo ""
    echo "The idea file should contain your detailed project description."
    exit 1
fi

PROJECT_NAME=$1
IDEA_FILE=$2
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DELIVERABLES_DIR="$BASE_DIR/deliverables"
PROJECT_DIR="$DELIVERABLES_DIR/$PROJECT_NAME"
PROMPTS_DIR="$BASE_DIR/prompts"
PROJECT_PROMPT="$PROMPTS_DIR/${PROJECT_NAME}_prompt.md"

# アイデアファイルの存在確認
if [ ! -f "$IDEA_FILE" ]; then
    echo "Error: Idea file '$IDEA_FILE' does not exist"
    exit 1
fi

# プロジェクトディレクトリ作成
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating new project: $PROJECT_NAME"
    "$SCRIPT_DIR/create_project.sh" "$PROJECT_NAME"
fi

# テンプレートからプロジェクト固有のプロンプトを作成
echo "Creating project-specific prompt..."
# sedの代わりにawkを使用して安全に置換
awk -v idea_file="$IDEA_FILE" '
BEGIN {
    while ((getline line < idea_file) > 0) {
        idea = idea (NR>1 ? "\n" : "") line
    }
    close(idea_file)
}
/{{USER_IDEA}}/ {
    print idea
    next
}
{print}
' "$PROMPTS_DIR/master_builder_template.md" > "$PROJECT_PROMPT"

echo "🤖 Starting OPTIMIZED autonomous development for: $PROJECT_NAME"
echo "📄 Using idea from: $IDEA_FILE"
echo "🎯 Using 8-subagent workflow (reduced from 15 for token efficiency)"
echo "📋 Phases: Plan→Implement→Test→Review→Build→Document→GitHub→Verify"
echo ""

# 自動開発を開始
cd "$PROJECT_DIR"
echo "🚀 Starting optimized development process..."
echo "📊 Using 8-subagent workflow for efficient token usage"
claude --dangerously-skip-permissions "$(cat "$PROJECT_PROMPT")"

# 開発完了後の処理
echo "🔄 Post-development processing..."

# GitHub統合の確認
if [ -d ".git" ]; then
    echo "✅ Git repository found"
    
    # リモートリポジトリが設定されているかチェック
    if git remote get-url origin > /dev/null 2>&1; then
        echo "📤 Pushing to existing remote repository..."
        git push origin main || git push origin master
    else
        echo "⚠️ No remote repository configured. Please set up GitHub integration manually."
    fi
fi

# ログ記録
echo "$(date): Completed project $PROJECT_NAME" >> "$BASE_DIR/logs/project_completion.log"

# 完了後、プロジェクト固有のプロンプトを削除
rm "$PROJECT_PROMPT"