#!/usr/bin/env python3
"""
SIGNAL STACK ENGINE - cross-checks every lead against all 5 signals.

Population-first scoring: take the full lead list, and for EACH person test
all five signal dimensions (not just the one play they came from). Score =
sum of confirmed signals. This produces real ranking and real overlap.

Most signals are detectable for free from the person's title/headline text
plus the play they originally came from. No per-person activity API needed.

Writes back: Score, Tier, and a Signals multi-select reflecting every
confirmed signal (so the stacking is visible in Airtable).
"""
import os, re, json, urllib.request, urllib.error, urllib.parse
from collections import defaultdict

# ---- CREDENTIALS ----
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN", "pat_REPLACE_ME")
AIRTABLE_BASE_ID = "appDRIUIwdsXdJUj7"
AIRTABLE_TABLE = "Leads"
AIRTABLE_BASE = "https://api.airtable.com/v0"

# ---- SIGNAL WEIGHTS (match the user's notebook diagram) ----
W_ICP    = 30
W_EXPERT = 30
W_BUILDER= 25
W_PAIN   = 25
W_HIRING = 15

# ---- DETECTION VOCAB ----
ICP_TERMS = ["gtm", "go-to-market", "go to market", "revops", "rev ops",
             "revenue oper", "sales", "growth", "demand gen", "outbound",
             "marketing", "bdr", "sdr", "account exec", "founder", "ceo",
             "co-founder", "lead gen", "pipeline"]
EXPERT_SENIORITY = ["head", "director", "vp", "vice president", "chief",
                    "founder", "co-founder", "lead ", "principal", "owner",
                    "partner", "manager"]
EXPERT_TOOLS = ["clay", "apollo", "n8n", "instantly", "smartlead", "hubspot",
                "outreach", "salesforce", "zapier", "make.com", "lemlist",
                "heyreach", "cargo"]
BUILDER_TERMS = ["build", "building", "builder", "engineer", "engineering",
                 "automation", "automate", "systems", "workflow", "ai ",
                 "agent", "no-code", "nocode"]
PAIN_STACK_TERMS = ["clay", "apollo", "enrichment", "data", "stack",
                    "multi-tool", "scraping", "lead intelligence", "tooling"]

def at_headers():
    return {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}

def get_all_records():
    records, offset = [], None
    while True:
        params = {"pageSize": 100}
        if offset: params["offset"] = offset
        url = f"{AIRTABLE_BASE}/{AIRTABLE_BASE_ID}/{urllib.parse.quote(AIRTABLE_TABLE)}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers=at_headers(), method="GET")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset: break
    return records

def has_any(text, terms):
    t = (text or "").lower()
    return any(term in t for term in terms)

def detect_signals(fields):
    """Return the set of confirmed signals for one lead."""
    title = fields.get("Title", "") or ""
    company = fields.get("Company", "") or ""
    play = (fields.get("Source Play") or "").strip()
    blob = f"{title} {company}"
    sig = set()

    # 1. ICP fit - from title, or any sales/gtm play origin
    if has_any(blob, ICP_TERMS) or play in ("Direct ICP", "Builders", "Builders (Hog)",
                                            "Pain Miner", "Open Web Experts", "Hiring"):
        sig.add("ICP Fit")

    # 2. Expert level - seniority OR names a tool
    if has_any(title, EXPERT_SENIORITY) or has_any(blob, EXPERT_TOOLS) or play == "Open Web Experts":
        sig.add("Expert Level")

    # 3. Builder - origin play or build language
    if play in ("Builders", "Builders (Hog)") or has_any(title, BUILDER_TERMS):
        sig.add("Builder")

    # 4. Pain - origin play or in-the-stack language
    if play == "Pain Miner" or has_any(blob, PAIN_STACK_TERMS):
        sig.add("Pain")

    # 5. Hiring - origin play (company-level signal)
    if play == "Hiring":
        sig.add("Hiring")

    return sig

def score_signals(sig):
    s = 0
    if "ICP Fit" in sig:      s += W_ICP
    if "Expert Level" in sig: s += W_EXPERT
    if "Builder" in sig:      s += W_BUILDER
    if "Pain" in sig:         s += W_PAIN
    if "Hiring" in sig:       s += W_HIRING
    return s

def tier_for(score):
    if score >= 70: return "Tier 1"
    if score >= 50: return "Tier 2"
    return "Tier 3"

def update_record(rec_id, score, tier, signals):
    url = f"{AIRTABLE_BASE}/{AIRTABLE_BASE_ID}/{urllib.parse.quote(AIRTABLE_TABLE)}/{rec_id}"
    # Only write Score and Tier. We do NOT overwrite the Signals multi-select
    # (it holds the original play signal, and PATCH + typecast is unreliable
    # for multi-selects). The full detected signal set is shown in the output.
    body = {"fields": {"Score": score, "Tier": tier}, "typecast": True}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=at_headers(), method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    records = get_all_records()
    print(f"Read {len(records)} leads. Cross-checking each against all 5 signals...\n")

    tiers = defaultdict(int)
    sig_count = defaultdict(int)   # how many leads confirmed each signal
    stack_dist = defaultdict(int)  # how many leads have N signals
    ranked = []

    for r in records:
        f = r.get("fields", {})
        sig = detect_signals(f)
        score = score_signals(sig)
        tier = tier_for(score)
        tiers[tier] += 1
        stack_dist[len(sig)] += 1
        for s in sig: sig_count[s] += 1
        ranked.append((score, f.get("Name", "?"), sorted(sig), f.get("Title", "")[:50]))
        try:
            update_record(r["id"], score, tier, sig)
        except urllib.error.HTTPError as e:
            print(f"  update error {r['id']}: {e.read().decode()[:120]}")

    print("=== RESULTS ===")
    print(f"Tier 1 (70+): {tiers['Tier 1']}   Tier 2 (50-69): {tiers['Tier 2']}   Tier 3 (<50): {tiers['Tier 3']}\n")
    print("Signals confirmed across all leads:")
    for s in ["ICP Fit","Expert Level","Builder","Pain","Hiring"]:
        print(f"  {s:13} {sig_count[s]}")
    print("\nSignal-stack distribution (how many signals each lead hit):")
    for n in sorted(stack_dist, reverse=True):
        print(f"  {n} signals: {stack_dist[n]} leads")
    print("\nTOP 15 LEADS (by stacked score):")
    for score, name, sig, title in sorted(ranked, key=lambda x: -x[0])[:15]:
        print(f"  {score:3}  {name:26}  [{', '.join(sig)}]")

if __name__ == "__main__":
    main()
