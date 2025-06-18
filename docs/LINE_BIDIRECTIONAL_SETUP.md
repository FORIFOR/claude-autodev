# 🔄 LINE 双方向通信セットアップガイド

## 📊 現在の状況

| 機能 | 状態 | 説明 |
|------|------|------|
| **プッシュ通知** (Bot→ユーザー) | 🟢 動作中 | プロジェクト完了時の通知 |
| **コマンド受信** (ユーザー→Bot) | 🔴 要設定 | `/create`, `/modify` コマンド |

## 🚀 5分でできる！Cloudflare Tunnel設定

### Step 1: Cloudflare Tunnel起動

```bash
cd /Users/horioshuuhei/Projects/claude-autodev/scripts
./setup_cloudflare_tunnel.sh
```

### Step 2: Quick Tunnel（すぐ試す）

1. オプション `1` を選択
2. 表示されるURL（例: `https://fuzzy-fox-123.trycloudflare.com`）をコピー
3. URLの末尾に `/webhook` を追加

### Step 3: LINE Developer Console設定

1. [LINE Developers](https://developers.line.biz/) にアクセス
2. あなたのチャンネルを選択
3. **Messaging API** タブ → **Webhook設定**
4. **Webhook URL**: `https://あなたのURL.trycloudflare.com/webhook`
5. **検証** ボタンをクリック → ✅ Success

## 📱 使用可能になるコマンド

```
# 新規プロジェクト作成
/create my-app ReactでTODOアプリを作成

# 既存プロジェクトの仕様変更
/modify my-app ダークモード機能を追加

# プロジェクト一覧
/list

# ヘルプ
/help
```

## 🏗 システム構成図

```
┌─────────────┐     HTTPS      ┌─────────────────┐
│    LINE     │ ─────────────→ │ Cloudflare Edge │
│   Server    │                └────────┬────────┘
└─────────────┘                         │
                                       │ Tunnel
┌─────────────┐                         ↓
│  あなたの   │     Push API    ┌─────────────────┐
│   LINE      │ ←───────────── │ localhost:5001  │
└─────────────┘                │  Webhook Server │
                               └─────────────────┘
```

## 🔧 トラブルシューティング

### エラー: "Webhook URL verification failed"
- URLの末尾に `/webhook` を付け忘れていないか確認
- Cloudflare Tunnelが起動中か確認
- LINE Webhook Serverが起動中か確認（port 5001）

### コマンドが反応しない
- Webhook URLが正しく設定されているか確認
- ログを確認: `tail -f /Users/horioshuuhei/Projects/claude-autodev/logs/line_server.log`

## 🌟 より安定した運用（オプション）

### Named Tunnel（固定URL）
```bash
./setup_cloudflare_tunnel.sh
# オプション 2 を選択
# 独自ドメイン（例: line.yourdomain.com）を設定
```

### 無料クラウドへデプロイ
- **Vercel**: `vercel.json` でサーバーレス関数として
- **Render**: Dockerfileでコンテナデプロイ
- **Cloud Run**: 月200万リクエストまで無料

## 📝 セキュリティ注意事項

1. **Channel Secret**の検証を有効化（本番環境）
2. **User ID**による認証を維持
3. **HTTPS**必須（Cloudflareが自動処理）

---

これで、**完全な双方向LINE連携**が実現します！

プロジェクト作成から完了通知まで、すべてLINEで操作できるようになります。🎉