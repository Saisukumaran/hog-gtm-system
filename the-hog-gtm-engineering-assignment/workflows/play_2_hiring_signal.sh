#!/bin/bash
source .env

curl -X POST https://developer.thehog.ai/api/v1/companies/search \
  -H "X-Access-Key: $HOG_AK" \
  -H "X-Secret-Key: $HOG_SK" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "companies hiring GTM Engineer or RevOps in San Francisco",
    "limit": 25
  }'