# app/services/ai_service.py
from fastapi import HTTPException
import openai
from app.config.settings import settings

class AIService:
    def __init__(self):
        openai.api_key = settings.AI_API_KEY

    async def analyze_contract(self, contract_text: str):
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"Analyze this real estate contract and summarize key points:\n{contract_text}",
                max_tokens=500
            )
            return response.choices[0].text.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    async def generate_property_description(self, property_details: dict):
        try:
            prompt = f"Generate a professional property description based on these details:\n{property_details}"
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=300
            )
            return response.choices[0].text.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI description generation failed: {str(e)}")