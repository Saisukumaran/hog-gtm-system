#!/bin/bash
source .env

OPERATION_ID=$1

if [ -z "$OPERATION_ID" ]; then
  echo "Usage: ./poll/poll_operation.sh <operationId>"
  exit 1
fi

echo "Polling: $OPERATION_ID"

while true; do
  RESULT=$(curl -s -X GET "https://developer.thehog.ai/api/operations/$OPERATION_ID" \
    -H "X-Access-Key: $HOG_AK" \
    -H "X-Secret-Key: $HOG_SK")

  STATUS=$(echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))")
  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    OUTPUT="output/result_$OPERATION_ID.json"
    echo $RESULT | python3 -m json.tool > "$OUTPUT"
    echo "Saved to $OUTPUT"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Failed."
    echo $RESULT
    break
  fi

  sleep 30
done