"""
Account POV Generator — no dependencies required (Python stdlib only)

Run interactively:
    python3 account-pov-generator.py

Run with arguments:
    python3 account-pov-generator.py --company "Acme" --website acme.com --product "Agentforce" --api-key sk-ant-...
"""

import os, re, json, ssl, argparse, urllib.request
from datetime import datetime
from html.parser import HTMLParser

ANTHROPIC_MODEL = "claude-sonnet-4-6"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


# ── HTML → plain text ────────────────────────────────────────────────────────

class _TextExtractor(HTMLParser):
    SKIP = {"script", "style", "nav", "footer", "svg", "noscript", "head"}

    def __init__(self):
        super().__init__()
        self._depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._depth:
            self._depth -= 1

    def handle_data(self, data):
        if not self._depth:
            self.parts.append(data)


def _html_to_text(html: str) -> str:
    p = _TextExtractor()
    p.feed(html)
    return re.sub(r"\s+", " ", " ".join(p.parts)).strip()


# ── Network ──────────────────────────────────────────────────────────────────

def fetch_website_text(url: str, max_chars: int = 12000) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=15) as r:
            charset = r.headers.get_content_charset() or "utf-8"
            return _html_to_text(r.read().decode(charset, errors="replace"))[:max_chars]
    except Exception:
        return ""


def call_api(api_key: str, prompt: str) -> str:
    body = json.dumps({
        "model": ANTHROPIC_MODEL,
        "max_tokens": 8000,
        "temperature": 0.4,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        ANTHROPIC_API_URL, data=body, method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=120) as r:
        return json.loads(r.read())["content"][0]["text"]


# ── Prompt ───────────────────────────────────────────────────────────────────

def build_prompt(company: str, url: str, product: str, website_text: str) -> str:
    context = website_text or "(Website unavailable — use your training knowledge about this company.)"
    return f"""You are an elite enterprise sales strategist.

Create a complete account POV for a sales rep selling {product} to {company} ({url}).

Website text:
{context}

Generate the output in this exact structure:

# {company} {product} POV

## 1. Account Summary

### Account Information

#### Strategic Account Snapshot

**Company Overview:**
**Business Model & Personas:**
**Strategic Priorities:**
**Recent Initiatives:** (label uncertain items as "Potential initiative.")

### Current Tech Stack
Infer likely categories. Mark uncertain items as "Unconfirmed."

### External Research Summary
5 insight sections with emojis. Each: headline, why it matters, sales relevance to {product}.

## 2. {product} POV

### 1. Why Change?
**External Pressures Demanding Change** — 3-4 bullets
**Internal Constraints Limiting Growth** — 3-4 bullets

### 2. Why {product}?
4 use cases specific to {company}. Each: Use Case Name, Strategic Bridge, The Solution, The Outcome.

### 3. Why Now?
Cover: market timing, competitive pressure, cost of inaction, business impact.

## 3. Account Outreach

### Key Contacts & Buying Group
Likely personas by role (not names unless public). Each: Role, Why they care, Messaging hook.

### Cold Call Script
Challenger-style.

### Voicemail Script
Concise.

### BASHO Emails
4 emails: Outcome-Focused, Challenge-Focused, Capability-Focused, Use Case-Focused.
Each: concise, executive-level, specific to {company}.

### Discovery Questions
8 questions connecting to: business problem, cost of inaction, strategic priority, data/process gap, revenue opportunity.

### 5-Minute Elevator Pitch
Polished pitch for {product} tailored to {company}.

## 4. Customer-Facing POV Deck Copy

### SLIDE 1: Title Slide
Main Title:
Subtitle:

### SLIDE 3: Priority Alignment
Title:
Vision Statement:
Priority 1 / 2 / 3:

### SLIDE 4: Key Challenges
Title:
Challenge 1 / 2 / 3:

### SLIDE 5: Product Vision
Title:
Vision Statement:

### SLIDE 7: Example Use Cases
Use Case 1 / 2 / 3 / 4:

### SLIDE 8: Business Value
Title:
Value Driver 1 / 2 / 3:

### SLIDE 9: Path Forward
Title:
Why Now:

Rules: be specific, no invented statistics, label inferences clearly, write like a top AE."""


# ── Output ───────────────────────────────────────────────────────────────────

def save(company: str, content: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
    path = os.path.join("outputs", f"{slug}-pov-{datetime.now().strftime('%Y%m%d-%H%M')}.md")
    os.makedirs("outputs", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company")
    parser.add_argument("--website")
    parser.add_argument("--product")
    parser.add_argument("--api-key")
    args = parser.parse_args()

    # Fill in anything not passed as an arg interactively
    company = args.company or input("Company name: ").strip()
    website = args.website or input("Website URL: ").strip()
    product = args.product or input("Product being sold: ").strip()
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY") or input("Anthropic API key: ").strip()

    url = website if website.startswith("http") else "https://" + website.rstrip("/")

    print(f"\nGenerating POV for {company}...")

    website_text = fetch_website_text(url)
    if not website_text:
        print("(Website unreachable — Claude will use training knowledge.)")

    pov = call_api(api_key, build_prompt(company, url, product, website_text))
    path = save(company, pov)

    print(f"Done. Saved to: {path}\n")


if __name__ == "__main__":
    main()
