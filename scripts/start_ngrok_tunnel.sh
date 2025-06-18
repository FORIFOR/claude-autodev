#!/usr/bin/env bash

echo "🌐 Starting ngrok tunnel for LINE Webhook Server"
echo "=============================================="
echo ""
echo "LINE Webhook Server is running on port: 5001"
echo ""
echo "Starting ngrok tunnel..."
echo ""
echo "📋 IMPORTANT: After ngrok starts:"
echo "1. Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)"
echo "2. Add '/webhook' to the end"
echo "3. Update LINE Developer Console with the full URL"
echo ""
echo "Press Ctrl+C to stop the tunnel"
echo "=============================================="
echo ""

# Start ngrok tunnel for port 5001
ngrok http 5001