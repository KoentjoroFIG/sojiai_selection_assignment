from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router


def init_app():
    app = FastAPI(
        title="Airworthiness Directive Extractor and Evaluator API",
        description="API for extracting and evaluating Airworthiness Directives (ADs).",
        version="1.0.0",
        openapi_tags=[
            {
                "name": "Assignment",
                "description": "Endpoints related to the assignment tasks",
            },
            {
                "name": "AI Chat",
                "description": "Operations for AI-powered chat interactions",
            },
            {
                "name": "AD Extractor",
                "description": "Extract and parse Airworthiness Directives",
            },
            {
                "name": "Evaluator",
                "description": "Evaluate extraction accuracy and quality",
            },
        ]
    )

    app.include_router(api_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = init_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)