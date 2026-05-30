#!/usr/bin/env python3
"""
Automated blog post generator using Groq API.
Picks next keyword from strategy, generates SEO-optimized article, injects affiliate links, commits to _posts/.
"""

import os
import json
import re
import sys
from datetime import datetime
from groq import Groq

STRATEGY_FILE = "scripts/niche_strategy.json"
AFFILIATE_FILE = "scripts/affiliate_links.json"
POSTS_DIR = "_posts"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def pick_keyword(strategy):
    pending = strategy.get("pending_keywords", [])
    if not pending:
        print("No pending keywords. Run update_strategy.py to generate more.", file=sys.stderr)
        sys.exit(1)
    return pending[0]

def build_prompt(keyword, affiliates, strategy):
    active_affiliates = [
        f"- {v['name']}: {v['description']} (CTA: \"{v['cta']}\")"
        for v in affiliates.values()
        if isinstance(v, dict) and v.get("active")
    ]
    affiliate_list = "\n".join(active_affiliates[:4])

    # Detect comparison/vs articles to conditionally inject the head-to-head table section
    is_comparison = any(
        marker in keyword.lower()
        for marker in [" vs ", " vs. ", " versus ", " comparison", " compare", " alternative"]
    )
    comparison_table_section = (
        "\n## Head-to-Head Comparison\n"
        "\n"
        "| Feature | [Tool A] | [Tool B] |\n"
        "|---------|----------|----------|\n"
        "[4-6 rows covering key differentiators: price, output quality, ease of use, integrations, support]\n"
        "\n"
        "[One paragraph below the table summarising who wins which category and why]\n"
        if is_comparison else ""
    )

    return f"""You are an expert tech blogger writing for SmartAI Picks, an honest AI tools review site.

Write a comprehensive, SEO-optimized blog post targeting this keyword: "{keyword}"

TONE: {strategy.get("content_tone", "honest, practical, no hype")}
TARGET LENGTH: {strategy.get("avg_article_length", 1500)} words

STRUCTURE (use this exact format):
---
title: "[Compelling title with keyword]"
description: "[150-160 char meta description with keyword]"
date: {datetime.now().strftime("%Y-%m-%d")}
keywords: [keyword1, keyword2, keyword3, keyword4, keyword5]
featured_tool: "[main tool being reviewed]"
---

# [Same title as above]

[Intro — use the PAS formula in this exact order:
  PROBLEM (1-2 sentences): Name the specific pain the reader is experiencing right now.
  AGITATION (2-3 sentences): Twist the knife — explain why this problem is costly, time-wasting, or getting worse without a fix.
  SOLUTION (1-2 sentences): Position this article as the clear answer that resolves their problem.
  Total intro length: 100-150 words.]

<div class="key-takeaways">

**Key Takeaways**
- [Most important finding or bottom-line recommendation — one punchy sentence]
- [Second key insight — concrete and actionable for the reader]
- [Third key insight — who this is best for and who should look elsewhere]

</div>

## What Is [Tool/Topic]?
[Clear explanation, 150-200 words]

## Key Features Worth Knowing
[3-5 features with H3 subheadings, each 80-100 words]

## Pricing Breakdown

| Plan | Price | Best For |
|------|-------|----------|
[2-4 rows]

{comparison_table_section}## Pros and Cons
**Pros:**
- [3-5 specific pros]

**Cons:**
- [2-4 honest cons, don't be a shill]

## Who Should Use This?
[2-3 paragraphs describing ideal users and use cases]

## [Tool] vs. Alternatives
[Compare 2-3 alternatives honestly, 200 words]

## Our Verdict
[Honest conclusion, 150 words. Include affiliate CTA using placeholder: [AFFILIATE_CTA:tool_key]]

## Frequently Asked Questions

**Q: [Most-searched question about this keyword — match "People Also Ask" intent]**
A: [Direct, self-contained answer in 40-60 words]

**Q: [Second common question — focus on pricing or free tier availability]**
A: [Direct, self-contained answer in 40-60 words]

**Q: [Third common question — focus on a specific use case or known limitation]**
A: [Direct, self-contained answer in 40-60 words]

**Q: [Fourth common question — comparison or best alternative angle]**
A: [Direct, self-contained answer in 40-60 words]

**Q: [Fifth common question — beginner or getting-started angle]**
A: [Direct, self-contained answer in 40-60 words]

---

AVAILABLE AFFILIATE TOOLS TO MENTION NATURALLY (use [AFFILIATE_CTA:tool_key] for CTA placement):
{affiliate_list}

Tool keys: jasper, writesonic, copy_ai, grammarly, surfer_seo, canva, notion, rytr

CRITICAL RULES:
- Be honest — negative points build trust and convert better than fake praise
- Place max 2 affiliate CTAs per article using ONLY the [AFFILIATE_CTA:key] placeholder — NEVER write raw URLs
- Don't fabricate specific pricing — use approximate ranges or "check current pricing"
- Write in US English
- Tables MUST use proper GFM markdown with header separator row: | Col | Col |\n|-----|-----|\n| val | val |
- Leave one blank line before and after every table
- Do NOT include any URLs in the article text — only use [AFFILIATE_CTA:key] placeholders
- The <div class="key-takeaways"> block MUST appear immediately after the intro, before the first H2
- The FAQ section MUST be the last section before the closing ---
- Each FAQ answer must be a self-contained sentence (Google uses these for featured snippets)
"""

