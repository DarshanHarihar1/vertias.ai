from fastapi import HTTPException
from fastapi import APIRouter
import logging
from services.claim_parser import extract_claim_entities
from services.web_search import search_web_from_parsed_claim
from services.article_summarizer import summarize_all_results
from services.evidence_validator import validate_claim
from fastapi import FastAPI, HTTPException
from models.pydantic_models import ParsedEntities, FactCheckResponse, ClaimRequest

logger = logging.getLogger(__name__)


router = APIRouter()

@router.post("/fact-check", response_model=FactCheckResponse)
def fact_check(request: ClaimRequest):
    claim = request.claim
    logger.info(f"Received claim: {claim}")

    parsed_entities = extract_claim_entities(claim)
    logger.info(f"Parsed entities: {parsed_entities}")
    if not parsed_entities:
        raise HTTPException(status_code=400, detail="Could not extract entities from claim.")

    results = search_web_from_parsed_claim(parsed_entities)
    logger.info(f"Search results: {results}")
    if not results:
        raise HTTPException(status_code=404, detail="No search results found.")

    summaries = summarize_all_results(results)
    links = [r["link"] for r in results]
    logger.info(f"Summaries: {summaries}")

    validation = validate_claim(claim, summaries, links)
    logger.info(f"Validation result: {validation}")

    return FactCheckResponse(
        verdict=validation["verdict"],
        justification=validation["justification"],
        evidence_used=validation["evidence_used"],
        parsed_entities=ParsedEntities(**parsed_entities)
    )
