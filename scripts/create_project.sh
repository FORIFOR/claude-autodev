#!/usr/bin/env bash

# プロジェクト名を引数から取得
PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: ./create_project.sh <project_name>"
    exit 1
fi

# プロジェクト用ディレクトリを作成
DELIVERABLES_DIR="/Users/horioshuuhei/Projects/claude-autodev/deliverables"
PROJECT_DIR="$DELIVERABLES_DIR/$PROJECT_NAME"

echo "Creating project: $PROJECT_NAME"

# プロジェクトディレクトリ構造を作成
mkdir -p "$PROJECT_DIR"/{src,tests,docs}
cd "$PROJECT_DIR"

# Git リポジトリを初期化
git init

# 基本的な .gitignore を作成
cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.env
.venv/
venv/
.DS_Store
*.log
EOF

# 初期コミット
git add .gitignore
git commit -m "Initial commit"

echo "Project created at: $PROJECT_DIR"
echo ""
echo "To start autonomous development, run:"
echo "  ./run_once.sh $PROJECT_DIR ../prompts/master_builder_prompt.md"