def generate_article(client, keyword, affiliates, strategy):
    prompt = build_prompt(keyword, affiliates, strategy)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.75,
            max_tokens=3500,
        )
    except Exception as e:
        print(f"Error: Groq API call failed: {e}", file=sys.stderr)
        sys.exit(1)
    return response.choices[0].message.content

def inject_affiliate_links(content, affiliates):
    """Replace [AFFILIATE_CTA:key] placeholders with HTML affiliate links."""
    def replace_cta(match):
        key = match.group(1).strip()
        tool = affiliates.get(key)
        if not tool or not tool.get("active"):
            return ""
        url = tool["url"]
        cta = tool["cta"]
        name = tool["name"]
        return (
            f'\n<div class="affiliate-cta">'
            f'<a href="{url}" target="_blank" rel="noopener nofollow sponsored" class="cta-button">'
            f'{cta}</a>'
            f'<span class="disclaimer">Affiliate link — we earn a commission at no extra cost to you.</span>'
            f'</div>\n'
        )
    return re.sub(r'\[AFFILIATE_CTA:([^\]]+)\]', replace_cta, content)

def keyword_to_slug(keyword):
    slug = keyword.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug[:60]

def save_post(content, keyword):
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = keyword_to_slug(keyword)
    filename = f"{POSTS_DIR}/{date_str}-{slug}.md"
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {filename}")
    return filename

def update_strategy(strategy, used_keyword):
    strategy["pending_keywords"] = [k for k in strategy["pending_keywords"] if k != used_keyword]
    strategy["used_keywords"].append(used_keyword)
    strategy["performance_data"][used_keyword] = {
        "published": datetime.now().strftime("%Y-%m-%d"),
        "clicks": 0,
        "conversions": 0,
    }
    save_json(STRATEGY_FILE, strategy)
    print(f"Strategy updated. {len(strategy['pending_keywords'])} keywords remaining.")

def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    strategy = load_json(STRATEGY_FILE)
    affiliates = load_json(AFFILIATE_FILE)
    client = Groq(api_key=api_key)

    keyword = pick_keyword(strategy)
    print(f"Generating post for: {keyword}")

    content = generate_article(client, keyword, affiliates, strategy)
    content = inject_affiliate_links(content, affiliates)

    save_post(content, keyword)
    update_strategy(strategy, keyword)
    print("Done.")

if __name__ == "__main__":
    main()
