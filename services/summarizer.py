from transformers import pipeline
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

summarization_model = os.getenv("SUMMARIZATION_MODEL")
summarizer = pipeline("summarization", model=summarization_model)

def summarize_text(text: str, max_words: int = 100, max_sentences: int = 3) -> Optional[str]:
    """
    Summarize the input text if it's too long.
    Returns the summary or the original text if short enough.
    """
    if len(text.split()) <= max_words:
        logger.info(f"[Summarizer] Text is short enough ({len(text.split())} words). No summarization needed.")
        return text

    try:
        summary = summarizer(
            text,
            max_length=130,  # rough token estimate for 2–3 sentences
            min_length=30,
            do_sample=False
        )
        logger.info(f"[Summarizer] Summarized text to {len(summary[0]['summary_text'].split())} words.")
        return summary[0]["summary_text"]
    except Exception as e:
        print(f"[Summarizer Error] {str(e)}")
        return None