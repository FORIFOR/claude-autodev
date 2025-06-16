# 実行方法の違いと出力先

## 📁 成果物の格納場所

全ての方法で成果物は **同じ場所** に格納されます：
```
/Users/horioshuuhei/Projects/claude-autodev/deliverables/<プロジェクト名>/
```

## 🔧 3つの実行方法の違い

### 1. `run_once.sh` (従来の方法)
```bash
./run_once.sh ../deliverables/AITec最新流行整理ツール ../prompts/master_builder_prompt.md
```
- **プロジェクト名**: 既存ディレクトリ名を指定
- **プロンプト**: 既存ファイルを直接指定
- **用途**: 既存プロジェクトの修正・更新
- **成果物**: `deliverables/AITec最新流行整理ツール/`

### 2. `start_project.sh` (短いアイデア用)
```bash
./start_project.sh "my-todo-app" "TODOアプリをReactで作成"
```
- **プロジェクト名**: 新規作成される（`my-todo-app`）
- **プロンプト**: 自動生成される（`prompts/my-todo-app_prompt.md`）
- **用途**: 新規プロジェクト（短いアイデア）
- **成果物**: `deliverables/my-todo-app/`

### 3. `start_project_file.sh` (長いアイデア用)
```bash
./start_project_file.sh "perfect-keiba-AI" "../ideas/example_idea_template.txt"
```
- **プロジェクト名**: 新規作成される（`perfect-keiba-AI`）
- **プロンプト**: 自動生成される（`prompts/perfect-keiba-AI_prompt.md`）
- **用途**: 新規プロジェクト（長い・詳細なアイデア）
- **成果物**: `deliverables/perfect-keiba-AI/`

## ⚠️ 重要な注意点

### プロジェクト名の重複
- **同じプロジェクト名を指定すると既存ファイルが上書きされます**
- 例：`perfect-keiba-AI` を再実行すると既存の内容が消えます

### 安全な実行方法
```bash
# ✅ 良い例：異なる名前を使用
./start_project.sh "todo-app-v1" "TODOアプリ"
./start_project.sh "todo-app-v2" "改良版TODOアプリ"

# ❌ 危険な例：同じ名前を再使用
./start_project.sh "todo-app" "TODOアプリ"
./start_project.sh "todo-app" "別のアプリ"  # 上書きされる！
```

## 📋 現在の成果物

現在の `deliverables/` ディレクトリ：
```
deliverables/
├── AITec最新流行整理ツール/    # run_once.sh で作成/更新
└── perfect-keiba-AI/          # start_project_file.sh で作成
```

## 🔄 プロンプトファイルの管理

- `run_once.sh`: 既存プロンプトファイルを使用
- `start_project.sh` / `start_project_file.sh`: プロジェクト別プロンプトを自動生成

生成されるプロンプトファイル：
```
prompts/
├── master_builder_template.md     # テンプレート
├── master_builder_prompt.md       # 手動編集用
├── perfect-keiba-AI_prompt.md     # 自動生成
└── <プロジェクト名>_prompt.md      # 各プロジェクト用
```