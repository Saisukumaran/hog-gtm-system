#!/bin/bash
source .env

curl -X POST https://developer.thehog.ai/api/deep-research \
  -H "X-Access-Key: $HOG_AK" \
  -H "X-Secret-Key: $HOG_SK" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find at least 20 individual people (not companies) who have publicly posted on LinkedIn or Twitter/X expressing frustrations, complaints, or pain points about B2B prospecting tools, outbound infrastructure, lead data quality, contact accuracy, enrichment tools, or GTM tooling costs. Focus on GTM operators, RevOps leaders, founders, growth operators, and GTM engineers. Look for posts where they mention tools like Clay, Apollo, ZoomInfo, Lusha, Clearbit, or similar and express dissatisfaction, limitations, or switching intent. Return their full name, current company, role, LinkedIn URL, their specific pain point in one sentence, and a direct quote or post excerpt as evidence.",
    "schema": {
      "type": "object",
      "properties": {
        "people": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name":         {"type": "string"},
              "company":      {"type": "string"},
              "role":         {"type": "string"},
              "linkedin_url": {"type": "string"},
              "pain_point":   {"type": "string"},
              "evidence":     {"type": "string"}
            },
            "required": ["name", "linkedin_url", "pain_point", "evidence"]
          }
        }
      }
    },
    "budget": { "maxCredits": 300 }
  }'