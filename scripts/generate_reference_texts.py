"""Generate reference texts for candidate LLM attribution profiling.

Usage:
    python scripts/generate_reference_texts.py [--topics 5] [--max-tokens 2000]

Requires API keys in environment:
- OPENAI_API_KEY for OpenAI models (e.g. gpt-4o)
- ANTHROPIC_API_KEY for Anthropic models (e.g. claude-3-5-sonnet-20241022)
- GOOGLE_API_KEY for Google Gemini models (e.g. gemini-1.5-pro)

Note: This is OPTIONAL. Fingerprints only need to be built if candidate attribution
is being configured. Human reference texts should be placed in data/reference_texts/human/.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

REF_DIR = BASE_DIR / "data" / "reference_texts"

PROMPT_TEMPLATE = (
    "Write an extensive, rigorous academic paper section (at least 1,500 words) discussing: {topic}. "
    "Use standard scientific terminology, formal academic syntax, structured arguments, and theoretical analysis."
)

TOPICS = [
    "Distributed consensus protocols under adversarial Byzantine network conditions",
    "Scalability and privacy trade-offs in decentralized verifiable computation",
    "Transformer attention sparsity mechanisms for sub-quadratic sequence modeling",
    "Zero-knowledge proof systems for verifiable state transitions in distributed ledgers",
    "Theoretical bounds of adversarial robustness in deep neural representations",
]


def print_cost_warning():
    print("================================================================================")
    print("COST AND API USAGE WARNING")
    print("--------------------------------------------------------------------------------")
    print("This script will call commercial LLM APIs using your configured environment keys.")
    print("Estimated cost: approximately $0.05 - $0.30 per 10 long scientific texts depending")
    print("on the provider. Press Ctrl+C within 5 seconds to abort if you do not wish to proceed.")
    print("================================================================================")
    for i in range(5, 0, -1):
        print(f"Proceeding in {i}...", end="\r", flush=True)
        time.sleep(1.0)
    print("\nStarting generation...")


def generate_openai(topic: str, output_path: Path):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(topic=topic)}],
        temperature=0.7,
        max_tokens=2500,
    )
    content = resp.choices[0].message.content
    output_path.write_text(content, encoding="utf-8")


def generate_anthropic(topic: str, output_path: Path):
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(topic=topic)}],
        max_tokens=2500,
        temperature=0.7,
    )
    content = resp.content[0].text
    output_path.write_text(content, encoding="utf-8")


def generate_google(topic: str, output_path: Path):
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-pro")
    resp = model.generate_content(PROMPT_TEMPLATE.format(topic=topic))
    output_path.write_text(resp.text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate reference texts via LLM APIs.")
    parser.add_argument("--topics", type=int, default=5, help="Number of topics to generate")
    args = parser.parse_args()

    active_providers = []
    if os.getenv("OPENAI_API_KEY"):
        active_providers.append(("openai_gpt4o", generate_openai))
    if os.getenv("ANTHROPIC_API_KEY"):
        active_providers.append(("anthropic_claude", generate_anthropic))
    if os.getenv("GOOGLE_API_KEY"):
        active_providers.append(("google_gemini", generate_google))

    if not active_providers:
        print("[NOTE] No LLM API keys found in environment (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY).")
        print("To generate reference texts, set at least one API key in your .env file.")
        print("Human reference texts can be manually placed in data/reference_texts/human/.")
        sys.exit(0)

    print_cost_warning()

    for provider_name, gen_func in active_providers:
        prov_dir = REF_DIR / provider_name
        prov_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n--- Generating for provider: {provider_name} ---")
        for idx, topic in enumerate(TOPICS[:args.topics]):
            out_file = prov_dir / f"ref_{idx+1}.txt"
            if out_file.exists():
                print(f"Skipping {out_file.name} (already exists)")
                continue
            print(f"Generating sample {idx+1}/{args.topics}: '{topic[:40]}...'")
            try:
                gen_func(topic, out_file)
                print(f"  [OK] Saved to {out_file}")
            except Exception as e:
                print(f"  [ERROR] Generation failed: {e}")
            time.sleep(1.0)


if __name__ == "__main__":
    main()

