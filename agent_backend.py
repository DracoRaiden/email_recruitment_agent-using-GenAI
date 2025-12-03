import os
import smtplib
import requests
import re
from typing import TypedDict, Optional, List
from email.mime.text import MIMEText
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

# --- CONFIGURATION ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyAUCmGefGpkI2Y_cLUKDPkO3OkV5lUTR38"
SMTP_USER = "cfc66d42997cee"
SMTP_PASS = "ef9bccaae045c8"
API_URL = "http://127.0.0.1:8000/applications"

# --- 1. DEFINE THE STATE ---
class AgentState(TypedDict):
    chat_history: List[str]      # Stores the conversation
    last_user_message: str       # The latest input
    user_id: Optional[int]       # Extracted ID
    recipient_email: Optional[str] # Extracted Email
    status: Optional[str]        # API Result
    awaiting_email_confirmation: bool # Logic Flag
    email_sent: bool             # Logic Flag
    final_response: str          # What the bot says back
    logs: List[str]              # Debugging

# --- 2. INITIALIZE LLM ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# --- 3. HELPER FUNCTIONS ---
def extract_info_from_text(text):
    """Simple Regex extraction to make the agent robust."""
    # Find 3 digit number for ID
    id_match = re.search(r'\b(10[0-9])\b', text) 
    # Find email address
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    
    return {
        "user_id": int(id_match.group(1)) if id_match else None,
        "email": email_match.group(0) if email_match else None
    }

# --- 4. DEFINE NODES ---

def conversation_manager_node(state: AgentState):
    """
    The Brain: Analyzes input and decides the next step.
    """
    user_msg = state['last_user_message']
    current_logs = state.get('logs', [])
    
    # 1. Try to extract info from the new message
    extracted = extract_info_from_text(user_msg)
    
    # Update state only if new info is found
    new_id = extracted['user_id'] if extracted['user_id'] else state.get('user_id')
    new_email = extracted['email'] if extracted['email'] else state.get('recipient_email')
    
    current_logs.append(f"Brain: Analyzed input. ID: {new_id}, Email: {new_email}")

    # 2. Logic Router
    
    # CASE A: We don't have ID or Email yet -> Ask for them
    if not new_id or not new_email:
        response = llm.invoke(f"The user said: '{user_msg}'. You need a User ID and Email to check application status. Ask for the missing details politely.").content
        return {
            "final_response": response, 
            "user_id": new_id, 
            "recipient_email": new_email,
            "logs": current_logs
        }

    # CASE B: We have ID/Email, but haven't checked status yet -> Go to Tool
    if new_id and new_email and not state.get('status'):
        return {
            "user_id": new_id, 
            "recipient_email": new_email, 
            "logs": current_logs + ["Transitioning to Status Lookup..."]
        }

    # CASE C: Status is known, User wants email? -> Check confirmation
    if state.get('status') and state.get('awaiting_email_confirmation'):
        # Check if user said "yes"
        is_yes = "yes" in user_msg.lower() or "sure" in user_msg.lower() or "please" in user_msg.lower()
        
        if is_yes:
            return {"logs": current_logs + ["User confirmed email. Sending..."]} # This will trigger the next edge
        else:
            return {
                "final_response": "Okay, I won't send the email. Let me know if you need anything else!", 
                "awaiting_email_confirmation": False,
                "logs": current_logs
            }

    # Default: Just chat
    response = llm.invoke(f"The user said: '{user_msg}'. Respond conversationally.").content
    return {"final_response": response, "logs": current_logs}

def status_lookup_node(state: AgentState):
    """Fetches data from FastAPI."""
    user_id = state['user_id']
    logs = state.get('logs', [])
    try:
        response = requests.get(f"{API_URL}/{user_id}")
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "Unknown")
            
            # Generate a nice message based on status
            prompt = f"The user {user_id} application status is '{status}'. Write a short, friendly response telling them the status. If accepted, congratulate them. Then, ASK if they want an official email confirmation sent to {state['recipient_email']}."
            bot_msg = llm.invoke(prompt).content
            
            logs.append(f"API Success: Status is {status}")
            
            return {
                "status": status, 
                "final_response": bot_msg,
                "awaiting_email_confirmation": True,
                "logs": logs
            }
        else:
            return {
                "status": "Error", 
                "final_response": "I couldn't find an application with that ID.", 
                "logs": logs + [f"API Error 404"]
            }
    except Exception as e:
        return {"final_response": "System Error: Cannot connect to database.", "logs": logs + [str(e)]}

def send_email_node(state: AgentState):
    """Generates and sends email via SMTP."""
    recipient = state['recipient_email']
    status = state['status']
    logs = state.get('logs', [])

    # 1. Generate Email Content
    subject_prompt = f"Write a professional email subject for job status: {status}. No lists. No newlines."
    body_prompt = f"Write a professional email body for job status: {status}."
    
    subject = llm.invoke(subject_prompt).content.replace("\n", "").strip()
    body = llm.invoke(body_prompt).content

    # 2. Send
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = "hr@giki.edu.pk"
        msg['To'] = recipient

        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail("hr@giki.edu.pk", recipient, msg.as_string())
            
        logs.append(f"Email Sent to {recipient}")
        return {
            "email_sent": True, 
            "awaiting_email_confirmation": False,
            "final_response": "I have successfully sent the email confirmation to your inbox!",
            "logs": logs
        }
    except Exception as e:
        return {
            "final_response": f"I tried to send the email but failed: {str(e)}", 
            "logs": logs + [f"SMTP Error: {str(e)}"]
        }

# --- 5. BUILD THE GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("conversation_manager", conversation_manager_node)
workflow.add_node("check_status", status_lookup_node)
workflow.add_node("send_email", send_email_node)

workflow.set_entry_point("conversation_manager")

# Conditional Logic for Edges
def route_step(state: AgentState):
    # If we just determined we need to check status (ID/Email present, Status None)
    if state.get('user_id') and state.get('recipient_email') and not state.get('status'):
        return "check_status"
    
    # If status is checked and we are waiting for confirmation
    # Note: The logic inside conversation_manager handles the "Wait for Yes" part.
    # If the manager sees "Yes", it DOES NOT return final_response, letting us flow here?
    # Actually, let's simplify: Check if we are ready to send email
    
    last_msg = state.get('last_user_message', "").lower()
    if state.get('status') and state.get('awaiting_email_confirmation') and ("yes" in last_msg or "sure" in last_msg):
        return "send_email"
        
    return END

workflow.add_conditional_edges(
    "conversation_manager",
    route_step,
    {
        "check_status": "check_status",
        "send_email": "send_email",
        END: END
    }
)

workflow.add_edge("check_status", END) # Stop to let user reply to the "Do you want email?" question
workflow.add_edge("send_email", END)

app = workflow.compile()