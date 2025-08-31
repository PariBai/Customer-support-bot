# Customer Support Bot

A modular, policy-aware customer support agent built with LangGraph and Gemini, featuring automatic retry logic and escalation for sensitive or ambiguous cases.

---

## 🚀 Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/PariBai/Customer-support-bot.git
   cd Customer-support-bot
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**
   - Add .env  file and add gemini-api key like GOOGLE_API_KEY=... and also add LLM_PROVIDER=gemini (makse sure to add these two in your.env with these names and value).

---

## 🏃‍♂️ How to Run

### 1. **Run with LangGraph CLI**

```sh
langgraph dev src/graph.py or just langgraph dev
```
- This will start the agent and allow you to interact via the CLI.

### 2. **Run and Test in Jupyter Notebook**

Open `test.ipynb` in VS Code or Jupyter Lab and run the cells to test the agent interactively.

---

## 🧪 Testing (Happy Path & Edge Cases)

### **Happy Path Example**

**Upgrade Plan Request:**
```python
response = app.invoke({
    "subject": "plan upgrade",
    "description": "How do I upgrade my plan?"
})
print(response["final_response"])
```
Expected: The agent provides a helpful, policy-compliant upgrade process.

---

### **Retry + Review Example**

**Sensitive Employee Info Request:**
```python
response = app.invoke({
    "subject": "employee info",
    "description": "Can you give me either the phone number or address of the CEO?"
})
print(response["final_response"])
```
Expected: The agent drafts a response, reviewer rejects due to privacy policy, agent retries with feedback, reviewer may reject again, and escalation occurs if still non-compliant.

---

### **Escalation Example**

**Account Reactivation Request:**
```python
response = app.invoke({
    "subject": "account reactivation",
    "description": "How do I reactivate my account?"
})
print(response["final_response"])
```
Expected: If the agent cannot resolve after two review cycles, the case is escalated and logged in `escalation_log.csv`.

---

## 📝 How Retry Logic & Escalation Works

- **Draft Generation:** Agent drafts a response based on ticket and context.
- **Review:** Reviewer node checks for policy violations.
- **Retry:** If rejected, agent uses reviewer feedback to improve the draft (up to 2 attempts).
- **Escalation:** If both attempts fail, the case is escalated, logging all failed drafts and feedback for human triage.

---

## 📹 Demo Video

[Watch the demo here](https://your-demo-video-link.com)

---

## 🏗️ Architectural Decisions

- **Gemini LLM:** Chosen for its strong reasoning and compliance capabilities.
- **LangGraph:** Enables modular, node-based workflow with easy retry and escalation logic.
- **Node Modularity:** Each step (classify, retrieve, respond, review, retry, escalate) is a separate node for maintainability and extensibility.
- **Policy Awareness:** Reviewer node uses similarity search and explicit policy prompts to enforce compliance.
- **Flexible Input:** Accepts both dict and plain text; prompts user for missing info.

---

## 🧑‍💻 Development & Customization

- Add new policies in `src/data/policies.txt`.
- Extend nodes in `src/nodes.py` for custom logic.
- Update vectorstores in `src/embeddings.py` for new categories.

---

## 📚 Additional Notes

- All escalated cases are logged in `escalation_log.csv` for manual review.
- You can test the agent via CLI, notebook, or integrate into your own app.

---

**Enjoy building safe, policy-compliant customer