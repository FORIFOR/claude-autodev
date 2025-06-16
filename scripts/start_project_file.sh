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

echo "Starting autonomous development for: $PROJECT_NAME"
echo "Using idea from: $IDEA_FILE"
echo ""

# 自動開発を開始
cd "$PROJECT_DIR"
claude --dangerously-skip-permissions "$(cat "$PROJECT_PROMPT")"

# 完了後、プロジェクト固有のプロンプトを削除（オプション）
# rm "$PROJECT_PROMPT"