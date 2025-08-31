from langgraph.graph import StateGraph, END
from .state import TicketState
from .nodes import node_echo, node_classify, node_retrieve, node_respond, reviewer_node, retry_response, node_escalate

def build_graph():
    g = StateGraph(TicketState)
    g.add_node("classify", node_classify)
    g.add_node("retrieve", node_retrieve)
    g.add_node("respond", node_respond)
    g.add_node("review", reviewer_node)
    g.add_node("retry", retry_response)
    g.add_node("escalate", node_escalate)
    g.add_node("echo", node_echo)

    g.set_entry_point("classify")
    g.add_edge("classify", "retrieve")
    g.add_edge("retrieve", "respond")
    g.add_edge("respond", "review")

    # Use add_conditional_edges for review node
    def review_decision(state: TicketState):
        if state.get("review_response", {}).get("REJECTED", False):
            if state.get("review_attempts", 0) < 2:
                return "retry"
            else:
                return "escalate"
        else:
            return "echo"

    g.add_conditional_edges("review", review_decision)
    g.add_edge("retry", "respond")
    g.add_edge("escalate", END)
    g.add_edge("echo", END)

    return g.compile()