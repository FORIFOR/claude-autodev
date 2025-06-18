#!/usr/bin/env bash

# Cloudflare Tunnel セットアップスクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "🌐 Cloudflare Tunnel Setup for LINE Webhook"
echo "=========================================="

# 1. cloudflared インストール確認
if ! command -v cloudflared >/dev/null 2>&1; then
    echo "📦 Installing cloudflared..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install cloudflare/cloudflare/cloudflared
    else
        echo "Please install cloudflared manually:"
        echo "  Ubuntu/Debian: sudo apt-get install cloudflared"
        echo "  https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation"
        exit 1
    fi
fi

echo "✅ cloudflared is installed"

# 2. LINE Webhook Server のポート確認
WEBHOOK_PORT=5001
echo "📡 LINE Webhook Server port: $WEBHOOK_PORT"

# 3. トンネル起動方法の選択
echo ""
echo "Choose tunnel type:"
echo "1) Quick tunnel (random URL, temporary)"
echo "2) Named tunnel (fixed URL, requires Cloudflare account)"
read -p "Select (1-2): " tunnel_type

case $tunnel_type in
    1)
        echo "🚀 Starting quick tunnel..."
        echo ""
        echo "Running: cloudflared tunnel --url http://localhost:$WEBHOOK_PORT"
        echo ""
        echo "⚠️  Copy the HTTPS URL that appears below and add '/webhook' to it"
        echo "📋 Example: https://fuzzy-fox-123.trycloudflare.com/webhook"
        echo ""
        echo "Then update your LINE Developer Console:"
        echo "1. Go to https://developers.line.biz/"
        echo "2. Select your channel"
        echo "3. Messaging API > Webhook URL"
        echo "4. Paste the full URL (with /webhook)"
        echo "5. Click Verify"
        echo ""
        echo "Press Ctrl+C to stop the tunnel"
        echo "===========================================" 
        
        # トンネル起動
        cloudflared tunnel --url http://localhost:$WEBHOOK_PORT
        ;;
        
    2)
        echo "📝 Named tunnel setup requires:"
        echo "- Cloudflare account (free)"
        echo "- Your own domain managed by Cloudflare"
        echo ""
        read -p "Continue? (y/n): " continue_named
        
        if [ "$continue_named" != "y" ]; then
            exit 0
        fi
        
        # 認証
        echo "🔐 Authenticating with Cloudflare..."
        cloudflared tunnel login
        
        # トンネル名入力
        read -p "Enter tunnel name (e.g., autodev-line): " tunnel_name
        
        # トンネル作成
        echo "🏗️  Creating tunnel: $tunnel_name"
        cloudflared tunnel create $tunnel_name
        
        # ドメイン設定
        read -p "Enter your domain (e.g., line.yourdomain.com): " domain_name
        
        echo "🌐 Routing $domain_name to tunnel..."
        cloudflared tunnel route dns $tunnel_name $domain_name
        
        # 設定ファイル作成
        config_dir="$HOME/.cloudflared"
        mkdir -p "$config_dir"
        
        cat > "$config_dir/$tunnel_name.yml" << EOF
tunnel: $tunnel_name
credentials-file: $config_dir/$(cloudflared tunnel info $tunnel_name -o json | jq -r '.id').json

ingress:
  - hostname: $domain_name
    service: http://localhost:$WEBHOOK_PORT
  - service: http_status:404
EOF
        
        echo "✅ Named tunnel configured!"
        echo ""
        echo "📋 Your webhook URL: https://$domain_name/webhook"
        echo ""
        echo "To start the tunnel:"
        echo "  cloudflared tunnel run $tunnel_name"
        echo ""
        echo "To run as a service:"
        echo "  cloudflared service install"
        echo "  cloudflared tunnel run $tunnel_name"
        ;;
        
    *)
        echo "❌ Invalid selection"
        exit 1
        ;;
esac