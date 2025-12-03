import os
import smtplib  # <--- New Import for standard email
from email.mime.text import MIMEText # <--- New Import for formatting
import requests
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

# --- CONFIGURATION ---
# 1. Google Gemini Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAUCmGefGpkI2Y_cLUKDPkO3OkV5lUTR38"

# 2. Mailtrap SMTP Credentials (PASTE YOURS HERE)
SMTP_USER = "cfc66d42997cee"
SMTP_PASS = "ef9bccaae045c8"

# --- TOOL 1: Check Application Status ---
@tool
def check_application_status(user_id: int) -> str:
    """
    Fetches the application status for a specific user ID.
    """
    try:
        response = requests.get(f"http://127.0.0.1:8000/applications/{user_id}")
        if response.status_code == 200:
            return str(response.json())
        elif response.status_code == 404:
            return "User not found."
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection failed: {e}"

# --- TOOL 2: Send Email (SECURE VERSION) ---
@tool
def send_email_notification(recipient_email: str, subject: str, body: str) -> str:
    """
    Sends an email notification using Secure SMTP (TLS).
    """
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = "system@giki.edu.pk"
        msg['To'] = recipient_email

        # CHANGED: Use Port 587 (Standard) instead of 2525
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 587) as server:
            server.ehlo()       # 1. Say Hello to the server
            server.starttls()   # 2. Upgrade connection to Secure (https)
            server.ehlo()       # 3. Say Hello again (required after starttls)
            
            server.login(SMTP_USER, SMTP_PASS) # 4. Login securely
            server.sendmail("ammarsaleem9117@gmail.com", recipient_email, msg.as_string())
            
        return "Email sent successfully!"
        
    except Exception as e:
        return f"Failed to send email: {e}"
    

# --- THE AGENT ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash") # Or "gemini-pro"
tools = [check_application_status, send_email_notification]
agent_executor = create_react_agent(llm, tools)

def run_query(query):
    print(f"\nUser: {query}")
    print("AI is thinking...")
    
    response = agent_executor.invoke({"messages": [HumanMessage(content=query)]})
    
    # --- FIX FOR MESSY OUTPUT ---
    # This cleans up the [{'type': 'text'}] mess you saw earlier
    last_message = response['messages'][-1].content
    if isinstance(last_message, list):
        print(f"AI: {last_message[0]['text']}")
    else:
        print(f"AI: {last_message}")

if __name__ == "__main__":
    run_query("Check the status for user 102. If they are accepted, send them a congratulatory email to test@example.com.")