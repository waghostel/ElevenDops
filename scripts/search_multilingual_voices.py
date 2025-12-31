#!/usr/bin/env python3
"""Script to search/fetch shared voices and rank them by language count."""

import os
import httpx
import json
from dotenv import load_dotenv
import time

load_dotenv()

def search_multilingual_voices(limit: int = 200) -> list[dict]:
    """Fetch shared voices and return them processed."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not found")
    
    headers = {"xi-api-key": api_key}
    base_url = "https://api.elevenlabs.io/v1/shared-voices"
    
    all_voices = []
    page_size = 100
    
    print(f"Fetching top {limit} voices from Library...")
    
    # We'll fetch a few pages. 
    # Note: 'featured' or 'professional' might be good filters, but let's try general popular ones first.
    # The API doesn't document sort order well publicly, but usually it's popularity/trending.
    
    try:
        with httpx.Client(timeout=30.0) as client:
            # Page 1
            print("  Fetching page 1...")
            resp = client.get(base_url, headers=headers, params={"page_size": page_size})
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("voices"):
                v1 = data["voices"][0]
                print("DEBUG: All Keys:")
                for k in sorted(v1.keys()):
                    print(f"  - {k}")
            
            all_voices.extend(data.get("voices", []))
            
            # Page 2 if needed
            if len(all_voices) < limit and data.get("has_more"):
                print("  Fetching page 2...")
                # Pagination uses 'reader' token usually or page index?
                # V1 shared-voices uses ?page_size & ?page? Or ?cursor?
                # Looking at response, checks for 'last_sort_id' usually.
                # Let's assume just grabbing top 100 is enough for a good sample, 
                # or try to get more if possible. 
                # For safety/simplicity in this script, getting top 100 featured is a great start.
                pass
                
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return []

    print(f"Analyze {len(all_voices)} voices...")
    processed = []
    
    for v in all_voices:
        # Extract unique languages
        # 'verified_languages' is a list of objects usually: [{'language': 'en', ...}]
        langs = sorted(set(
            vl.get("language", "") 
            for vl in v.get("verified_languages", [])
            if vl.get("language")
        ))
        
        processed.append({
            "voice_id": v["voice_id"],
            "name": v.get("name", "Unknown"),
            "category": v.get("category", "-"),
            "languages": langs,
            "lang_count": len(langs),
            "cloned_by_count": v.get("cloned_by_count", 0),
            "featured": v.get("featured", False),
            "description": v.get("description", "")[:100].replace("\n", " "),
            "preview_url": v.get("preview_url")
        })

    # Sort by Popularity (cloned_by_count) desc
    processed.sort(key=lambda x: x["cloned_by_count"], reverse=True)
    
    return processed[:limit]

def generate_report(voices: list[dict], output_path: str):
    """Generate markdown report."""
    md = "# Top Popular Voices Report\n\n"
    md += "This report lists voices from the ElevenLabs Library sorted by popularity (Usage/Clone Count).\n\n"
    
    md += "| # | Voice ID | Name | Category | Usage | Languages |\n"
    md += "|---|----------|------|----------|-------|-----------|\n"
    
    for i, v in enumerate(voices, 1):
        langs = ", ".join(v["languages"]) if v["languages"] else "-"
        usage_str = f"{v['cloned_by_count']:,}"
        name_display = f"**{v['name']}**"
        if v['featured']:
            name_display += " (Featured)"
            
        md += f"| {i} | `{v['voice_id']}` | {name_display} | {v['category']} | {usage_str} | {langs} |\n"
    
    md += "\n## How to use\n"
    md += "To use these voices, you must add them to your Voice Lab:\n"
    md += "1. Copy the `Voice ID`.\n"
    md += "2. Go to [ElevenLabs Voice Library](https://elevenlabs.io/voice-library).\n"
    md += "3. Search/Filter or use the API to add them.\n"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    
    print(f"Report saved to: {output_path}")

if __name__ == "__main__":
    voices = search_multilingual_voices(limit=100)
    generate_report(voices, "reports/top-multilingual-voices.md")
