from typing_extensions import TypedDict
from typing import Optional, List

class RequiredTicketState(TypedDict):
    subject: str
    description: str

class TicketState(RequiredTicketState, total=False):
    category: str
    category_confidence: float
    context: str
    response: str
    review_response: str
    review_attempts: int
    failed_drafts: List[str]
    review_feedbacks: List[str]
    end_early: bool
    final_response: Optional[str]
