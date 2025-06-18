実装完了後、要件定義ディレクトリ `_docs/` に実装ログを残して。yyyy-mm-dd_機能名.md という形式で保存して。起動時も今週分のみで良いので読んで。作成時には各プロジ>ェクトごとにフォルダきちんと分けて整理してください
また、以下も参照してください

**— Simple & Critical Operating Rules for Claude-Autodev —**

## 1. Objective (Why does this repo exist?)
> **「課題を 1 行で書き、CI を緑にしてマージ」**  
> それ以外のことは *一切しない*。

---

## 2. Workflow (4 Steps, no shortcuts)

| # | フェーズ | 実行例 | 成功条件 |
|---|---------|-------|----------|
| 1 | PLAN   | `claude /subagent plan "CSV→JSON"` | 仕様 Markdown が返る |
| 2 | BUILD  | `claude /subagent implement "src/cli.py"` | PR が作成される |
| 3 | TEST   | `bash scripts/run_once.sh` (CI 上でも同じ) | すべて緑 ✅ |
| 4 | MERGE  | Gi:q
tHub “Merge” ボタン | main へ反映 |

*❌ CI が赤なら → `claude /subagent fix "<失敗ログ要約>"` → BUILD へ戻る。*

---

## 3. ルール (覚えるのは 3 つだけ)

1. **1 指示 = 1 目的** — 複数依頼は禁止  
2. **CI 緑以外はマージ禁止** — Branch Protection 有効化必須  
3. **/subagent のログは必ず `status/` へコミット** — 透明性確保

---

## 4. 手元チェック (同じコマンドが CI で走る)

```bash
# 依存インストール（初回のみ）
./scripts/setup_line_notify.sh   # 他 setup スクリプトがあれば実行

# 開発ループごとに
bash scripts/run_once.sh         # Lint → Test → Build → Dashboard 更新
open DASHBOARD.md                # 結果を目視確認


⸻

5. 成否判定 (run_once.sh 内に組み込み済み)
	•	PASS → ✅ PASS が DASHBOARD.md に記録、次フェーズへ
	•	FAIL → スクリプトが exit 1 で停止し、赤字 Reason を表示

⸻

6. 緊急停止

claude /subagent suspend "理由"

無限ループ・機密漏えいなど異常時は迷わず実行。

⸻

Last updated: 2025-06-18 (JST)


