import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from .summarizer import summarize_text
import logging

logger = logging.getLogger(__name__)


def fallback_extract_with_bs4(url: str) -> str:
    """
    Extract readable content from a URL using BeautifulSoup.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        for tag in soup(["script", "style", "header", "footer", "nav", "form", "aside"]):
            tag.decompose()

        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        return "\n".join(paragraphs)

    except Exception as e:
        print(f"[BS4 Fallback Error] {str(e)}")
        return ""


def summarize_evidence_with_fallback(result: Dict[str, str], max_words: int = 200) -> str:
    """
    Tries to summarize the full article content from the URL,
    falling back to SerpAPI snippet if content can't be extracted.
    """
    url = result.get("link", "")
    title = result.get("title", "")
    snippet = result.get("snippet", "")

    full_text = ""

    full_text = fallback_extract_with_bs4(url)
    logger.info(f"[Summarizer] Extracted {len(full_text.split())} words from URL.")


    # 3. Final fallback to title + snippet
    if not full_text:
        print("[Summarizer] BS4 failed. Using SerpAPI metadata.")
        fallback_text = f"{title}. {snippet}"
        return summarize_text(fallback_text, max_words=max_words) or fallback_text

    return summarize_text(full_text, max_words=max_words) or full_text[:max_words]

def summarize_all_results(results: List[Dict[str, str]], max_words: int = 200) -> List[str]:
    """
    Summarizes a list of SerpAPI search results using fallback logic.
    """
    summaries = []
    for result in results:
        summary = summarize_evidence_with_fallback(result, max_words)
        summaries.append(summary)
    return summaries

