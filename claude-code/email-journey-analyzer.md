# email-journey-analyzer

*Part of [claude-for-sales-professionals](https://github.com/kevinpaolocervantes-commits/claude-for-sales-professionals) — a collection of Claude-powered tooling for sales workflows.*

*Tool repo: [github.com/kevinpaolocervantes-commits/email-journey-analyzer](https://github.com/kevinpaolocervantes-commits/email-journey-analyzer) · Maintainer: Kevin Cervantes*

---

## Why this exists

Every deal we work has the same prep step: pull a prospect's newsletter or journey, eyeball it, and figure out what to pitch. Doing it well takes 1-2 hours per deal — read the emails carefully, evaluate against best practices, map gaps to Marketing Cloud capabilities, frame the rebuild story for an SE handoff or a meeting. Doing it consistently across multiple deals, multiple AEs, and multiple prospect industries is even harder.

This tool runs that prep automatically. Drop a folder of `.eml` files into it, run one command, and get back a structured report with:

1. An ESP-agnostic critique of the prospect's email program (defensible enough that you could show it to them)
2. Every finding tagged with the specific SFMC capability that addresses it
3. A prescriptive "how Salesforce would rebuild this journey" section — phased rollout, expected lift framing, migration considerations from their current ESP

The whole flow takes about two minutes of human time per journey. The report is consistent enough to paste straight into a deal-review doc or hand to an SE.

**What it doesn't do.** It doesn't generate pricing, it doesn't write the actual proposal, and it doesn't replace your judgment on which findings matter for the specific deal. It does the structured, repeatable part so you can spend your time on the parts that aren't repeatable.

**Why it's worth your time to learn it.** The cost is a one-time 10-minute install. The payoff compounds across every deal where the prospect has a visible email program.

---

## What the output looks like

This is a sanitized excerpt from a real run against the **Teddy Baldassarre** newsletter (a watch retail and editorial brand currently on Klaviyo). The full report is 7 sections; this excerpt shows three of them.

### From section 1 — Executive Summary

> Teddy Baldassarre is running two distinct newsletter formats out of a single send stream: a long-form "Weekend Recap" digest (3 of 10 sends, ~200 words, 12 images, 20 links) and short single-topic announcement emails (7 of 10 sends, 73-121 words, 2 images, 4 links). They send from `teddy.b@teddybaldassarre.com` with a reply-able from-address, and run on **Klaviyo** with a branded click-tracking subdomain (`trk.teddybaldassarre.com`) — both signs of an intermediate-to-mature ESP setup. Cadence is irregular (gaps between sends range from 2.3 to 142 hours, with one same-day double-send on June 17 that looks like an editorial mistake). The single highest-leverage opportunity is moving from a blast-to-all model to behavior- and interest-segmented sends.

### From section 3 — Per-email teardown (one of ten)

> **Email 7 — "Your Guide to GMT Watches"**
>
> Sent: 2026-06-17 14:29 UTC (+2.3 hrs after previous email)
> Preheader: "Discover the Ultimate Travel Complication"
> Word count: 73  ·  Images: 2 (1 with alt)  ·  Links: 4  ·  Primary CTAs detected: 0
>
> **Strengths:** Excellent subject + preheader pairing — subject is intriguing-but-vague, preheader gives the concrete topic ("Travel Complication") that pulls the relevant subscriber.
>
> **Weaknesses:** Sent **2 hours and 17 minutes** after the Certina news email. Two emails to the same subscriber within a single sitting is a near-certain frequency-fatigue trigger and disrespects the inbox. For a newsletter program with no behavioral throttling, this is the single most painful finding in the sample.
> → **SFMC:** Einstein Engagement Frequency — automatic per-contact send caps; this kind of double-send would be suppressed for high-frequency-sensitive contacts.

### From section 7 — How Salesforce Would Run This Journey

> **The reimagined program.** The same editorial output, but operated as two orchestrated parent journeys instead of one undifferentiated blast stream. The Weekly Digest journey rebuilt as a per-recipient, send-time-optimized Sunday morning send with dynamic content blocks rendered by signaled brand affinity (the OMEGA collector sees an OMEGA-led recap; the Seiko collector sees a Seiko-led one) and price-tier interest. The Topical News journey rebuilt with subscriber interest profiles gating which topicals reach which subscribers, and Einstein Engagement Frequency caps that make the June 17 double-send structurally impossible.
>
> **The Marketing Cloud stack we'd deploy** (in deployment order):
>
> 1. Audience Builder + Data Extensions — unified subscriber model with brand-affinity and price-tier attributes
> 2. Journey Builder — three parent journeys (Weekly Digest, Topical News, Win-Back)
> 3. Einstein Engagement Frequency — per-contact send caps
> 4. Einstein Send Time Optimization — per-recipient delivery within an editorial window
> 5. Personalization Builder + Content Builder Dynamic Content — brand and price-tier content blocks
> 6. Einstein Copy Insights — subject and preheader variant scoring
> 7. Path Optimizer — multi-variant in-journey testing
> 8. Einstein Recommendations — product-level recs on commerce-tilted sends
>
> **Expected impact framing.** These are typical ranges from Salesforce customers running comparable programs, not guaranteed lifts. Engagement Frequency capping typically reduces unsubscribe rate 10-25% on programs with current frequency-fatigue events. STO typically lifts opens 5-10% versus a single broadcast send time. Dynamic content personalization by behavioral attribute typically lifts click rate 15-30% on content-driven programs. *Aggregate framing for a deal review:* in a comparable D2C content brand on Marketing Cloud, the combination of Engagement Frequency, STO, and behavioral personalization typically moves total email-attributed revenue by 15-30% within two quarters of the foundation phase.

That entire section is the part you paste into your deal-review doc.

---

## Get started (about 10 minutes the first time)

### What you need on your Mac

- **Claude Code** — the CLI that runs the tool. Install from [docs.claude.com/en/docs/claude-code](https://docs.claude.com/en/docs/claude-code) if you don't have it.
- **Python 3.10 or newer** — almost certainly already installed on your Mac. Open Terminal and run `python3 --version` to check.
- **Git** — also almost certainly already installed. `git --version` confirms.

### Install

Open Terminal (Applications → Utilities → Terminal) and run these one at a time:

```bash
cd ~
git clone https://github.com/kevinpaolocervantes-commits/email-journey-analyzer.git
cd email-journey-analyzer
pip install -r parser/requirements.txt
```

That's it. The tool is installed at `~/email-journey-analyzer`.

### Run your first analysis

1. **Get the `.eml` files.** Ask the contact (your rep, an SDR, whoever is on the prospect's list) to forward you the journey emails. Critically, **ask them to use Gmail's "Forward as attachment"** option rather than a regular forward — right-click the message in Gmail and pick "Forward as attachment". This preserves all the original headers and gives you a much higher-quality report. Regular forwards work but lose some deliverability data.

2. **Drop the files into the brand's input folder.** Pick a slug for the brand (e.g., `glossier`, `allbirds`, `teddy-baldassarre`):

   ```bash
   mkdir -p ~/email-journey-analyzer/analyses/glossier/inputs
   ```

   Then drag the `.eml` files into that folder using Finder.

3. **Open Claude Code in the repo and run the analysis:**

   ```bash
   cd ~/email-journey-analyzer
   claude
   ```

   Then in Claude Code, type:

   ```
   /analyze-journey glossier --type welcome_series
   ```

   Valid journey types: `welcome_series`, `abandoned_cart`, `post_purchase`, `browse_abandonment`, `win_back`, `newsletter`.

4. **Read the report** at `~/email-journey-analyzer/analyses/glossier/report.md`. Open it in any text editor, or `cat ~/email-journey-analyzer/analyses/glossier/report.md` in Terminal.

Total runtime per analysis: usually 2-5 minutes.

---

## How we improve this together

The repo is the canonical version. Three files in it are *meant* to evolve based on what we learn in the field:

- `parser/benchmarks.yaml` — journey-type norms (typical email count, cadence, red flags). The values are educated starting guesses. Tune them as you see real journeys in your segments.
- `prompts/sfmc-mapping.md` — gap-to-capability lookup. Add capabilities, refine the messaging, add migration framings for ESPs we displace often.
- `prompts/analysis.md` — the report template itself. Highest-leverage file — small edits here change every future report.

The norm: **if you find something that should be tuned, open a pull request.** Don't fork into a personal version. We get more value if we compound our learnings through one shared repo.

Your actual analyses stay on your own machine — `.gitignore` makes sure `.eml` files, parsed JSON, and reports never get committed to the shared repo. You don't have to be careful; the repo is set up so you can't accidentally leak prospect data.

If you don't know git well enough to open a PR, message Kevin and we'll do it together. After a few rounds, the workflow becomes second nature.

---

## FAQ

**What if my rep already forwarded the emails with a regular forward?** The tool detects Gmail-style forwards and recovers the original sender, subject, date, and preheader from the inner body. You get a slightly degraded report (no deliverability headers, like SPF/DKIM/DMARC), but everything else works. The report will explicitly flag the data quality caveat.

**What if I have screenshots of emails instead of `.eml` files?** Not currently supported — the tool needs the structured email format. Push for `.eml` files from your contact; it's almost always one Gmail menu option away.

**Can I run this on a customer (not a prospect)?** Yes. The tool is journey-agnostic; it doesn't know whether the brand is a prospect or a customer. For customers, you'll most often use it to identify capabilities they're paying for but not using.

**What if the report gets something wrong?** Three options. (1) If it's a one-off, just ignore that section. (2) If it's a recurring problem with a specific type of journey, that's a signal that `parser/benchmarks.yaml` or `prompts/analysis.md` needs tuning — open a PR. (3) If the parser is missing something it should catch (wrong ESP fingerprint, missing personalization detection), open a GitHub issue with the `.eml` file if you can share it.

**What about prospect data privacy?** The tool runs entirely on your local machine. `.eml` files never leave your computer. Claude Code does send the parsed content to Anthropic's models for the analysis pass — review your team's policy on what data is allowed through Claude Code before using on highly regulated industries.

**Who maintains this?** Currently Kevin Cervantes. As adoption grows we'll designate a small group of co-maintainers.

---

## What's next for the tool

Roughly in priority order, based on real usage:

- **Custom branded click-tracking detection.** The fingerprinter currently misses some sends that use a CNAMEd subdomain (e.g., `trk.brand.com` pointing to Klaviyo). Easy fix.
- **A Gmail MCP integration** — pull `.eml` files directly from a shared label instead of the forward-and-upload dance. Bigger lift; worth it if usage volume warrants.
- **Multi-journey analysis** — analyze welcome + cart + post-purchase as a single program rather than three separate reports.
- **Benchmark data from your actual deals.** Right now benchmarks are educated guesses. Once we have 50+ analyses across the team, we can replace heuristics with empirical norms.

Suggestions, requests, and especially "this finding was wrong because…" feedback all go to the GitHub repo as issues, or to Kevin directly.
