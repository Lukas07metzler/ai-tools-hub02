#!/usr/bin/env python3
"""
Weekly strategy improvement agent.
Asks Groq to research new trending AI tool keywords and refresh the keyword list.
Runs every Sunday via GitHub Actions.
"""

import os
import json
import sys
from datetime import datetime
from groq import Groq

STRATEGY_FILE = "scripts/niche_strategy.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_new_keywords(client, strategy):
    used = strategy.get("used_keywords", [])
    pending = strategy.get("pending_keywords", [])
    all_known = set(used + pending)

    prompt = f"""You are an SEO strategist for an AI tools review blog called SmartAI Picks.

The blog targets: people searching for honest AI tool reviews, comparisons, and "best X" lists.
Affiliate focus: writing tools, productivity AI, SEO tools (Jasper, Writesonic, Grammarly, Surfer SEO, etc.)

Already covered topics (do NOT repeat):
{json.dumps(list(all_known)[:30], indent=2)}

Today's date: {datetime.now().strftime("%Y-%m-%d")}

Your task: Generate 20 fresh, high-intent blog post keywords/topics that:
1. Have clear search intent (review, comparison, "best X")
2. Are relevant to AI tools released or updated in the last 6 months
3. Haven't been covered above
4. Would naturally lead to affiliate link clicks

Return ONLY a JSON array of strings, no explanation. Example format:
["keyword one", "keyword two", ...]
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=800,
        )
    except Exception as e:
        print(f"Error: Groq API call failed while generating keywords: {e}", file=sys.stderr)
        sys.exit(1)

    raw = response.choices[0].message.content.strip()

    # Extract JSON array from response
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        print("Could not parse keyword list from response:", raw, file=sys.stderr)
        return []

    try:
        keywords = json.loads(raw[start:end])
        return [k for k in keywords if k not in all_known]
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        return []

def analyze_and_recommend(client, strategy):
    """Ask AI to analyze performance data and suggest strategy adjustments."""
    perf = strategy.get("performance_data", {})
    if len(perf) < 5:
        return None  # Not enough data yet

    prompt = f"""You are an SEO analyst reviewing a blog's content performance.

Performance data (keyword -> published date, clicks, conversions):
{json.dumps(perf, indent=2)}

Affiliate focus areas: {strategy.get("primary_affiliate_focus")}

Based on this data:
1. Which types of content seem to perform best?
2. Should we adjust the affiliate focus?
3. What content types should we create more of?

Respond in 3 short bullet points, max 50 words each.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
    except Exception as e:
        print(f"Error: Groq API call failed while analyzing performance: {e}", file=sys.stderr)
        return None
    return response.choices[0].message.content.strip()

def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    client = Groq(api_key=api_key)
    strategy = load_json(STRATEGY_FILE)

    print("Generating new keywords...")
    new_keywords = generate_new_keywords(client, strategy)
    print(f"Found {len(new_keywords)} new keywords: {new_keywords}")

    if new_keywords:
        strategy["pending_keywords"].extend(new_keywords)
        strategy["last_strategy_update"] = datetime.now().strftime("%Y-%m-%d")

    insights = analyze_and_recommend(client, strategy)
    if insights:
        print("\nStrategy insights:\n", insights)
        strategy["last_insights"] = insights

    save_json(STRATEGY_FILE, strategy)
    print(f"\nStrategy updated. Total pending: {len(strategy['pending_keywords'])} keywords.")

if __name__ == "__main__":
    main()
