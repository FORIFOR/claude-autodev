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

# 3. src/ ディレクトリに実際のコードファイルがある
if [ -d "src" ] && [ "$(find src -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.java" -o -name "*.go" | wc -l)" -gt 0 ]; then
    echo "✅ Source code files found in src/"
    ((completion_criteria++))
else
    echo "❌ No source code files in src/"
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

# 5. "DONE" キーワードがRELEASE.mdまたは最新のGitコミットメッセージに含まれている
done_found=false
if [ -f "RELEASE.md" ] && grep -q "DONE" "RELEASE.md"; then
    done_found=true
fi

if [ -d ".git" ]; then
    latest_commit=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "")
    if echo "$latest_commit" | grep -q "DONE"; then
        done_found=true
    fi
fi

if $done_found; then
    echo "✅ 'DONE' keyword found"
    ((completion_criteria++))
else
    echo "❌ 'DONE' keyword not found"
fi

# 判定結果
echo "📊 Completion score: $completion_criteria/5"

# 4つ以上の条件を満たせば完了とみなす
if [ $completion_criteria -ge 4 ]; then
    echo "🎉 Project is considered COMPLETE"
    exit 0
else
    echo "⏳ Project is still IN PROGRESS"
    exit 1
fi