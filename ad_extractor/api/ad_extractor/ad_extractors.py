from openai import OpenAI
from typing import Optional, Protocol

from pydantic import BaseModel
from api.schema import ADDocument


class ADExtractor(Protocol):
    def extract_ad(self, text: str | dict, response_format: dict | ADDocument, system_context: Optional[str] = None) -> Optional[ADDocument]:
        ...

class OpenAIADExtractor:
    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url


    def extract_ad(self, prompt: str | dict, response_format: Optional[dict | BaseModel] =  ADDocument, system_context: Optional[str] = None) -> Optional[ADDocument]:
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        try:
            response_format_json = response_format.model_json_schema()
        except:
            response_format_json = response_format

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_schema", "json_schema": {"name": "ADDocument", "schema": response_format_json}},
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        ad_data = response.choices[0].message.content
        try:
            ad_document = ADDocument.model_validate_json(ad_data)
            return ad_document
        except Exception as e:
            print(f"Error parsing AD document: {e}")
            return None
        

class GeminiADExtractor:
    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def extract_ad(self, prompt: str | dict, response_format: Optional[dict | BaseModel] =  ADDocument) -> Optional[ADDocument]:
        # Placeholder for Gemini API integration
        pass
        

class ADExtractorFactory:
    def __init__(self, extractor_strategy: Optional[ADExtractor] = None) -> None:
        if extractor_strategy is None:
            raise ValueError("An ADExtractor strategy must be provided.")
        self._extractor = extractor_strategy

    def extract_ad(self, ad_text: str | dict) -> Optional[ADDocument]:
        """
            Method to extract AD information from the provided text using the specified extractor strategy.
        """
        system_context = """
            You are an expert Airworthiness Directive (AD) extraction system. 
            Your task is to accurately parse AD documents and extract structured information following strict rules.            
            Extract the applicability rules from AD text and structure them into JSON format with precision.
        """
        
        prompt = f"""
            IMPORTANT INSTRUCTIONS:
            1. Extract AD ID with issuing authority prefix (e.g., "FAA-2025-23-53", "EASA-2025-0254R1")
               - Format: [AUTHORITY]-[AD_NUMBER]
               - Look for authority in document header (FAA, EASA, TCCA, etc.)
               - Always include the authority prefix in ad_id field
            2. Extract aircraft models listed in the applicability section
            3. For MSN (Manufacturer Serial Number) constraints:
                - Look for "all manufacturer serial numbers (MSN)" or "all MSN" mentions
                - Extract min_msn and max_msn if a range is specified (e.g., "MSN 0001 to 5000")
                - Extract exclude_msns if specific serials are excluded (e.g., "except those with MSN 0055, 0066")
                - Extract include_msns if only specific serials are affected
                - If it says "all MSN" with no range, set both min and max to null
                - Becareful to not confuse MSN with other numbers like mod number, part numbers, SB numbers, etc.
            4. Extract required modifications (SBs, mods that need to be done)
            5. Extract excluded modifications (mods/SBs that exempt the aircraft if already applied)
            6. Extract any additional conditions (time limits, inspection intervals, etc.)
            
            AD Text:
            {ad_text}
        """
        return self._extractor.extract_ad(
            prompt=prompt, response_format=ADDocument, system_context=system_context
        )