import os
import google.generativeai as genai

# Setup
os.environ["GOOGLE_API_KEY"] = "AIzaSyAUCmGefGpkI2Y_cLUKDPkO3OkV5lUTR38"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")