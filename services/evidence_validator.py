from typing import List, Dict
import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_model = os.getenv("GEMINI_MODEL")

if not gemini_api_key or not gemini_model:
    raise ValueError("GEMINI_API_KEY and GEMINI_MODEL must be set in environment variables.")


genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel(gemini_model)


def validate_claim(claim: str, evidence_list: List[str], source_links: List[str] = []) -> Dict[str, str]:
    """
    Use Gemini to validate the claim using summarized evidence.
    Returns: verdict (True / False / Unclear), justification, and optional sources.
    """
    combined_evidence = "\n\n".join(f"- {e}" for e in evidence_list)
    links_text = "\n".join(source_links) if source_links else ""

    prompt = f"""
        You are a factual reasoning assistant that verifies sports-related claims based on real-world evidence.

        CLAIM:
        "{claim}"

        EVIDENCE:
        {combined_evidence}

        Evaluate whether the claim is factually correct based on the evidence.

        Respond in the following JSON format:
        {{
        "verdict": "True" | "False" | "Unclear",
        "justification": "Explain your reasoning in 2-3 sentences.",
        "evidence_used": ["{links_text}"]
        }}

        Only use the evidence provided. Do not assume anything outside of it.
        """

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Auto-clean Markdown/JSON
        import json, re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            logger.info(f"[EvidenceValidator] Parsed JSON: {match.group(0)}")
            return json.loads(match.group(0))
        
        return {"verdict": "Unclear", "justification": "Unable to parse LLM response.", "evidence_used": source_links}

    except Exception as e:
        logger.error(f"[EvidenceValidator Error] {str(e)}")
        return {
            "verdict": "Unclear",
            "justification": "An error occurred while processing the claim.",
            "evidence_used": source_links
        }
