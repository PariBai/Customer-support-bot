# src/nodes/classifier.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .utils import get_llm
from .tools import policy_lookup
from .state import TicketState


def build_classifier():
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a support ticket classifier.\n"
            "Your job is to carefully read the **subject** and **description** of a support ticket, "
            "then decide which one of these categories it belongs to: Billing, Technical, Security, General.\n"
            "for each category, here are some guidelines:\n\n"
            "- Billing: Issues related to invoices, payments, refunds, account charges, subscription plans and etc.\n"
            "- Technical: Problems with software functionality, bugs, error messages, performance issues login, reactivation, reset password, app not loading and etc.\n"
            "- Security: Concerns about account security, data breaches, password best practices, unauthorized access, phishing and etc.\n"
            "- General: Any other inquiries that do not fit into the above categories, including product information, features include, inital setup guide, profile settings, team invitation settings, basic navigationguide, and general feedback and any other things.\n\n"

            "Rules:\n"
            "1. Always choose exactly one category.\n"
            "2. Base your decision primarily on the description and the subject.\n"
            "3. Return the result in JSON format with two fields:\n"
            '   - category: string (one of the categories)\n'
            "   - confidence: float between 0 and 1 (your confidence in the classification)\n\n"
            "Example output:\n"
           "category: Billing, confidence: 0.87"
        ),
        ("human", "Subject: {subject}\nDescription: {description}")
    ])

    parser = JsonOutputParser()
    chain = prompt | llm | parser
    return chain

def classify_ticket(subject: str, description: str):
    agent = build_classifier()
    return agent.invoke({
        "subject": subject,
        "description": description,
    })

def generate_draft_response(category: str, context: str, subject: str, description: str , feedback: str = ""):
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful customer support assistant.\n"
        "Your job: Generate a professional response using the ticket subject/description, context from knowledge base, and reviewer feedback.\n\n"
        "Rules:\n"
        "1. If reviewer feedback restricts sharing certain information, you must NOT include it in your response, even if context suggests it.\n"
        "2. Always follow reviewer feedback strictly.\n"
        "3. If feedback suggest or restricts you for something strictly follow feedback to generate your response.\n"
        "4. Be polite and professional.\n"
        "5. Address the specific issue mentioned in the subject and description.\n"
        "6. If context is insufficient and no feedback is provided, generate a generic but helpful response.\n"
        "7. If feedback conflicts with context, feedback takes priority.\n"
        "Example: If feedback says 'do not share salary info', your response should say 'Sorry, we cannot share that information due to company policy.'"
    ),
    ("human", "Category: {category}\nContext: {context}\nSubject: {subject}\nDescription: {description}\nFeedback: {feedback}\nDraft a response:")
])

    chain = prompt | llm
    return chain.invoke({
        "category": category,
        "context": context,
        "subject": subject,
        "description": description,
        "feedback": feedback
    })

def get_reviewer_agent(subject: str, description: str, category: str, response: str):
    llm = get_llm() 
    policy_result = policy_lookup({"category": category, "subject": subject, "description": description })
    
    # Now use LLM to make the review decision
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a reviewer for customer support responses.\n"
            "You will be given a support ticket subject, description, category and a drafted response, along with relevant company policies.\n"
            "Your job is to review the response against company policies and guidelines.\n\n"
            "Rules:\n"
            "1. Check if the response violates any company policies\n"
            "2. Ensure the response is professional and helpful\n"
            "3. Return your decision in JSON format with one of these structures:\n\n"
            "If APPROVED:\n"
            "APPROVED: true, response: the approved response text\n\n"
            "If REJECTED:\n"
            "REJECTED: true, feedback: explanation of why rejected and what needs improvement\n\n"
            "Company Policies:\n{policies}\n"
        ),
        (
            "human", 
            "Subject: {subject}\n"
            "Description: {description}\n"
            "Category: {category}\n"
            "Drafted Response: {response}\n\n"
            "Please review this response and provide your decision in JSON format."
        )
    ])
    
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    return chain.invoke({
        "subject": subject,
        "description": description,
        "category": category,
        "response": response,
        "policies": policy_result
    })
