from pathlib import Path
from typing import Dict, Optional, Protocol

from openai import OpenAI

from api.schema import ADDocument
from api.utils import load_parsed_ads
from config.config import settings


class AIModel(Protocol):
    def generate_response(
            self, prompt: str | dict, 
            system_context: Optional[str] = None, 
            temperature: Optional[float] = None
    ) -> str:
        ...


class OpenAIAIModel:
    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def generate_response(
            self, prompt: str | dict, 
            system_context: Optional[str] = None, 
            temperature: Optional[float] = 0.2
    ) -> str:
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)        
        response = client.chat.completions.create(
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

    def generate_response(self, prompt: str | dict) -> str:
        # Placeholder for Gemini API integration
        pass


class AIModelFactory:
    def __init__(self, model_strategy: Optional[AIModel] = None, ) -> None:
        if model_strategy is None:
            raise ValueError("An AIModel strategy must be provided.")
        self._model = model_strategy

    def generate_response(
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

        ads: Dict[str, ADDocument] = load_parsed_ads(output_dir)
        for ad_id, ad in ads.items():
            system_context += f"\nAD ID:  {ad_id}\n"
            system_context += f"Title: {ad.title}\n"
            system_context += f"Effective: {ad.effective_date}\n"
            system_context += f"Applicability: {ad.raw_applicability_text}\n"
            print(ad.raw_applicability_text)
        
        system_context += """
            When users ask about aircraft:
            1. Extract aircraft model, MSN, and any modifications from their query
            2. Check the AD applicability rules
            3. Determine if the aircraft is affected
            4. Provide a clear YES/NO answer with explanation

            Be concise, accurate, and cite relevant AD rules.
        """
        return self._model.generate_response(prompt, system_context, temperature)