# Claude Autodev - 完全自動開発システム

Claude Code の `/subagent` 機能を使った **無人で動作する開発システム** です。アイデア一つから完成品まで、寝ている間に自動で作り上げます。

## 🎯 このシステムでできること

- **完全無人開発**: アイデアを入力したら放置するだけ
- **企画→実装→テスト→納品**: 全工程を自動化
- **Git管理**: コミット履歴で開発過程を追跡可能
- **プロジェクト管理**: 複数プロジェクトを分離して管理

## 🏗 システム構成と仕組み

### 基本構造
```
claude-autodev/
├── scripts/              # 実行スクリプト（制御層）
│   ├── run_once.sh          # 基本実行エンジン
│   ├── create_project.sh    # プロジェクト生成器
│   ├── start_project.sh     # 短いアイデア用（直接入力）
│   └── start_project_file.sh # 長いアイデア用（ファイル入力）
├── prompts/             # AI指示書（頭脳）
│   ├── master_builder_template.md  # マスターテンプレート
│   └── <project>_prompt.md        # プロジェクト別プロンプト（自動生成）
├── ideas/               # アイデアファイル保管庫 🆕
│   ├── example_idea_template.txt  # テンプレート
│   └── x_repost_app.txt          # 実例
└── deliverables/        # 成果物（出力層）
    └── <project_name>/
        ├── src/         # 生成されたソースコード
        ├── tests/       # 自動生成テスト
        ├── SPEC.md      # 自動作成された仕様書
        └── RELEASE.md   # 完成品リリースノート
```

### 動作原理（Parent ⇄ Child エージェント）

```
┌─────────────────┐    /subagent呼び出し    ┌─────────────────┐
│   親エージェント    │ ────────────────────→ │  子エージェント1    │
│  (Master Builder) │                      │   (Planner)     │
│                 │ ←──── 仕様書返却 ────── │                 │
└─────────────────┘                      └─────────────────┘
         │
         │ /subagent呼び出し
         ▼
┌─────────────────┐    実装完了報告    ┌─────────────────┐
│   子エージェント2   │ ────────────────→ │   子エージェント3   │
│  (Implementer)  │                  │    (Tester)     │
└─────────────────┘                  └─────────────────┘
```

1. **親エージェント（Master Builder）**: 全体統制・進行管理
2. **子エージェント（Subagents）**: 特定タスク実行（仕様策定・実装・テスト等）
3. **状態管理**: ファイルシステム + Git コミットで永続化
4. **終了制御**: 最大15子エージェント制限で無限ループ防止

## 📋 セットアップ手順（初心者向け）

### 必要なもの
- Claude CLI （`brew install claude` または `pip install claude`）
- Git
- macOS/Linux 環境

### Step 1: システムの準備
```bash
# 1. プロジェクトディレクトリに移動
cd /Users/horioshuuhei/Projects/claude-autodev

# 2. スクリプトに実行権限を付与
chmod +x scripts/*.sh
```

### Step 2: 新規プロジェクト作成
```bash
# プロジェクト名を指定して作成
cd scripts
./create_project.sh my-web-app
```

### Step 3: アイデアの設定
```bash
# プロンプトファイルを編集
code ../prompts/master_builder_prompt.md
# または
vim ../prompts/master_builder_prompt.md
```

ファイル内の `<<<USER_IDEA>>>` を実際のアイデアに置換：
```markdown
## 💬 User Idea
家計簿アプリを Python FastAPI + SQLite で作りたい
```

### Step 4: 自動開発の実行

#### 方法1: 短いアイデアの場合（ワンコマンド実行）
```bash
# アイデアを直接指定して実行
./start_project.sh "my-todo-app" "TODOアプリをReactとFirebaseで作成"
```

#### 方法2: 長い・詳細なアイデアの場合（ファイル指定）🆕
```bash
# 1. アイデアファイルを作成
vim ../ideas/my_detailed_app.txt

# 2. ファイルを指定して実行
./start_project_file.sh "my-app" "../ideas/my_detailed_app.txt"
```

#### 方法3: 従来の方法（プロンプトファイル編集）
```bash
# プロンプトファイルを編集してから実行
./run_once.sh ../deliverables/my-web-app ../prompts/master_builder_prompt.md
```

### Step 5: 結果の確認
```bash
# 生成されたプロジェクトを確認
cd ../deliverables/my-web-app
ls -la

# 開発履歴を確認
git log --oneline

# アプリケーションを実行
python src/main.py  # または生成された実行ファイル
```

## 🔧 高度な使い方

### 複数プロジェクトの並列実行（改良版 ✨）
```bash
# ターミナル1
./start_project.sh "web-app" "ECサイトをNext.jsとStripeで作成"

# ターミナル2 
./start_project.sh "mobile-app" "天気予報アプリをReact Nativeで作成"

# ターミナル3
./start_project.sh "api-service" "REST APIをFastAPIとPostgreSQLで作成"
```

