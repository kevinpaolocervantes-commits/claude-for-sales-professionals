"""
Account POV Generator

Generates a sales account POV from 3 inputs:
1. Company Name
2. Website URL
3. Product the sales rep is selling

Install:
    pip install -r requirements.txt

Run:
    python claude-code/account-pov-generator.py
"""

import os
import re
import argparse
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


ANTHROPIC_MODEL = "claude-3-5-sonnet-latest"


def clean_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def fetch_website_text(url: str, max_chars: int = 12000) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 AccountPOVGenerator/1.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "svg", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()

    return text[:max_chars]


def build_prompt(company_name: str, website_url: str, product: str, website_text: str) -> str:
    return f"""
You are an elite enterprise sales strategist.

Create a complete account POV for a sales rep selling:

Product:
{product}

Target Account:
{company_name}

Website:
{website_url}

Website Text:
{website_text}

Generate the output in this exact structure:

# {company_name} {product} POV

## 1. Account Summary

### Account Information

#### Strategic Account Snapshot

**Company Overview:**
Write a concise but detailed overview of the company, what they do, their market position, business model, and why they matter.

**Business Model & Personas:**
Explain how the company likely makes money and identify likely customer personas.

**Strategic Priorities:**
Infer the company's likely current-year priorities based on website content, industry context, and business model.

**Recent Initiatives:**
Identify likely recent initiatives based on website signals. Do not invent facts. If uncertain, say "Potential initiative."

### Current Tech Stack

Infer likely technology categories based on the website and business model. Mark anything uncertain as "Unconfirmed."

### External Research Summary

Create 5 strategic insight sections using emojis and clear business language.

Each section should include:
- Insight headline
- Why it matters
- Sales relevance to {product}

## 2. {product} POV

### 1. Why Change?

Explain why the company should consider changing now.

Include:

**External Pressures Demanding Change**
- 3 to 4 bullets

**Internal Constraints Limiting Growth**
- 3 to 4 bullets

### 2. Why {product}?

Create 4 use cases.

For each use case include:

**Use Case Name**
**Strategic Bridge**
**The Solution**
**The Outcome**

The use cases should be specific to {company_name}, not generic.

### 3. Why Now?

Explain why timing matters now.

Include:
- Market timing
- Competitive pressure
- Cost of inaction
- Business impact

## 3. Account Outreach

### Key Contacts & Buying Group

List likely buyer personas by role, not specific names unless they are publicly present in the website text.

For each persona include:
- Role
- Why they care
- Messaging hook

### Cold Call Script

Write a Challenger-style cold call script.

### Voicemail Script

Write a concise voicemail.

### BASHO Emails

Write 4 emails:

1. Outcome-Focused
2. Challenge-Focused
3. Capability-Focused
4. Use Case-Focused

Each email should be concise, executive-level, and relevant to {company_name}.

### Discovery Questions

Write 8 strong discovery questions.

Each question should connect to:
- Business problem
- Cost of inaction
- Strategic priority
- Data/process gap
- Revenue opportunity

### 5-Minute Elevator Pitch

Write a polished 5-minute pitch for {product} tailored to {company_name}.

## 4. Customer-Facing POV Deck Copy

Create slide copy for:

### SLIDE 1: Title Slide
Main Title:
Subtitle:

### SLIDE 3: Priority Alignment
Title:
Vision Statement:
Priority 1:
Priority 2:
Priority 3:

### SLIDE 4: Key Challenges
Title:
Challenge 1:
Challenge 2:
Challenge 3:

### SLIDE 5: Product Vision
Title:
Vision Statement:

### SLIDE 7: Example Use Cases
Use Case 1:
Use Case 2:
Use Case 3:
Use Case 4:

### SLIDE 8: Business Value
Title:
Value Driver 1:
Value Driver 2:
Value Driver 3:

### SLIDE 9: Path Forward
Title:
Why Now:

Important rules:
- Be specific.
- Do not make up fake statistics.
- If data is unknown, use strategic inference and label it clearly.
- Write like a top enterprise account executive.
- Make the POV feel useful enough to bring into account planning.
"""


def call_claude(prompt: str) -> str:
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError("Install Anthropic SDK with: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("Missing ANTHROPIC_API_KEY environment variable.")

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=8000,
        temperature=0.4,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.content[0].text


def save_markdown(company_name: str, content: str) -> str:
    safe_company = re.sub(r"[^a-zA-Z0-9]+", "-", company_name.lower()).strip("-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"{safe_company}-account-pov-{timestamp}.md"

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Generate a sales account POV using Claude.")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--website", required=True, help="Company website URL")
    parser.add_argument("--product", required=True, help="Product being sold")
    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Generate the Claude prompt without calling the API"
    )

    args = parser.parse_args()

    company_name = args.company.strip()
    website_url = clean_url(args.website.strip())
    product = args.product.strip()

    print(f"\nResearching {company_name}...")
    print(f"Website: {website_url}")
    print(f"Product: {product}\n")

    website_text = fetch_website_text(website_url)
    prompt = build_prompt(company_name, website_url, product, website_text)

    if args.prompt_only:
        filepath = save_markdown(company_name, prompt)
        print(f"Prompt saved to: {filepath}")
        return

    try:
        pov = call_claude(prompt)
        filepath = save_markdown(company_name, pov)

        print("\nPOV generated successfully.")
        print(f"Saved to: {filepath}")

    except Exception as error:
        print(f"\nClaude API call failed: {error}")
        print("Saving prompt instead so you can paste it into Claude manually.")

        filepath = save_markdown(company_name, prompt)
        print(f"Prompt saved to: {filepath}")


if __name__ == "__main__":
    main()
