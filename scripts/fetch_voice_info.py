#!/usr/bin/env python3
"""Script to fetch ElevenLabs voice information from the shared-voices API."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()


def fetch_voice_info(voice_ids: list[str]) -> list[dict]:
    """Fetch voice information for a list of voice IDs.
    
    Args:
        voice_ids: List of ElevenLabs voice IDs to look up.
        
    Returns:
        List of voice info dictionaries with keys: voice_id, status, name, languages
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not found in environment")
    
    headers = {"xi-api-key": api_key}
    base_url = "https://api.elevenlabs.io/v1/shared-voices"
    
    results = []
    unique_ids = list(dict.fromkeys(voice_ids))  # Remove duplicates, preserve order
    
    print(f"Searching for {len(unique_ids)} unique voice IDs...")
    
    with httpx.Client(timeout=30.0) as client:
        for voice_id in unique_ids:
            try:
                resp = client.get(
                    base_url,
                    headers=headers,
                    params={"search": voice_id, "page_size": 10}
                )
                resp.raise_for_status()
                data = resp.json()
                
                # Find exact match
                found = None
                for v in data.get("voices", []):
                    if v.get("voice_id") == voice_id:
                        found = v
                        break
                
                if found:
                    # Extract unique languages
                    langs = sorted(set(
                        vl.get("language", "") 
                        for vl in found.get("verified_languages", [])
                        if vl.get("language")
                    ))
                    results.append({
                        "voice_id": voice_id,
                        "status": "FOUND",
                        "name": found.get("name", "Unknown"),
                        "languages": langs,
                        "lang_count": len(langs),
                        "rate": found.get("rate", 1),
                        "free_users_allowed": found.get("free_users_allowed", False)
                    })
                    print(f"  ✅ {voice_id}: {found.get('name')} ({len(langs)} langs)")
                else:
                    results.append({
                        "voice_id": voice_id,
                        "status": "NOT_FOUND",
                        "name": "-",
                        "languages": [],
                        "lang_count": 0,
                        "rate": 0,
                        "free_users_allowed": False
                    })
                    print(f"  ❌ {voice_id}: NOT FOUND")
                    
            except Exception as e:
                results.append({
                    "voice_id": voice_id,
                    "status": "ERROR",
                    "name": str(e),
                    "languages": [],
                    "lang_count": 0,
                    "rate": 0,
                    "free_users_allowed": False
                })
                print(f"  ⚠️ {voice_id}: ERROR - {e}")
    
    return results


def generate_markdown_report(results: list[dict], output_path: str) -> None:
    """Generate a markdown report from voice search results.
    
    Args:
        results: List of voice info dictionaries.
        output_path: Path to save the markdown file.
    """
    # Filter: Only show found, free voices, sorted by language count
    valid_voices = [
        r for r in results 
        if r["status"] == "FOUND" and r.get("free_users_allowed", False)
    ]
    valid_voices.sort(key=lambda x: x["lang_count"], reverse=True)
    
    md = "# Voice ID Search Results\n\n"
    md += f"> {len(valid_voices)} valid voices (free, sorted by language count)\n\n"
    md += "| # | Voice ID | Name | Languages | Count |\n"
    md += "|---|----------|------|-----------|-------|\n"
    
    for i, r in enumerate(valid_voices, 1):
        langs = ", ".join(r["languages"]) if r["languages"] else "-"
        md += f"| {i} | `{r['voice_id']}` | {r['name']} | {langs} | {r['lang_count']} |\n"
    
    # Voices with Chinese support
    zh_voices = [r for r in valid_voices if "zh" in r["languages"]]
    if zh_voices:
        md += "\n## Voices with Chinese (zh) Support\n\n"
        for v in zh_voices:
            md += f"- **{v['name']}** (`{v['voice_id']}`)\n"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    
    print(f"\n📄 Report saved to: {output_path}")


if __name__ == "__main__":
    # Voice IDs to search
    voice_ids = [
        "EkK5I93UQWFDigLMpZcX",
        "lcMyyd2HUfFzxdCaC4Ta",
        "Dnd9VXpAjEGXiRGBf1O6",
        "wyWA56cQNU2KqUW4eCsI",
        "MFZUKuGQUsGJPQjTS4wC",
        "RILOU7YmBhvwJGDGjNmP",
        "Z3R5wn05IrDiVCyEkUrK",
        "tnSpp4vdxKPjI9w0GnoV",
        "NNl6r8mD7vthiJatiJt1",
        "c6SfcYrb2t09NHXiT80T",
        "B8gJV1IhpuegLxdpXFOE",
        "2zRM7PkgwBPiau2jvVXc",
        "1SM7GgM6IMuvQlz2BwM3",
        "scOwDtmlUjD3prqpp97I",
        "NOpBlnGInO9m6vDvFkFC",
        "Sm1seazb4gs7RSlUVw7c",
        "P1bg08DkjqiVEzOn76yG",
        "kUUTqKQ05NMGulF08DDf",
        "cgSgspJ2msm6clMCkdW9",
        "FGY2WhTYpPnrIDTdsKH5",
        "iP95p4xoKVk53GoZ742B",
        # New voice IDs
        "1t1EeRixsJrKbiF1zwM6",
        "FUfBrNit0NNZAwb58KWH",
        "bhJUNIXWQQ94l8eI2VUf",
        "4O1sYUnmtThcBoSBrri7",
        "dn9HtxgDwCH96MVX9iAO",
        "tgfcQY9SGvn3GfmnNWIi",
        "93nuHbke4dTER9x2pDwE",
    ]
    
    results = fetch_voice_info(voice_ids)
    generate_markdown_report(results, "reports/voice-search-results.md")
