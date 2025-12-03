🤖 AI Recruitment Agent (GIKI HR Assistant)An intelligent, conversational AI agent designed to automate HR recruitment queries. This application interacts with candidates, checks their application status via a backend API, and sends official confirmation emails using a secure SMTP workflow.Built with LangGraph, FastAPI, Streamlit, and Google Gemini 2.5 Flash.🌟 Features🗣️ Conversational Interface: A ChatGPT-like UI where users can chat naturally. The agent remembers context and extracts information (User IDs, Emails) automatically.🧠 Intelligent Orchestration: Uses LangGraph state machines to route decisions (e.g., Does the user want to check status? Do they want an email?).🔌 Real-time Backend: Connects to a FastAPI service to simulate a real HR database.📧 Email Automation: Sends formatted, professional emails via SMTP (configured with Mailtrap for testing) with strict header sanitization.🕵️ Live Debug Panel: A side-panel in the UI that visualizes the agent's internal thought process, logs, and state changes in real-time.🏗️ ArchitectureThe system consists of three main components working in unison:graph TD
    User((User)) <--> UI[Streamlit Frontend]
    UI <--> Brain[LangGraph Agent]
    
    subgraph "The Agent Brain"
        Brain --> Parse[Conversation Manager]
        Parse -->|Needs Data| API_Node[Status Lookup Node]
        Parse -->|Confirmed| Email_Node[Email Sender Node]
    end
    
    API_Node <-->|HTTP GET| DB[FastAPI Backend]
    Email_Node <-->|SMTP/TLS| Mail[Mailtrap Server]
🛠️ Tech StackLanguage: Python 3.13Frontend: StreamlitBackend: FastAPI, UvicornAI Model: Google Gemini 2.5 Flash (via langchain-google-genai)Orchestration: LangGraph, LangChain CoreEmail: SMTP (Standard Library) with Mailtrap Sandbox🚀 Installation & SetupPrerequisitesPython 3.10 or higher (Python 3.13 recommended)A Google AI Studio API Key.A Mailtrap Account (Free Tier).1. Clone & Environment Setup# Create a virtual environment
python3 -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
2. Install Dependenciespip install fastapi[standard] uvicorn streamlit langchain langchain-google-genai langgraph requests
3. ConfigurationOpen agent_backend.py and update the configuration section with your credentials:os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_KEY"
SMTP_USER = "YOUR_MAILTRAP_USER"
SMTP_PASS = "YOUR_MAILTRAP_PASSWORD"
🏃‍♂️ How to RunThis application requires two terminal windows running simultaneously.Terminal 1: The Backend (Database)Start the mock API server.source venv/bin/activate
fastapi dev main.py
You should see: Application startup complete.Terminal 2: The Frontend (UI)Start the Streamlit interface.source venv/bin/activate
streamlit run app.py
The application will open automatically in your browser at http://localhost:8501.🧪 Testing the WorkflowStart a Chat: The bot will greet you.Ask for Status: Type "I want to check my application status."Provide Details: The bot will ask for your ID and Email.Test ID: 102 (Status: Accepted)Test Email: candidate@test.com (or any dummy email).Confirm Email: When the bot reports success and asks to send an email, reply "Yes, please."Verify: Check your Mailtrap Inbox to see the actual email delivered.📂 Project Structure├── main.py             # FastAPI Backend (Mock Database)
├── agent_backend.py    # LangGraph Logic (Nodes, Edges, Email Tools)
├── app.py              # Streamlit Frontend (Chat UI & Debug Panel)
├── README.md           # Documentation
└── venv/               # Virtual Environment