**メリット**：
- プロンプトファイルの編集不要
- プロジェクトごとに独立したプロンプトファイルを自動生成
- 何個でも同時実行可能

### バックグラウンド実行（夜間放置）
```bash
# nohupで実行してログ保存
nohup ./run_once.sh ../deliverables/myapp ../prompts/master_builder_prompt.md > ../logs/myapp.log 2>&1 &

# 進捗確認
tail -f ../logs/myapp.log
```

### プロンプトのカスタマイズ
プロンプトファイルを複製して用途別に作成：
```bash
cp ../prompts/master_builder_prompt.md ../prompts/web_app_prompt.md
cp ../prompts/master_builder_prompt.md ../prompts/api_prompt.md
```

## 🚨 トラブルシューティング

### 権限エラーが出る場合
```bash
# スクリプトに実行権限を付与
chmod +x scripts/*.sh

# Claude CLIの権限確認
claude --help | grep permission
```

### 無限ループで終わらない場合
- システムは最大15子エージェント制限済み
- 強制停止: `Ctrl+C`
- ログ確認: プロジェクトディレクトリ内のファイル変更を監視

### 生成コードが動かない場合
```bash
# 依存関係をインストール
cd deliverables/myapp
pip install -r requirements.txt  # Python の場合
npm install                      # Node.js の場合
```

## 📊 成果物の構成

開発完了後の `deliverables/<project_name>/` 構成：
```
my-web-app/
├── .git/                 # Git履歴（開発過程の記録）
├── .gitignore           # 自動生成
├── src/                 # メインソースコード
│   ├── main.py
│   ├── models/
│   └── api/
├── tests/               # 自動生成テスト
│   ├── test_main.py
│   └── test_api.py
├── requirements.txt     # 依存関係
├── SPEC.md             # 詳細仕様書
├── TODO.md             # 完了済みタスクリスト
├── README.md           # プロジェクト説明
└── RELEASE.md          # リリースノート
```

## 💡 効果的な使い方のコツ

1. **具体的なアイデアを書く**: 「ECサイト」より「商品登録・決済機能付きECサイト」
2. **技術スタックを指定**: 「Python FastAPI + PostgreSQL + React」
3. **シンプルに始める**: 最初は小さな機能から
4. **結果を確認してから次へ**: 生成されたコードをレビューしてから次のプロジェクト

このシステムで、一晩でMVPレベルのアプリケーションが完成します！

## 🎛️ マスターモニターシステム（NEW! 🚀）

### 自動監視・通知機能
プロジェクトの完了を自動監視し、LINE通知でお知らせします。

#### 起動方法
```bash
cd scripts
./start_master_monitor.sh
```

#### 機能
- 🔍 **プロジェクト完了の自動検知**
- 📱 **LINE通知の自動送信**
- 📊 **完了レポートの自動生成**
- 📋 **開発統計の自動収集**

#### 通知内容例
```
🎉 プロジェクト完了通知

📋 プロジェクト: my-todo-app
⏰ 完了時刻: 2024/06/15 14:30
📁 生成ファイル数: 25
📖 README: ✅
🧪 テスト: ✅

🔗 パス: deliverables/my-todo-app/
```

#### マスターモニターの3つの実行モード
```bash
# 1. フォアグラウンド実行（監視画面表示）
./start_master_monitor.sh → 1を選択

# 2. バックグラウンド実行（デーモン化）
./start_master_monitor.sh → 2を選択

# 3. テスト実行（既存プロジェクトで確認）
./start_master_monitor.sh → 3を選択
```

### 完全自動運用の例
```bash
# ターミナル1: マスターモニター起動（バックグラウンド）
./start_master_monitor.sh

# ターミナル2-4: 複数プロジェクトを同時実行
./start_project.sh "web-app" "ECサイト作成"
./start_project.sh "mobile-app" "天気アプリ作成"  
./start_project.sh "api-service" "REST API作成"

# → 各プロジェクト完了時にLINE通知が自動送信される
```

### 📱 双方向LINE通信（NEW! ✨）

#### LINE Webhook Server 起動
```bash
cd scripts
./start_line_server.sh
```

#### LINEからプロジェクト操作
```
# 新規プロジェクト作成
/create todo-app TODOアプリをReactで作成してください

# 既存プロジェクトの仕様変更
/modify todo-app ダークモード機能を追加してください

# プロジェクト一覧確認
/list

# ヘルプ
/help
```

#### 完了判定の改善
以下の5つの条件中4つ以上を満たした場合のみ「完了」と判定：
- ✅ RELEASE.md が存在し内容がある
- ✅ README.md が存在し内容がある  
- ✅ src/ にコードファイルが存在
- ✅ Git コミットが3つ以上
- ✅ "DONE" キーワードが含まれている