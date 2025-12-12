from pathlib import Path
from typing import Dict, Optional, Protocol

from openai import AsyncOpenAI

from api.schema import ADDocument
from api.utils import load_parsed_ads
from config.config import settings


class AIModel(Protocol):
    async def generate_response(
            self, prompt: str | dict, 
            system_context: Optional[str] = None, 
            temperature: Optional[float] = None
    ) -> str:
        ...


class OpenAIAIModel:
    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url

    async def generate_response(
            self, prompt: str | dict, 
            system_context: Optional[str] = None, 
            temperature: Optional[float] = 0.2
    ) -> str:
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        
        return response.choices[0].message.content
    
class GeminiAIModel:
    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url

    async def generate_response(self, prompt: str | dict) -> str:
        # Placeholder for Gemini API integration
        pass


class AIModelFactory:
    def __init__(self, model_strategy: Optional[AIModel] = None, ) -> None:
        if model_strategy is None:
            raise ValueError("An AIModel strategy must be provided.")
        self._model = model_strategy

    async def generate_response(
            self, prompt: str | dict, 
            temperature: Optional[float] = 0.2
    ) -> str:
        """
            Method to ask if specific aircraft configurations are affected by ADs.
        """
        system_context = f"""
            You are an expert Airworthiness Directive (AD) assistant.
            Provide accurate and concise answers based on the AD documents provided.
            Carefully reference specific ADs when answering user queries.
            Here are available ADs in the database for your reference:
        """
        base_dir = Path(__file__).parent.parent.parent.parent
        output_dir = base_dir / "output"

        ads: Dict[str, ADDocument] = await load_parsed_ads(output_dir)
        for ad_id, ad in ads.items():
            system_context += f"\nAD ID: {ad_id}\n"
            system_context += f"Title: {ad.title}\n"
            system_context += f"Effective: {ad.effective_date}\n"
            system_context += f"Affected Aircraft Models: {ad.applicability_rules.aircraft_models}\n"
            
            if ad.applicability_rules.exclude_if_modification:
                system_context += "Exclusions (aircraft NOT affected if modification applied):\n"
                for exclusion in ad.applicability_rules.exclude_if_modification:
                    system_context += f"  - Modification: {exclusion.modification}\n"
                    system_context += f"    Only excludes models: {exclusion.applicable_models}\n"
            
            if ad.applicability_rules.msn_constraints:
                msn = ad.applicability_rules.msn_constraints
                system_context += f"MSN Constraints: min={msn.min_msn}, max={msn.max_msn}, exclude={msn.exclude_msns}, include={msn.include_msns}\n"
            
            system_context += f"Raw Applicability Text: {ad.raw_applicability_text}\n"
        
        system_context += """
            When users ask about aircraft applicability:
            
            ANALYSIS STEPS (do these silently):
            1. Extract aircraft model, MSN, and modifications from the query
            2. Check if aircraft model is in the affected models list
            3. Check exclusions - a modification ONLY excludes if BOTH conditions are met:
               a) The aircraft HAS that modification, AND
               b) The aircraft MODEL is listed in that exclusion's applicable_models
            4. If modification's applicable_models doesn't include the aircraft model, NO exclusion applies
            
            ANSWER FORMAT (strict):
            - First: Show your reasoning step by step
            - Last: End with a clear conclusion: "CONCLUSION: [YES/NO], [aircraft] [does/does not] require [action] because [reason]"
            
            IMPORTANT:
            - YES = aircraft IS affected, needs inspection/modification
            - NO = aircraft is NOT affected (excluded or not applicable)
            - Your final YES/NO must match your reasoning. Re-read before answering.
        """
        return await self._model.generate_response(prompt, system_context, temperature)