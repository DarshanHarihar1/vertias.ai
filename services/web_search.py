import os
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


serpapi_url = os.getenv("SERPAPI_URL")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")

if not serpapi_url or not serpapi_api_key:
    raise ValueError("SERPAPI_URL and SERPAPI_API_KEY must be set in environment variables.")


def build_search_query(parsed_claim: Dict[str, Optional[str]]) -> str:
    """
    Builds a smarter search query from parsed claim entities.
    """
    parts = []

    if parsed_claim.get("player_or_team"):
        parts.append(parsed_claim["player_or_team"])

    if parsed_claim.get("event"):
        parts.append(parsed_claim["event"])

    if parsed_claim.get("league_or_tournament"):
        parts.append(parsed_claim["league_or_tournament"])

    # Keep date at the end (optional context)
    if parsed_claim.get("date"):
        parts.append(parsed_claim["date"])

    return " ".join(part for part in parts if part)

def search_web_from_parsed_claim(parsed_claim: Dict[str, Optional[str]], num_results: int = 5) -> List[Dict[str, str]]:
    query = build_search_query(parsed_claim)
    logger.info(f"[WebSearch] Searching for: {query}")
    params = {
        "q": query,
        "api_key": serpapi_api_key,
        "engine": "google",
        "num": num_results
    }

    try:
        response = requests.get(serpapi_url, params=params)
        response.raise_for_status()
        data = response.json()

        organic_results = data.get("organic_results", [])

        # Fallback to related search if empty
        if not organic_results and data.get("related_searches"):
            related_link = data["related_searches"][0].get("serpapi_link")
            if related_link:
                logger.info(f"[WebSearch] Fallback to related search: {related_link}")
                fallback_resp = requests.get(related_link, params={"api_key": serpapi_api_key})
                fallback_resp.raise_for_status()
                data = fallback_resp.json()
                organic_results = data.get("organic_results", [])

        results = []
        for item in organic_results[:num_results]:
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet") or "No snippet available.",
                "link": item.get("link")
            })

        logger.info(f"[WebSearch] Found {len(results)} results.")
        return results

    except Exception as e:
        logger.error(f"[WebSearch] Error during web search: {e}")
        return []