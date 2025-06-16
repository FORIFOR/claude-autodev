#!/usr/bin/env bash

# 引数チェック
if [ $# -ne 2 ]; then
    echo "Usage: $0 <project_dir> <prompt_file>"
    echo "Example: $0 /path/to/myapp ../prompts/master_builder_prompt.md"
    exit 1
fi

PROJECT_DIR=$1
PROMPT_FILE=$2

# プロジェクトディレクトリの存在確認
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory '$PROJECT_DIR' does not exist"
    echo "Create it first with: ./create_project.sh <project_name>"
    exit 1
fi

# プロンプトファイルの存在確認
if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: Prompt file '$PROMPT_FILE' does not exist"
    exit 1
fi

echo "Starting autonomous development for: $PROJECT_DIR"
echo "Using prompt: $PROMPT_FILE"
echo ""

# プロンプトファイルの絶対パスを取得
PROMPT_FILE_ABS=$(cd "$(dirname "$PROMPT_FILE")" && pwd)/$(basename "$PROMPT_FILE")

# detach して朝まで放置したい場合は nohup など併用
cd "$PROJECT_DIR"
claude --dangerously-skip-permissions "$(cat "$PROMPT_FILE_ABS")"