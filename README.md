🤖 AI Recruitment Agent (GIKI HR Assistant)AI Recruitment Agent is a fully-featured, conversational HR Assistant built to automate candidate interactions and status checks. With a microservices architecture and stateful AI orchestration, this project simulates a complete recruitment workflow including natural language processing, database querying, and automated email dispatch. It uses advanced state management, secure API handling, and real-time UI updates to provide a seamless experience for both candidates and HR systems.🎯 Key Features🗣️ Conversational Interface: Natural language chat UI powered by Streamlit🧠 Intelligent Orchestration, including:Context-aware intent parsingAutomated extraction of User IDs and EmailsConditional logic routing (State Machine)🔌 Real-time Backend Integration using FastAPI📧 Automated Email Notifications via secure SMTP (TLS)🕵️ Glass-Box Debugging showing internal AI thought processes and logs📦 Modular Architecture: Separated into frontend, backend, and logic layers🛡️ Input Sanitization to prevent header injection and format errors🛠️ Project Structure├── main.py                   # FastAPI Backend (Mock Database & API Endpoints)├── agent_backend.py          # LangGraph Logic (Nodes, Edges, Tools, State)├── app.py                    # Streamlit Frontend (Chat UI & Debug Panel)├── README.md                 # Documentation and Setup Guide└── venv/                     # Virtual Environment dependencies)        subgraph "The Agent Brain"        Brain --> Parse[Conversation Manager]        Parse -->|Needs Status| API_Node[Status Lookup Node]        Parse -->|Confirmed| Email_Node[Email Sender Node]    end        API_Node <-->|HTTP GET| DB[FastAPI Backend]    Email_Node <-->|SMTP/TLS| Mail[Mailtrap Server]🛠️ Tech StackLanguage: Python 3.10+ (Tested on 3.13)Frontend: StreamlitBackend: FastAPI, UvicornAI Model: Google Gemini 2.5 Flash (via langchain-google-genai)Orchestration: LangGraph, LangChain CoreEmail: Python smtplib (TLS Encryption)🚀 Installation & SetupPrerequisitesPython 3.10+ installed (Recommended: Python 3.13 via Deadsnakes PPA on Linux).A Google AI Studio API Key.A Mailtrap Account (Free Tier) for safe email testing.1. Clone & Environment Setup# Clone the repository
git clone [https://github.com/your-username/ai-hr-agent.git](https://github.com/your-username/ai-hr-agent.git)
cd ai-hr-agent

# Create a virtual environment
python3 -m venv venv

# Activate the environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
2. Install Dependencies# Install the Google GenAI SDK first to avoid conflicts
pip install "google-generativeai>=0.8.3"

# Install the rest of the stack
pip install fastapi[standard] uvicorn streamlit langchain langchain-google-genai langgraph requests
3. ConfigurationOpen agent_backend.py and update the configuration section at the top with your credentials:# agent_backend.py

os.environ["GOOGLE_API_KEY"] = "AIzaSy..."  # Your Google Gemini Key
SMTP_USER = "..."                           # Your Mailtrap Username
SMTP_PASS = "..."                           # Your Mailtrap Password
🏃‍♂️ How to RunThis application requires two terminal windows running simultaneously (Microservices architecture).Terminal 1: The Backend (Database)Start the mock API server.source venv/bin/activate
fastapi dev main.py
You should see: Application startup complete.Terminal 2: The Frontend (UI)Start the Streamlit interface.source venv/bin/activate
streamlit run app.py
The application will open automatically in your browser at http://localhost:8501.🧪 Testing the WorkflowStart a Chat: The bot will greet you.Ask for Status: Type "I want to check my application status."Provide Details: The bot will ask for your ID and Email.Test ID: 102 (Status: Accepted)Test Email: candidate@test.com (or any dummy email).Confirm Email: When the bot reports success and asks to send an email, reply "Yes, please."Verify: Check your Mailtrap Inbox to see the actual email delivered.📂 Project Structure├── main.py             # FastAPI Backend (Mock Database & API Endpoints)
├── agent_backend.py    # LangGraph Logic (Nodes, Edges, Tools, State)
├── app.py              # Streamlit Frontend (Chat UI & Debug Panel)
├── README.md           # Documentation
└── venv/               # Virtual Environment dependencies
🛡️ TroubleshootingErrorSolutionConnection Error / RefusedEnsure main.py is running in a separate terminal via fastapi dev.SMTP/Auth ErrorCheck your Mailtrap credentials in agent_backend.py. Use SMTP Credentials, not the API Token.404 Model Not FoundEnsure you enabled "Generative Language API" in Google Cloud Console. Try changing model to gemini-pro.Header Parse ErrorThe agent sanitized newlines in the subject line. Ensure `agent
