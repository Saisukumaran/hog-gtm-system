#!/bin/bash
source .env

curl -X POST https://developer.thehog.ai/api/deep-research \
  -H "X-Access-Key: $HOG_AK" \
  -H "X-Secret-Key: $HOG_SK" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find individual people (not companies or agencies) who publicly identify as a Clay Certified Expert, Certified Clay Expert, or Clay Solutions Partner. Focus on people who have this visible in their LinkedIn headline, LinkedIn job title, or LinkedIn certifications section. Also include people who have publicly announced Clay certification on Twitter/X or LinkedIn posts. Exclude Clay employees. Return at least 20 people with their full name, current company, job title, LinkedIn profile URL, and specific evidence (e.g. exact LinkedIn headline text or post excerpt proving certification).",
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
              "evidence":     {"type": "string"}
            },
            "required": ["name", "linkedin_url", "evidence"]
          }
        }
      }
    },
    "budget": { "maxCredits": 300 }
  }'