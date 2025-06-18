#!/usr/bin/env bash

# プロジェクト完了の厳密なチェック

if [ $# -lt 1 ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

PROJECT_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$BASE_DIR/deliverables/$PROJECT_NAME"

if [ ! -d "$PROJECT_DIR" ]; then
    exit 1
fi

cd "$PROJECT_DIR"

# 完了判定の条件（すべて満たす必要がある）
completion_criteria=0

echo "🔍 Checking completion criteria for: $PROJECT_NAME"

# 1. RELEASE.md が存在し、内容がある
if [ -f "RELEASE.md" ] && [ -s "RELEASE.md" ]; then
    echo "✅ RELEASE.md exists and has content"
    ((completion_criteria++))
else
    echo "❌ RELEASE.md missing or empty"
fi

# 2. README.md が存在し、内容がある
if [ -f "README.md" ] && [ -s "README.md" ]; then
    echo "✅ README.md exists and has content"
    ((completion_criteria++))
else
    echo "❌ README.md missing or empty"
fi

# 3. ソースコードファイルがある（src/ディレクトリまたはルートディレクトリ）
src_files=$(find . -maxdepth 2 -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.java" -o -name "*.go" | grep -v venv | grep -v __pycache__ | wc -l)
if [ "$src_files" -gt 0 ]; then
    echo "✅ Source code files found ($src_files files)"
    ((completion_criteria++))
else
    echo "❌ No source code files found"
fi

# 4. Git コミットが少なくとも3つ以上ある（開発活動の証拠）
if [ -d ".git" ]; then
    commit_count=$(git rev-list --count HEAD 2>/dev/null || echo 0)
    if [ "$commit_count" -ge 3 ]; then
        echo "✅ Sufficient Git commits ($commit_count)"
        ((completion_criteria++))
    else
        echo "❌ Insufficient Git commits ($commit_count < 3)"
    fi
else
    echo "❌ No Git repository"
fi

# 5. "DONE" キーワードまたは完了を示すファイルが存在
done_found=false

# RELEASE.mdで"DONE"またはプロダクション/完成を示すキーワード
if [ -f "RELEASE.md" ] && (grep -qi "DONE\|production\|complete\|finished\|final" "RELEASE.md"); then
    done_found=true
fi

# 最新のGitコミットメッセージをチェック
if [ -d ".git" ]; then
    latest_commit=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "")
    if echo "$latest_commit" | grep -qi "DONE\|complete\|final\|finish"; then
        done_found=true
    fi
fi

# 完了を示すファイルの存在チェック
if [ -f "DONE" ] || [ -f "COMPLETE" ] || [ -f "FINISHED" ]; then
    done_found=true
fi

if $done_found; then
    echo "✅ Completion indicator found"
    ((completion_criteria++))
else
    echo "❌ No completion indicator found"
fi

# 判定結果
echo "📊 Completion score: $completion_criteria/5"

# 基本完了判定（4/5以上）
if [ $completion_criteria -ge 4 ]; then
    echo "📋 Basic completion criteria met. Running functionality validation..."
    
    # 実際の動作可能性をテスト
    if "$SCRIPT_DIR/validate_project_functionality.sh" "$PROJECT_NAME" >/dev/null 2>&1; then
        echo "🎉 Project is FUNCTIONALLY COMPLETE and ready for use"
        exit 0
    else
        echo "⚠️  Project files exist but functionality validation failed"
        echo "📝 This indicates the project may not actually work as intended"
        exit 1
    fi
else
    echo "⏳ Project is still IN PROGRESS"
    exit 1
fi