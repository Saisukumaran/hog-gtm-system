#!/usr/bin/env python3
"""
Hog Lead Intelligence — Collector: DIRECT ICP (pipeline validation play)
Finds people who ARE GTM Engineers / RevOps (direct potential Hog users),
then writes each as a raw lead into Airtable.

This is the pipeline-validation play: prove Hog -> Airtable works end to end,
then build the real intent plays (Pain Miner, Builders, Hiring) on the same pipe.

Run small first (LIMIT = 2) to confirm it works, then scale.
"""

import os
import time
import json
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# SETTINGS — change these as needed
# ---------------------------------------------------------------------------
LIMIT = 2  # keep SMALL for first run to protect credits (~60 cr/lead)
QUERY = "GTM Engineer or RevOps leaders at B2B SaaS companies"
SOURCE_PLAY = "Direct ICP"
SIGNAL = "Direct ICP"

# ---------------------------------------------------------------------------
# CREDENTIALS — set as environment variables before running (see instructions)
# ---------------------------------------------------------------------------
HOG_ACCESS_KEY = os.environ.get("HOG_AK", "ak_REPLACE_ME")
HOG_SECRET_KEY = os.environ.get("HOG_SK", "sk_REPLACE_ME")
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN", "pat_REPLACE_ME")

AIRTABLE_BASE_ID = "appDRIUIwdsXdJUj7"
AIRTABLE_TABLE = "Leads"

HOG_BASE = "https://developer.thehog.ai"
AIRTABLE_BASE = "https://api.airtable.com/v0"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def post_json(url, headers, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_json(url, headers):
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def hog_headers():
    return {
        "X-Access-Key": HOG_ACCESS_KEY,
        "X-Secret-Key": HOG_SECRET_KEY,
        "Content-Type": "application/json",
    }

# ---------------------------------------------------------------------------
# 1. Submit the people search
# ---------------------------------------------------------------------------
def submit_search():
    body = {"query": QUERY, "limit": LIMIT}  # bare/cheap — no enrichment flags
    print(f"-> Submitting search: {QUERY!r} (limit {LIMIT})")
    resp = post_json(f"{HOG_BASE}/api/v1/people/search", hog_headers(), body)
    op_id = resp.get("operationId") or resp.get("id")
    print(f"   operationId: {op_id}")
    return op_id

# ---------------------------------------------------------------------------
# 2. Poll until succeeded
# ---------------------------------------------------------------------------
def poll(op_id, max_tries=30, wait=8):
    url = f"{HOG_BASE}/api/operations/{op_id}"
    for i in range(max_tries):
        resp = get_json(url, hog_headers())
        status = resp.get("status")
        progress = resp.get("progress", 0)
        print(f"   poll {i+1}: status={status} progress={progress}")
        if status in ("succeeded", "completed"):
            return resp.get("result")
        if status in ("failed", "error"):
            raise RuntimeError(f"Operation failed: {resp.get('error')}")
        time.sleep(wait)
    raise TimeoutError("Polling timed out")

# ---------------------------------------------------------------------------
# 3. Write a lead to Airtable
# ---------------------------------------------------------------------------
def write_lead(person):
    fields = {
        "Name": person.get("name", ""),
        "LinkedIn URL": person.get("linkedinUrl", ""),
        "Company": (person.get("company") or {}).get("name", ""),
        "Source Play": SOURCE_PLAY,
        "Signals": [SIGNAL],          # multi-select -> list
    }
    url = f"{AIRTABLE_BASE}/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {"fields": fields, "typecast": True}  # typecast auto-creates select options
    resp = post_json(url, headers, body)
    print(f"   wrote: {fields['Name']} ({fields['Company']})")
    return resp

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    op_id = submit_search()
    result = poll(op_id)
    people = (result or {}).get("data", [])
    print(f"\n<- Got {len(people)} people. Writing to Airtable...\n")
    for person in people:
        try:
            write_lead(person)
        except urllib.error.HTTPError as e:
            print(f"   Airtable error for {person.get('name')}: {e.read().decode()}")
    print("\nDone.")

if __name__ == "__main__":
    main()
