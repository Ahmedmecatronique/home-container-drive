#!/bin/bash

# Health check script for Mini-Cloud Storage

HOST=${HOST:-localhost}
PORT=${PORT:-8000}

# Try to reach the health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" http://${HOST}:${PORT}/api/health 2>/dev/null)

if [ "$response" = "200" ]; then
    echo "✅ Mini-Cloud Storage is healthy"
    exit 0
else
    echo "❌ Mini-Cloud Storage is not responding (HTTP $response)"
    exit 1
fi
