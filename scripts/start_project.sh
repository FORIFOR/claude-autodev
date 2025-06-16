#!/usr/bin/env bash

# 引数チェック
if [ $# -lt 2 ]; then
    echo "Usage: $0 <project_name> \"<your idea>\""
    echo "Example: $0 my-app \"Create a todo app with React and Firebase\""
    exit 1
fi

PROJECT_NAME=$1
USER_IDEA=$2
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DELIVERABLES_DIR="$BASE_DIR/deliverables"
PROJECT_DIR="$DELIVERABLES_DIR/$PROJECT_NAME"
PROMPTS_DIR="$BASE_DIR/prompts"
PROJECT_PROMPT="$PROMPTS_DIR/${PROJECT_NAME}_prompt.md"

# プロジェクトディレクトリ作成
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating new project: $PROJECT_NAME"
    "$SCRIPT_DIR/create_project.sh" "$PROJECT_NAME"
fi

# テンプレートをコピーして、USER_IDEAを置換
echo "Creating project-specific prompt..."
cp "$PROMPTS_DIR/master_builder_template.md" "$PROJECT_PROMPT"

# プロンプトファイル内の{{USER_IDEA}}を置換
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|{{USER_IDEA}}|$USER_IDEA|g" "$PROJECT_PROMPT"
else
    # Linux
    sed -i "s|{{USER_IDEA}}|$USER_IDEA|g" "$PROJECT_PROMPT"
fi

echo "Starting autonomous development for: $PROJECT_NAME"
echo "Idea: $USER_IDEA"
echo ""

# 自動開発を開始
cd "$PROJECT_DIR"
claude --dangerously-skip-permissions "$(cat "$PROJECT_PROMPT")"

# 完了後、プロジェクト固有のプロンプトを削除（オプション）
# rm "$PROJECT_PROMPT"