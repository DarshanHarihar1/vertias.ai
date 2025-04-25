from typing import Dict, Optional
import google.generativeai as genai
from google import genai
from google.genai import types
import re
import json
import os
import logging

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

if not GEMINI_API_KEY or not GEMINI_MODEL:
    raise ValueError("GEMINI_API_KEY and GEMINI_MODEL must be set in environment variables.")

def clean_gemini_json(raw_text: str) -> str:
    """
    Removes Markdown code fences and extracts the JSON content.
    """
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    return match.group(1) if match else raw_text.strip()


def extract_claim_entities(claim: str) -> Optional[Dict[str, str]]:
    """
    Parses a sports claim using Gemini to extract key entities like:
    - Subject
    - Event
    - Date
    - Player/Team
    - League
    - Match

    Returns a dict with extracted entities.
    """

    try:
        system_instructions = """
        You are an expert sports fact-checking assistant. Your task is to analyze claims related to sports events and extract structured information about the claim. You will be provided with a claim, and you need to identify key entities such as the subject, event, date, player/team, league/tournament, and location. Your output should be in JSON format.
        The JSON should contain the following fields:
        - subject: The main subject of the claim (e.g., player, team).
        - event: The specific event being claimed (e.g., match, game).
        - date: The date of the event (e.g., YYYY-MM-DD).
        - player_or_team: The player or team involved in the claim.
        - league_or_tournament: The league or tournament associated with the event.
        - location: The location of the event (e.g., stadium, city).
        You should return the results in this exact JSON format:
        {
        "subject": "...",
        "event": "...",
        "date": "...",
        "player_or_team": "...",
        "league_or_tournament": "...",
        "location": "..."
        }

        Make sure to provide clear and concise information. If any field is not mentioned or unclear, set it to null.
        """

        config = types.GenerateContentConfig(
            system_instruction=system_instructions,
        )
        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=claim,
            config=config,
        )

        cleaned_text = clean_gemini_json(response.text)
        parsed_json = json.loads(cleaned_text)
        logger.info(f"[ClaimParser] Parsed JSON: {parsed_json}")
        if not isinstance(parsed_json, dict):
            raise ValueError("Parsed JSON is not a dictionary.")

        return parsed_json

    except Exception as e:
        logger.error(f"[ClaimParser Error] {str(e)}")
        return None
