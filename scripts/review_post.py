#!/usr/bin/env python3
"""
Post-generation review pass using Groq API.
Finds the most recently modified post in _posts/, sends it for a targeted
quality review, and overwrites it with the improved version.

Focused checks:
- Year references match current year
- Pricing claims are appropriately hedged (no stale specific numbers)
- Hook/intro is engaging, not generic
- Meta description is 150-160 chars
- CTAs are placed at high-intent moments (after Pricing + in Verdict)
- FAQ answers are self-contained sentences
"""

import os
import sys
import glob
from datetime import datetime
from groq import Groq

POSTS_DIR = "_posts"


def find_latest_post():
    posts = glob.glob(f"{POSTS_DIR}/*.md")
    if not posts:
        print("No posts found in _posts/", file=sys.stderr)
        sys.exit(1)
    return max(posts, key=os.path.getmtime)


def build_review_prompt(content, current_year):
    return f"""You are a senior editor reviewing an AI-tools affiliate blog post for SmartAI Picks. Your job is to make targeted, high-value improvements — NOT a full rewrite.

CURRENT YEAR: {current_year}

Apply ONLY the following fixes (skip any that don't apply):

1. YEAR REFERENCES — Replace any wrong year references (e.g. "{current_year - 1}" in titles, headings, body) with "{current_year}". The filename slug does not need changing.

2. PRICING CLAIMS — If the article states specific dollar prices without hedging language, add "approximately" or "check current pricing" as appropriate. Do NOT invent prices. Legitimate hedges look like: "starting at around $X/month (check current pricing)" or "from ~$X/month".

3. HOOK — If the opening paragraph starts with a generic problem statement or "Many [people] struggle with...", rewrite only the first paragraph to open with a compelling hook: a surprising stat, a bold claim, or a direct question. Keep it under 80 words. Do not touch the rest of the intro.

4. META DESCRIPTION — If the `description:` frontmatter field is under 140 or over 165 characters, rewrite it to land between 150-160 characters while keeping the primary keyword.

5. CTA PLACEMENT — The article should have exactly 2-3 affiliate CTAs (`<div class="affiliate-cta">` blocks). If there is only 1, add a second one immediately after the Pricing section (before the next H2). Do not add more than 3 total. Do not change existing CTA HTML, only add if missing.

6. FAQ ANSWERS — Each FAQ answer must be a self-contained sentence that makes sense without reading the question. If any answer starts with "Yes," "No," or "It depends" followed by a vague clause, complete it with the specific tool name and detail.

OUTPUT: Return the complete improved article, starting with `---` (the YAML frontmatter). No explanations, no preamble — just the full article content.

ARTICLE TO REVIEW:
---
{content}"""


def review_post(client, content, current_year):
    prompt = build_review_prompt(content, current_year)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
    except Exception as e:
        print(f"Error: Groq review call failed: {e}", file=sys.stderr)
        sys.exit(1)
    return response.choices[0].message.content


def extract_article(raw):
    """Strip any preamble before the opening --- of the frontmatter."""
    idx = raw.find("---")
    if idx == -1:
        return raw
    return raw[idx:]


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    post_path = find_latest_post()
    print(f"Reviewing: {post_path}")

    with open(post_path, "r", encoding="utf-8") as f:
        original = f.read()

    client = Groq(api_key=api_key)
    current_year = datetime.now().year

    reviewed = review_post(client, original, current_year)
    reviewed = extract_article(reviewed)

    with open(post_path, "w", encoding="utf-8") as f:
        f.write(reviewed)

    print(f"Review complete. Post updated: {post_path}")


if __name__ == "__main__":
    main()
