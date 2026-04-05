import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def get_pricing_data():
    """Fetches service names and prices with Case Sensitivity matching the screenshot."""
    try:
        if not NOTION_TOKEN or not DATABASE_ID:
            return get_fallback_prices()

        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        response = requests.post(url, headers=headers)
        
        if response.status_code != 200:
            print(f"--- Notion API HTTP Error: {response.status_code} ---")
            return get_fallback_prices()

        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return get_fallback_prices()

        prices_context = "Official Quotix Price List (Live from Notion):\n"
        for page in results:
            props = page.get("properties", {})
            
            # 1. 'service' column matching (Small 's' as per screenshot)
            service_prop = props.get("service", {}).get("title", [])
            name = service_prop[0].get("plain_text") if service_prop else "Unknown Service"
            
            # 2. 'price' column matching (Small 'p' as per screenshot)
            price_prop = props.get("price", {})
            val = price_prop.get("number", 0) if price_prop.get("type") == "number" else 0
            
            # 3. 'unit' column matching (Small 'u' - optional to show 'per project')
            unit_prop = props.get("unit", {}).get("select", {})
            unit_val = unit_prop.get("name", "")
            
            prices_context += f"- {name}: Rs. {val} ({unit_val})\n"
            
        return prices_context

    except Exception as e:
        print(f"--- Notion Direct Request Error: {e} ---")
        return get_fallback_prices()

def get_fallback_prices():
    """Backup data if connection fails."""
    return """
    Official Quotix Price List (Backup):
    - Web Development: Rs. 50,000
    - logo design: Rs. 6,000
    - Maintanenace: Rs. 2,000
    """