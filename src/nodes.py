# Node function for graph
from .state import TicketState
from .agents import classify_ticket, generate_draft_response,get_reviewer_agent
from .embeddings import build_vectorstores
import csv
from datetime import datetime

_vectorstores_cache = None

def get_vectorstores():
    global _vectorstores_cache
    if _vectorstores_cache is None:
        _vectorstores_cache = build_vectorstores()
    return _vectorstores_cache


def node_classify(state: TicketState) -> TicketState:
    result = classify_ticket(
        subject=state.get("subject"),
        description=state.get("description")
    )
    state["category"] = result.get("category")
    state["category_confidence"] = result.get("confidence")
    return state

def node_retrieve(state: TicketState) -> TicketState:
    VECTORSTORES = get_vectorstores()
    category = state.get("category", "General")
    query = f"{category} issue: {state.get('subject', '')} {state.get('description', '')}"

    store = VECTORSTORES.get(category, VECTORSTORES["General"])
    docs = store.similarity_search(query, k=2)

    retrieved = "\n".join([d.page_content for d in docs])
    state["context"] = retrieved
    return state


def node_respond(state: TicketState) -> TicketState:
    category = state.get("category", "General")
    context = state.get("context", "")
    subject = state.get("subject", "")
    description = state.get("description", "")

    # Print feedback for debugging
    feedbacks = state.get("review_feedbacks", [])
    feedback = feedbacks[-1] if feedbacks else ""

    response = generate_draft_response(
        category=category,
        context=context,
        subject=subject,
        description=description,
        feedback=feedback  # <-- Pass feedback here!
    )
    state["response"] = response
    return state

def reviewer_node(state: TicketState) -> TicketState:
    subject = state.get("subject", "")
    description = state.get("description", "")
    category = state.get("category", "General")
    response = state.get("response", "")
    response_text = getattr(response, "content", response)
    review_response = get_reviewer_agent(subject=subject, description=description, category=category, response=response_text)

    # Track attempts and feedback
    state["review_attempts"] = state.get("review_attempts", 0) + 1

    # Ensure lists are initialized
    if "failed_drafts" not in state or state["failed_drafts"] is None:
        state["failed_drafts"] = []
    if "review_feedbacks" not in state or state["review_feedbacks"] is None:
        state["review_feedbacks"] = []

    if review_response.get("REJECTED", False):
        state["failed_drafts"].append(response_text)
        state["review_feedbacks"].append(review_response.get("feedback", ""))
    state["review_response"] = review_response
    return state

def retry_response(state: TicketState) -> TicketState:
    # Use last feedback to refine context/query
    VECTORSTORES = get_vectorstores()
    feedback = state.get("review_feedbacks", [])[-1] if state.get("review_feedbacks") else ""
    category = state.get("category", "General")
    subject = state.get("subject", "")
    description = state.get("description", "")
    #  adjust query/context using feedback

    query = f"{category} issue: {subject} {description} {feedback}"
    store = VECTORSTORES.get(category, VECTORSTORES["General"])

    docs = store.similarity_search(query, k=2)
    retrieved = "\n".join([d.page_content for d in docs])
    state["context"] = retrieved
    return state


def node_escalate(state: TicketState) -> TicketState:
    subject = state.get("subject", "")
    description = state.get("description", "")
    failed_drafts = state.get("failed_drafts", [])
    feedbacks = state.get("review_feedbacks", [])

    # Log into CSV
    with open("escalation_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            subject,
            description,
            failed_drafts,
            feedbacks
        ])

    # Format failed drafts and feedbacks for readability
    drafts_str = "\n".join(
        [f"Draft {i+1}:\n{draft}\nFeedback:\n{feedback}\n{'-'*40}" 
         for i, (draft, feedback) in enumerate(zip(failed_drafts, feedbacks))]
    )

    state["final_response"] = (
        "Escalation Required: This ticket could not be auto-resolved.\n"
        "A human support agent must review.\n\n"
        f"Subject: {subject}\n"
        f"Description: {description}\n\n"
        f"category: {state.get('category', 'General')} | confidence: {state.get('category_confidence', 0.0)}\n\n"
        "==== Failed Drafts & Reviewer Feedback ====\n"
        f"{drafts_str}\n"
        "===========================================\n"
    )
    return state

def node_echo(state: TicketState) -> TicketState:

    response = state.get("response")
    original_response_text = getattr(response, "content", response)
    review_response = state.get("review_response", {})
    feedbacks = state.get("review_feedbacks", [])
    
    if feedbacks:
        feedback = feedbacks[-1]
        print(f"feeback on review was {feedback}\n")
        print("And Improved response based on feedback is below\n")
    
    response_text = review_response.get("response", original_response_text)
        
    state["final_response"] = response_text
    return state