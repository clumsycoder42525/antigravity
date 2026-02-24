from serpapi import GoogleSearch   # ✅ correct ONLY with google-search-results
import os

def bing_search(query: str, max_results: int = 5) -> str:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return ""

    search = GoogleSearch({
        "engine": "bing",
        "q": query,
        "api_key": api_key,
        "num": max_results
    })

    data = search.get_dict()
    results = []

    for r in data.get("organic_results", []):
        results.append(r.get("snippet", ""))

    return "\n".join(results)
