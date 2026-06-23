# The Hog · GTM Engineering Assignment

A signal-driven prospecting engine built on The Hog's API.

**Core hypothesis:** The Hog is most valuable as a signal engine rather than a traditional contact database.

The objective was to identify high-intent prospects through multiple acquisition plays, normalize them into one unified lead database, score them across every signal, and prepare the top tier for enrichment and outbound.

Full narrative, architecture, and benchmark walkthrough live on the accompanying project site.

---

## Acquisition plays

Five plays, each a different intent signal feeding one shared pipeline. All ran on The Hog's API and wrote real leads to Airtable.

These plays intentionally target different dimensions of intent: identity, expertise, engagement, organizational demand, and pain.

| Play             | Signal type          | Method                         | Output       |
| ---------------- | -------------------- | ------------------------------ | ------------ |
| Direct ICP       | Person is the user   | People Search                  | 2 prospects  |
| Hiring           | Account-level intent | Web scrape + company search    | 9 companies  |
| Builders         | Person engagement    | LinkedIn post-comments scraper | 59 builders  |
| Pain Miner       | Person pain          | Deep Research                  | 24 prospects |
| Open Web Experts | Identity / expertise | Deep Research                  | 27 experts   |

**Total: 112 records.**

* **Direct ICP** identifies people who already are GTM engineers / RevOps via People Search.
* **Hiring** finds companies actively hiring GTM roles (organizational intent).
* **Builders** scrapes commenters on GTM / AI build posts via The Hog's LinkedIn post-comments endpoint.
* **Pain Miner** uses Deep Research to surface operators publicly discussing frustration with prospecting, enrichment, data quality, and tooling cost.
* **Open Web Experts** uses Deep Research to find Clay-certified experts, solutions partners, and recognized GTM tooling specialists.

---

## The signal-stack scoring engine

Raw leads are not the deliverable. Every lead is cross-checked against all five signals (not just the one it arrived on), and scored by the sum of confirmed signals. Leads that confirm on multiple axes rise to the top.

Weights:

* ICP Fit = 30
* Expert = 30
* Builder = 25
* Pain = 25
* Hiring = 15

Tier 1 = 70+

Result on the 112 leads:

* Tier 1 (70+): **35**
* Tier 2 (50-69): **71**
* Below 50: **6**

Of the 35 Tier 1 leads, **6 matched four independent signals**, making them the strongest prospects in the database.

Detection is keyword-based on profile text plus origin play: a defensible proxy, not ground truth. A production version would verify pain and builder signals from real post activity per person.

---

## Hog vs Apollo benchmark

Top leads enriched on The Hog, then looked up on Apollo. Neither dominates; the failure modes differ.

* **Accuracy:** both correct on one lead; The Hog caught a false-company inference Apollo made (a lead Apollo placed at Clay is actually an independent freelancer); Apollo found one email The Hog returned null.
* **Cost:** The Hog ~$1.62 per email found (14,956 credits / 6 emails, charged for nulls). Apollo ~$0.20 per email. Apollo was roughly 8x cheaper on enrichment in this test.
* **Takeaway:** The Hog's strongest differentiation appears to be sourced discovery and signal generation. Enrichment is best positioned as a selective workflow applied after lead qualification.

A second comparison (Apify vs The Hog) on the Builders scrape:

The Hog's native LinkedIn endpoint replaced a third-party scraper I had wired in, proving the consolidation thesis. Apify returned richer structured company fields; The Hog returned headline-only.

---

## What surprised me

* Open Web Experts produced the highest signal-to-noise ratio.
* Pain Miner generated fewer leads than expected but significantly higher intent.
* Discovery costs were predictable while enrichment costs varied materially.
* Deep Research was more effective for expert discovery than I initially expected.
* Builders produced the largest volume of prospects while maintaining relevance.

---

## Key findings

* Found an undocumented LinkedIn post-comments endpoint by testing (not in public docs). It unlocked three social plays natively.
* Enrichment cost is uncapped and charges for null results. One call required 2,736 credits with no ceiling; a 6-email batch consumed ~15,000 credits.
* Discovery is cheap and predictable (~42 credits per lead; the full campaign ran under 4,700 credits) while enrichment is ~18x more expensive. This drove the discover-cheap / score-free / enrich-winners-only architecture.
* Search latency scales with title rarity: "GTM Engineer" queries stalled for minutes while common titles returned in seconds. Discovery should run as an asynchronous background process.
* Deep Research performed strongly for intent and expert discovery (Pain Miner and Open Web Experts).
* Signal-based prospecting produced more relevant prospects than title-based prospecting, supporting the positioning of The Hog as a signal engine rather than a contact database.

---

## Architecture

```text
Signal Sources (5 Plays)
          ↓
    Lead Database
      (Airtable)
          ↓
     Deduplication
          ↓
 Signal-Stack Scoring
   (Free Qualification)
          ↓
      Enrichment
   (Tier 1 Only)
          ↓
       Outbound
```

---

## Repository structure

/scripts
    Python source code for acquisition, scoring, and CSV merging


/workflows
    Shell workflows, n8n exports, and play documentation


/research
    Raw Deep Research outputs
    (Pain Miner, Open Web Experts)


/data
    Lead datasets and supporting CSVs


/poll
    Async operation polling helper


/screenshots
    Airtable lead view, n8n canvases,
    scoring output, research results,
    and Hog usage dashboard

    - 01_airtable_leads.png
    - 02_signal_scoring_output.png
    - 03_pain_miner_results.png
    - 04_builders_workflow.png
    - 05_hog_api_usage.png

## Setup

1. Clone the repo
2. Copy the env file and add your keys
   cp env.example .env
3. Make the poll script executable
   chmod +x poll/poll_operation.sh
   
API keys and tokens are loaded through environment variables. No credentials are committed to the repository.

---

## Future improvements

If extended further, I would focus on:

* Real-time signal monitoring
* Automated signal verification
* Continuous lead scoring
* Champion identification inside hiring accounts
* Routing enriched prospects directly into outbound sequences

---

## Submission

Full submission, architecture diagram, benchmark exhibit, workflow walkthroughs, and outbound examples live on the accompanying project website.
