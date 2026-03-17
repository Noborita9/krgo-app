import json
from fastapi import UploadFile
from google import genai
from pydantic import BaseModel, ValidationError

from api.database import settings

# Expected output schema for GenAI
class ReceiptItemsModel(BaseModel):
    items: list[dict[str, float]] # e.g. [{"Burger": 12.50}]

async def parse_receipt_image(file: UploadFile) -> list[dict[str, float]]:
    """
    Parses a receipt image and returns a list of items with their prices.
    Uses Google GenAI if the API key is configured.
    Falls back to dummy data if not configured or if parsing fails.
    """
    if not settings.gemini_api_key:
        print("Warning: GEMINI_API_KEY not set. Using dummy data for receipt parsing.")
        return [{"Burger": 12.50}, {"Fries": 4.00}, {"Soda": 2.50}]

    try:
        # Read file content
        image_bytes = await file.read()
        await file.seek(0) # Reset pointer
        
        client = genai.Client(api_key=settings.gemini_api_key)
        
        prompt = (
            "You are a professional receipt OCR and parsing expert. "
            "Analyze the provided receipt image and extract every individual line item. "
            "For each item, provide its name and the unit price. "
            "If there are multiple quantities of the same item (e.g., '3x Burger'), "
            "list them as separate items in the JSON array so each one can be claimed individually. "
            "Crucial Instructions: "
            "1. Only return a JSON array of objects. "
            "2. Each object must have exactly one key (the item name) and its value (the price as a float). "
            "3. Do not include currency symbols, taxes, service charges, or totals. "
            "4. If you see '3 Burgers $30', return three entries: {'Burger': 10.0}, {'Burger': 10.0}, {'Burger': 10.0}. "
            "5. Be extremely precise with names and decimal prices."
        )

        # Use gemini-1.5-flash which is much more stable for this task
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                {"mime_type": file.content_type, "data": image_bytes},
                prompt
            ],
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        # Parse the JSON response
        try:
            # Sometime the model returns a direct list, sometimes wrapped in an object
            data = json.loads(response.text)
            parsed_items = []
            if isinstance(data, list):
                 for item in data:
                     for k, v in item.items():
                         parsed_items.append({"name": str(k), "price": float(v)})
            elif isinstance(data, dict):
                 for k, v in data.items():
                     if isinstance(v, list): # if it returned {"items": [...]}
                         for item in v:
                             if isinstance(item, dict):
                                 for ik, iv in item.items():
                                     parsed_items.append({"name": str(ik), "price": float(iv)})
                     else:
                        parsed_items.append({"name": str(k), "price": float(v)})
            
            if parsed_items:
                 # Standardize to the list of dicts format expected by the caller
                 return [{item['name']: item['price']} for item in parsed_items]
                 
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from GenAI response: {response.text}")
            pass

    except Exception as e:
        print(f"Error during receipt parsing: {e}")
        pass
    
    # Fallback
    return [{"Unknown Item 1": 10.00}, {"Unknown Item 2": 15.00}]
