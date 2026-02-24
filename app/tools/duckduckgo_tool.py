from ddgs import DDGS
from app.utils.logger import get_logger

logger = get_logger("DuckDuckGoTool")

def duckduckgo_search(query: str, max_results: int = 5) -> list:
    """
    Search DuckDuckGo and return structured data with title, body, and URL.
    Uses modern ddgs package.
    
    Returns:
        list of dicts with keys: title, body, url
        Empty list [] if search fails
    """
    try:
        results = []
        with DDGS() as ddgs:
            # Using text search which provides title, body (snippet), and href (url)
            ddgs_results = ddgs.text(query, max_results=max_results)
            for r in ddgs_results:
                results.append({
                    "title": r.get("title", "No Title"),
                    "body": r.get("body", r.get("snippet", "")),
                    "url": r.get("href", r.get("link", ""))
                })

        logger.info(f"🦆 DuckDuckGo search completed: {len(results)} results")
        return results

    except Exception as e:
        logger.warning(f"DuckDuckGo failed: {e}")
        return []
