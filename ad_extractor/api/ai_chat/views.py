from fastapi import APIRouter, Depends
from api.ai_chat.ai_model import AIModelFactory, OpenAIAIModel
from config.config import settings

router = APIRouter()

@router.post(
        "/chat",
        description="Ask AI about specific aircraft configuration",
        tags=["Assignment"]
    )
async def chat_with_ai(prompt: str) -> dict:
    ai_model_factory = AIModelFactory(
        model_strategy=OpenAIAIModel(api_key=settings.LLM_API_KEY.get_secret_value(), base_url=settings.BASE_URL)
    )
    response = ai_model_factory.generate_response(prompt)
    return {"response": response}