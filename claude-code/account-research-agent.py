"""
Account Research Agent
A practical sales research utility that analyzes a company website and generates
a structured account brief for prospecting, discovery prep, and outreach planning.

Run:
    python scripts/account_research_agent.py

Install:
    pip install requests beautifulsoup4
"""

import re
import textwrap
from collections import Counter
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "you", "your", "are",
    "our", "was", "will", "have", "has", "but", "not", "all", "can", "more",
    "about", "into", "their", "they", "them", "been", "than", "who", "what",
    "when", "where", "why", "how", "its", "it's", "we", "to", "of", "in",
    "on", "a", "an", "is", "as", "by", "or", "at"
}


PAIN_POINT_SIGNALS = {
    "growth": ["scale", "expansion", "growing", "growth", "enterprise"],
    "efficiency": ["automate", "automation", "manual", "efficiency", "productivity"],
    "customer_experience": ["customer", "personalized", "experience", "engagement"],
    "data": ["data", "analytics", "insights", "intelligence", "reporting"],
    "security": ["secure", "security", "compliance", "privacy", "risk"],
    "revenue": ["revenue", "sales", "pipeline", "conversion", "retention"],
}


def normalize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def fetch_site_text(url: str) -> tuple[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 account-research-agent/1.0"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else "No title found"

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()

    return title, text


def extract_keywords(text: str, limit: int = 15) -> list[str]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z\-]{3,}\b", text.lower())
    filtered = [word for word in words if word not in STOPWORDS]

    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(limit)]


def detect_business_signals(text: str) -> dict[str, int]:
    lowered = text.lower()
    signals = {}

    for category, keywords in PAIN_POINT_SIGNALS.items():
        score = sum(lowered.count(keyword) for keyword in keywords)
        if score > 0:
            signals[category] = score

    return dict(sorted(signals.items(), key=lambda item: item[1], reverse=True))


def build_account_brief(company: str, url: str, product: str, title: str, text: str) -> str:
    keywords = extract_keywords(text)
    signals = detect_business_signals(text)

    top_signals = list(signals.keys())[:3] or ["general business improvement"]

    discovery_questions = [
        f"How is {company} currently thinking about improving {signal.replace('_', ' ')}?"
        for signal in top_signals
    ]

    outreach_angles = [
        f"Lead with a point of view around {signal.replace('_', ' ')} and connect it to {product}."
        for signal in top_signals
    ]

    brief = f"""
# Account Research Brief: {company}

## Website
{url}

## Website Title
{title}

## Executive Summary
{company} appears to emphasize themes related to {", ".join(keywords[:5])}. 
Based on the language found on their website, the strongest business signals are:
{", ".join(signal.replace("_", " ") for signal in top_signals)}.

## Keyword Themes
{", ".join(keywords)}

## Detected Business Signals
"""

    for signal, score in signals.items():
        brief += f"- {signal.replace('_', ' ').title()}: {score}\n"

    brief += f"""

## Potential Sales Hypotheses
- {company} may care about improving operational efficiency, customer engagement, or revenue performance.
- Messaging should be tied to visible business priorities rather than generic product features.
- A strong outreach angle should connect {product} to measurable business outcomes.

## Suggested Stakeholders
- Revenue Leader
- Operations Leader
- Marketing Leader
- Customer Experience Leader
- Data / Analytics Leader

## Discovery Questions
"""

    for question in discovery_questions:
        brief += f"- {question}\n"

    brief += "\n## Outreach Angles\n"

    for angle in outreach_angles:
        brief += f"- {angle}\n"

    brief += f"""

## First Email Draft

Subject: Idea for {company}

Hi [Name],

I was looking through {company}'s site and noticed a strong focus around {", ".join(keywords[:3])}.

That made me curious how your team is thinking about {top_signals[0].replace("_", " ")} this year.

I work with teams using {product} to improve visibility, prioritize better actions, and move faster without adding more manual work.

Worth a quick conversation next week?

Best,
[Your Name]

## Notes
This brief is generated from public website text only. Validate assumptions with real research before outreach.
"""

    return textwrap.dedent(brief).strip()


def save_brief(company: str, brief: str) -> str:
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", company.lower()).strip("_")
    filename = f"{safe_name}_account_brief.md"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(brief)

    return filename


def main():
    print("\nAccount Research Agent")
    print("-" * 30)

    company = input("Company name: ").strip()
    website = normalize_url(input("Company website: ").strip())
    product = input("What do you sell?: ").strip()

    print("\nResearching account...\n")

    try:
        title, text = fetch_site_text(website)
        brief = build_account_brief(company, website, product, title, text)
        filename = save_brief(company, brief)

        print(brief)
        print(f"\nSaved brief to: {filename}")

    except requests.RequestException as error:
        print(f"Could not fetch website: {error}")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
