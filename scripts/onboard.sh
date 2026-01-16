#!/bin/bash
set -euo pipefail
echo "=== ChittyTrace-CC Onboarding ==="
curl -s -X POST "${GETCHITTY_ENDPOINT:-https://get.chitty.cc/api/onboard}" \
  -H "Content-Type: application/json" \
  -d '{"service_name":"ChittyTrace-CC","organization":"CHITTYAPPS","type":"service","tier":4,"domains":["trace-cc.chitty.cc"]}' | jq .
