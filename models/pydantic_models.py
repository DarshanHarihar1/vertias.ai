from pydantic import BaseModel
from typing import List, Optional

class ParsedEntities(BaseModel):
    subject: Optional[str]
    event: Optional[str]
    date: Optional[str]
    player_or_team: Optional[str]
    league_or_tournament: Optional[str]
    location: Optional[str]

# Output model
class FactCheckResponse(BaseModel):
    verdict: str
    justification: str
    evidence_used: List[str]
    parsed_entities: ParsedEntities

# Input model
class ClaimRequest(BaseModel):
    claim: str
