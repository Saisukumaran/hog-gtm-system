#!/usr/bin/env python3
"""
Lead Scoring + Tiering pass over Airtable.
Reads all Leads, groups by LinkedIn URL (so the same person across multiple
plays is merged), scores by signal type + a stacking bonus for multi-play
overlap, then writes Score and Tier back to each record.

Philosophy: ranking here is to TRIAGE, not to discard. Every intent-based
lead stays on the list. The score orders them; signal-stacking surfaces the
hottest. At larger volume this same engine triages thousands.
"""
import os, json, urllib.request, urllib.error, urllib.parse
from collections import defaultdict

# ---- CREDENTIALS ----
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN", "pat_REPLACE_ME")
AIRTABLE_BASE_ID = "appDRIUIwdsXdJUj7"
AIRTABLE_TABLE = "Leads"
AIRTABLE_BASE = "https://api.airtable.com/v0"

# ---- SIGNAL WEIGHTS (by Source Play) ----
PLAY_WEIGHTS = {
    "Pain Miner": 30,          # named a problem = hottest intent
    "Open Web Experts": 25,    # Clay-certified, lives the multi-tool pain
    "Builders": 20,            # hands-on, publicly engaged
    "Builders (Hog)": 20,      # same signal, Hog-sourced
    "Direct ICP": 20,          # is the user
    "Hiring": 15,              # org-level intent
}
STACK_BONUS = 15               # per ADDITIONAL play a person appears in

def at_headers():
    return {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}

def get_all_records():
    """Page through every record in the table."""
    records = []
    offset = None
    while True:
        params = {"pageSize": 100}
        if offset:
            params["offset"] = offset
        url = f"{AIRTABLE_BASE}/{AIRTABLE_BASE_ID}/{urllib.parse.quote(AIRTABLE_TABLE)}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers=at_headers(), method="GET")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records

def normalize_url(u):
    if not u:
        return ""
    return u.strip().rstrip("/").split("?")[0].lower()

def score_group(plays):
    """plays = set of distinct Source Play values for one person."""
    base = sum(PLAY_WEIGHTS.get(p, 10) for p in plays)
    extra = STACK_BONUS * max(0, len(plays) - 1)
    return base + extra

def tier_for(plays, score):
    multi = len(plays) >= 2
    has_pain = "Pain Miner" in plays
    if multi or has_pain:
        return "Tier 1"
    return "Tier 2"

def update_record(rec_id, score, tier):
    url = f"{AIRTABLE_BASE}/{AIRTABLE_BASE_ID}/{urllib.parse.quote(AIRTABLE_TABLE)}/{rec_id}"
    body = {"fields": {"Score": score, "Tier": tier}, "typecast": True}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=at_headers(), method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    records = get_all_records()
    print(f"Read {len(records)} records.\n")

    # Group records by normalized LinkedIn URL
    by_person = defaultdict(list)      # url -> list of records
    plays_by_person = defaultdict(set) # url -> set of Source Play
    for r in records:
        f = r.get("fields", {})
        url = normalize_url(f.get("LinkedIn URL", ""))
        if not url:
            url = f"__nourl__{r['id']}"   # treat blank-URL rows as unique
        by_person[url].append(r)
        play = f.get("Source Play")
        if play:
            plays_by_person[url].add(play)

    print(f"{len(by_person)} unique people after merging by LinkedIn URL.\n")

    # Score + tier, write back to ALL records for that person
    tier1 = tier2 = 0
    multi_play = []
    for url, recs in by_person.items():
        plays = plays_by_person[url]
        score = score_group(plays)
        tier = tier_for(plays, score)
        if tier == "Tier 1":
            tier1 += 1
        else:
            tier2 += 1
        if len(plays) >= 2:
            name = recs[0].get("fields", {}).get("Name", "?")
            multi_play.append((name, sorted(plays), score))
        for r in recs:
            try:
                update_record(r["id"], score, tier)
            except urllib.error.HTTPError as e:
                print(f"  update error {r['id']}: {e.read().decode()}")

    print(f"Done. Tier 1: {tier1}  |  Tier 2: {tier2}\n")
    if multi_play:
        print("MULTI-SIGNAL LEADS (appear in 2+ plays, your hottest):")
        for name, plays, score in sorted(multi_play, key=lambda x: -x[2]):
            print(f"  {score}  {name}  <- {', '.join(plays)}")
    else:
        print("No multi-play overlap yet (expected with small/non-overlapping runs).")

if __name__ == "__main__":
    main()
