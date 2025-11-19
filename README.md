# 📧 Email Productivity Agent

An intelligent, AI-powered email management system built with **Streamlit**, **LangChain**, **LangGraph**, and **Google Gemini**. This application helps users categorize emails, extract action items, chat with their inbox, and generate email drafts automatically.

## 🚀 Features

- **Inbox Management**: Load and view emails from a JSON source.
- **AI Categorization**: Auto-classify emails (Important, To-Do, Newsletter, etc.) and detect priority.
- **Action Extraction**: Automatically identify tasks and action items within emails.
- **Email Agent (Chat)**: RAG-powered chat interface to query your inbox or specific emails.
- **Draft Generation**: AI-assisted drafting for new emails and replies with context awareness.
- **Customizable Prompts**: Edit system prompts directly from the UI to control AI behavior.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)
- **AI Model**: Google Gemini (`gemini-2.5-flash-lite`) via `langchain-google-genai`
- **Data Handling**: Pandas, JSON
- **Environment Management**: Python Dotenv

## ⚙️ Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Yuvraj-ai/Email_Productivity_Agent.git
    cd Email_Productivity_Agent
    ```

2.  **Create and activate a virtual environment** (optional but recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If `requirements.txt` is missing, install manually:*
    ```bash
    pip install streamlit pandas python-dotenv langchain-google-genai langchain langgraph pydantic
    ```

4.  **Set up Environment Variables**:
    Create a `.env` file in the root directory and add your Google API Key:
    ```env
    GOOGLE_API_KEY=your_google_api_key_here
    ```

## 🏃‍♂️ How to Run

The application uses Streamlit for the frontend which integrates directly with the Python backend.

1.  **Start the application**:
    ```bash
    streamlit run app.py
    ```

2.  **Access the UI**:
    The application will open automatically in your default web browser at `http://localhost:8501`.

## 📖 Usage Guide

### 1. Loading the Mock Inbox
To simulate a real email environment, the app uses a JSON file (`sources/inbox.json`) as a mock inbox.
- Navigate to the **Home** tab.
- Click the **"Load Emails"** button in the sidebar or main area.
- Once loaded, click **"Categorize Emails"** to run the AI processing. This will generate summaries, tags, and action items.

### 2. Configuring Prompts
You can customize how the AI behaves without touching the code.
- Open the **Sidebar** on the left.
- Expand the **"Edit Prompts"** section.
- Select the prompt type you want to edit:
    - **Categorization**: Rules for classifying emails.
    - **Action Extraction**: Rules for identifying tasks.
    - **Drafting**: Instructions for style and tone.
- Modify the text and click **"Save Prompts"**.

### 3. Usage Examples

#### Scenario A: Triage Your Inbox
1.  Go to the **Home** page.
2.  Load and Categorize emails.
3.  Look at the **"Processed Emails"** table.
4.  Sort by **Priority** to see "High" priority emails first.
5.  Expand an email row to read the **Summary** and **Action Items**.

#### Scenario B: Chat with your Email
1.  Switch to the **Email Agent** page.
2.  Select a specific email from the sidebar dropdown (e.g., "Project Update").
3.  Ask the agent: *"What are the key deadlines mentioned here?"* or *"Summarize the main points."*

#### Scenario C: Draft a Reply
1.  Switch to the **Draft Agent** page.
2.  Select the email you want to reply to.
3.  In the instructions box, type: *"Accept the meeting invitation and ask if we can move it to 3 PM."*
4.  Click **"Generate Draft"**.
5.  Review the generated text in the editor, make tweaks, and click **"Save Draft"**.

## 📂 Project Structure

```
Email_Productivity_Agent/
├── app.py                  # Main Streamlit application entry point
├── backend/
│   ├── agent.py            # LangGraph agent logic for Chat and Drafting
│   ├── categorizer.py      # Logic for batch categorization of emails
│   ├── structure.py        # Pydantic models for data validation
│   └── extractor/          # Helper modules for data extraction
├── sources/
│   ├── inbox.json          # Mock input emails
│   ├── processed_inbox.json # Output after AI processing
│   ├── drafts.json         # Saved drafts
│   └── prompts.json        # Customizable system prompts
└── .env                    # API keys (not committed)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
