import wikipedia
from app.utils.logger import get_logger

logger = get_logger("WikipediaTool")

def wikipedia_search(query: str) -> dict:
    """
    Search Wikipedia and return structured data with title, summary, and URL.
    
    Returns:
        dict with keys: title, summary, url
        Empty dict {} if search fails
    """
    try:
        # Search for the most relevant page first to avoid "Page id does not match" errors
        search_results = wikipedia.search(query)
        if not search_results:
            logger.warning(f"No Wikipedia results found for: {query}")
            return {}
        
        # Use the first search result title
        page_title = search_results[0]
        page = wikipedia.page(page_title)
        summary = wikipedia.summary(page_title, sentences=5)
        
        logger.info(f"📘 Wikipedia search completed for: {page_title}")
        
        return {
            "title": page_title,
            "summary": summary,
            "url": page.url
        }

    except wikipedia.exceptions.DisambiguationError as e:
        logger.warning(f"Wikipedia disambiguation error for '{query}': {e.options}")
        # Try the first result from disambiguation options
        try:
            first_option = e.options[0]
            page = wikipedia.page(first_option)
            summary = wikipedia.summary(first_option, sentences=5)
            return {
                "title": first_option,
                "summary": summary,
                "url": page.url
            }
        except:
            return {}
    except wikipedia.exceptions.PageError:
        logger.warning(f"Wikipedia page not found for: {query}")
        return {}
    except Exception as e:
        logger.warning(f"Wikipedia failed unexpectedly: {e}")
        return {}
