import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:10]}...{api_key[-5:]}" if api_key else "API Key not found!")

# Configure Gemini
genai.configure(api_key=api_key)

# Try to generate a simple response
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello!")
    print("\n✅ SUCCESS! Gemini API is working:")
    print(response.text)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
