import json
import csv

rows = []

# Open Web Experts
with open("clay_certified_experts.json", "r") as f:
    data = json.load(f)

for p in data["people"]:
    rows.append({
        "Name": p.get("name", ""),
        "Company": p.get("company", ""),
        "Title": p.get("role", ""),
        "LinkedIn URL": p.get("linkedin_url", ""),
        "Signals": "Clay Certified Expert",
        "Source Play": "Open Web Experts",
        "Source": "Deep Research",
        "Evidence": p.get("evidence", "")
    })

# Pain Miner
with open("pain_miner_v2.json", "r") as f:
    data = json.load(f)

for p in data["people"]:
    rows.append({
        "Name": p.get("name", ""),
        "Company": p.get("company", ""),
        "Title": p.get("role", ""),
        "LinkedIn URL": p.get("linkedin_url", ""),
        "Signals": "Pain Signal",
        "Source Play": "Pain Miner",
        "Source": "Deep Research",
        "Evidence": p.get("evidence", "")
    })

with open("signals_import.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "Name",
            "Company",
            "Title",
            "LinkedIn URL",
            "Signals",
            "Source Play",
            "Source",
            "Evidence"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print(f"Created signals_import.csv with {len(rows)} rows")
