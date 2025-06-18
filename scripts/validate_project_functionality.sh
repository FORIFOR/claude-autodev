#!/usr/bin/env bash

# プロジェクトの実際の動作可能性を検証

if [ $# -lt 1 ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

PROJECT_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$BASE_DIR/deliverables/$PROJECT_NAME"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

echo "🔍 Validating project functionality: $PROJECT_NAME"
echo "================================================="

validation_score=0
max_score=7

# 1. 依存関係のインストールテスト
echo ""
echo "1️⃣ Testing dependency installation..."
if [ -f "requirements.txt" ]; then
    # Python仮想環境作成
    if [ ! -d "test_venv" ]; then
        python3 -m venv test_venv >/dev/null 2>&1
    fi
    
    source test_venv/bin/activate
    pip install -r requirements.txt --quiet --no-warn-script-location >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
        ((validation_score++))
    else
        echo "❌ Failed to install dependencies"
    fi
    deactivate 2>/dev/null
elif [ -f "package.json" ]; then
    npm install >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ NPM dependencies installed successfully"
        ((validation_score++))
    else
        echo "❌ Failed to install NPM dependencies"
    fi
else
    echo "⚠️  No dependency file found (requirements.txt/package.json)"
fi

# 2. メインアプリケーションの起動テスト
echo ""
echo "2️⃣ Testing main application startup..."
main_executable=false

if [ -f "test_venv/bin/activate" ]; then
    source test_venv/bin/activate
fi

# Python プロジェクト
if [ -f "main.py" ]; then
    timeout 10s python3 main.py --help >/dev/null 2>&1 && main_executable=true
elif [ -f "cli.py" ]; then
    timeout 10s python3 cli.py --help >/dev/null 2>&1 && main_executable=true
elif [ -f "app.py" ]; then
    timeout 10s python3 app.py --help >/dev/null 2>&1 && main_executable=true
elif [ -f "src/main.py" ]; then
    timeout 10s python3 src/main.py --help >/dev/null 2>&1 && main_executable=true
# Node.js プロジェクト
elif [ -f "package.json" ]; then
    timeout 10s npm start >/dev/null 2>&1 && main_executable=true
fi

if $main_executable; then
    echo "✅ Main application starts without errors"
    ((validation_score++))
else
    echo "❌ Main application fails to start or has no clear entry point"
fi

if [ -f "test_venv/bin/activate" ]; then
    deactivate 2>/dev/null
fi

# 3. テストの実行
echo ""
echo "3️⃣ Running automated tests..."
test_passed=false

if [ -f "test_venv/bin/activate" ]; then
    source test_venv/bin/activate
fi

if [ -d "tests" ] && [ -f "requirements.txt" ]; then
    timeout 60s python3 -m pytest tests/ --tb=no -q >/dev/null 2>&1 && test_passed=true
elif [ -f "package.json" ]; then
    timeout 60s npm test >/dev/null 2>&1 && test_passed=true
fi

if $test_passed; then
    echo "✅ Tests pass successfully"
    ((validation_score++))
else
    echo "❌ Tests fail or no tests found"
fi

if [ -f "test_venv/bin/activate" ]; then
    deactivate 2>/dev/null
fi

# 4. ビルドプロセス
echo ""
echo "4️⃣ Testing build process..."
build_success=false

if [ -f "package.json" ] && grep -q "build" package.json; then
    timeout 120s npm run build >/dev/null 2>&1 && build_success=true
elif [ -f "setup.py" ]; then
    timeout 60s python3 setup.py build >/dev/null 2>&1 && build_success=true
elif [ -f "Dockerfile" ]; then
    timeout 180s docker build -t "test-$PROJECT_NAME" . >/dev/null 2>&1 && build_success=true
else
    # ビルドプロセスが不要な場合はスキップ
    build_success=true
fi

if $build_success; then
    echo "✅ Build process completes successfully"
    ((validation_score++))
else
    echo "❌ Build process fails"
fi

# 5. 設定ファイルの妥当性
echo ""
echo "5️⃣ Validating configuration files..."
config_valid=true

# JSON ファイルの構文チェック
for json_file in $(find . -name "*.json" -maxdepth 2 2>/dev/null); do
    if ! python3 -m json.tool "$json_file" >/dev/null 2>&1; then
        echo "❌ Invalid JSON: $json_file"
        config_valid=false
    fi
done

# YAML ファイルの基本チェック（python3 -c で簡易チェック）
for yaml_file in $(find . -name "*.yml" -o -name "*.yaml" -maxdepth 2 2>/dev/null); do
    if [ -f "$yaml_file" ]; then
        # 基本的なYAML構文チェック
        if ! python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" >/dev/null 2>&1; then
            echo "❌ Invalid YAML: $yaml_file"
            config_valid=false
        fi
    fi
done

if $config_valid; then
    echo "✅ Configuration files are valid"
    ((validation_score++))
else
    echo "❌ Configuration file validation failed"
fi

# 6. ドキュメントの完全性
echo ""
echo "6️⃣ Checking documentation completeness..."
doc_complete=true

# README.mdの必須セクション
if [ -f "README.md" ]; then
    required_sections=("install" "usage" "example")
    for section in "${required_sections[@]}"; do
        if ! grep -qi "$section" README.md; then
            doc_complete=false
            break
        fi
    done
else
    doc_complete=false
fi

if $doc_complete; then
    echo "✅ Documentation is complete"
    ((validation_score++))
else
    echo "❌ Documentation is incomplete"
fi

# 7. セキュリティ基本チェック
echo ""
echo "7️⃣ Basic security checks..."
security_ok=true

# ハードコードされた秘密情報のチェック
if grep -r "password\|secret\|token\|key" --include="*.py" --include="*.js" --include="*.ts" . | grep -v -i "example\|test\|placeholder" >/dev/null 2>&1; then
    echo "⚠️  Potential hardcoded secrets found"
    security_ok=false
fi

# .envファイルの存在チェック
if [ -f ".env" ] && [ ! -f ".env.example" ]; then
    echo "⚠️  .env file without .env.example template"
    security_ok=false
fi

if $security_ok; then
    echo "✅ Basic security checks pass"
    ((validation_score++))
else
    echo "❌ Security issues detected"
fi

# クリーンアップ
rm -rf test_venv 2>/dev/null

# 最終評価
echo ""
echo "================================================="
echo "📊 Functionality Validation Score: $validation_score/$max_score"

if [ $validation_score -ge 5 ]; then
    echo "🎉 Project is FUNCTIONALLY COMPLETE and ready for use"
    exit 0
elif [ $validation_score -ge 3 ]; then
    echo "⚠️  Project has MINOR ISSUES but is mostly functional"
    exit 1
else
    echo "❌ Project has MAJOR ISSUES and is not ready for use"
    exit 2
fi