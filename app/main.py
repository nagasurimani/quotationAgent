from fastapi import FastAPI, Request
from groq import Groq
import os
from dotenv import load_dotenv
import uvicorn

# FIX: Relative import (.notion_client) badulu direct import vadadam best for local running
try:
    from app.notion_client import get_pricing_data
except ImportError:
    from notion_client import get_pricing_data

load_dotenv()

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Root route - Browser lo check cheyadaniki (http://127.0.0.1:8000/)
@app.get("/")
def read_root():
    return {"status": "Quotix Backend is Live!"}

@app.post("/generate")
async def generate_proposal(request: Request):
    try:
        data = await request.json()
        user_query = data.get("text")
        
        if not user_query:
            return {"error": "No requirements provided"}
        
        # 1. Get Live Prices (Hardcoded or Notion based on your notion_client.py)
        prices = get_pricing_data()
        
        # 2. System Prompt
        system_msg = f"""
        You are the Quotix Sales Executive. 
        Use these exact prices from our database:
        {prices}
        
        Task: Create a professional, modern business proposal. 
        - Break down costs clearly.
        - Mention the total sum calculated accurately.
        - Be polite and business-oriented.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_query},
            ],
            model="llama-3.3-70b-versatile",
        )
        return {"quote": chat_completion.choices[0].message.content}
    
    except Exception as e:
        print(f"--- Backend Error: {e} ---")
        return {"error": str(e)}

# Running the app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)