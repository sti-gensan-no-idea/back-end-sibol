# app/services/ai_service.py
from fastapi import HTTPException
import requests
from supabase import create_client, Client
from app.config.settings import settings

class AIService:
    def __init__(self):
        self.vllm_url = "http://localhost:8002/v1/chat/completions"
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def query_properties(self, query: str) -> str:
        """Query Supabase for properties based on input."""
        try:
            location = None
            type_ = None
            for loc in ["Sarangani", "Dadiangas", "Lagao", "Calumpang", "Bula", "Fatima", 
                        "Pioneer", "City Heights", "Baluan", "San Isidro", "Labangal", 
                        "Makar", "Tambler", "Ligaya"]:
                if loc in query: location = loc
            for t in ["VILLA", "APARTMENT", "HOUSE", "CONDO", "TOWNHOUSE"]:
                if t.lower() in query.lower(): type_ = t

            db_query = self.supabase.table("properties").select("*")
            if location: db_query = db_query.eq("location", location)
            if type_: db_query = db_query.eq("type", type_)
            response = db_query.execute()

            if response.data:
                return "\n".join([
                    f"{prop['title']} at {prop['address']}, priced at ₱{prop['price'] / 1000000:.1f}M, "
                    f"{prop['total_bed']} bed, {prop['total_bathroom']} bath, {prop['status'].lower()}"
                    for prop in response.data[:3]
                ])
            return "No matching properties found."
        except Exception as e:
            return f"Error querying properties: {str(e)}"

    async def analyze_contract(self, contract_text: str):
        """Analyze a real estate contract using the fine-tuned gpt-oss-20b model."""
        try:
            prompt = (
                "You are a real estate assistant for aTuna in General Santos City, Philippines. "
                "Analyze the following real estate contract and summarize key points in a concise, professional manner:\n"
                f"{contract_text}"
            )
            response = requests.post(
                self.vllm_url,
                json={
                    "model": "gpt-oss-20b-finetuned",
                    "messages": [
                        {"role": "system", "content": "Provide accurate, concise contract analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI contract analysis failed: {str(e)}")

    async def generate_property_description(self, property_details: dict):
        """Generate a property description using the fine-tuned gpt-oss-20b model."""
        try:
            property_info = self.query_properties(str(property_details))
            prompt = (
                "You are a real estate assistant for aTuna in General Santos City, Philippines. "
                "Generate a professional, engaging property description based on these details. "
                "Use Filipino-friendly language (e.g., 'Mabuhay!'). Include price in PHP, bedrooms, bathrooms, and key features:\n"
                f"{property_details}\nRelevant properties:\n{property_info}"
            )
            response = requests.post(
                self.vllm_url,
                json={
                    "model": "gpt-oss-20b-finetuned",
                    "messages": [
                        {"role": "system", "content": "Generate concise, engaging property descriptions."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI description generation failed: {str(e)}")