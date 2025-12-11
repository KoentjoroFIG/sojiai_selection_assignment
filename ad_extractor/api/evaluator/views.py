import json
from pathlib import Path
from typing import Any
from fastapi import APIRouter

from api.evaluator.schema import EvaluationResponse
from api.evaluator.evaluator import AircraftEvaluator
from api.evaluator.test_case import create_verification_aircraft
from api.evaluator.utils import (
    create_verification_result_dict,
    format_verification_output,
    check_all_verification_passed,
    save_evaluation_results
)
from api.schema import AircraftConfiguration, EvaluationResult
from api.utils import load_parsed_ads
from api.evaluator.test_case import create_test_aircraft

router = APIRouter()


@router.get(
        "/evaluation_test",
        description="Run test evaluation cases based on the assignment specifications.",
        tags=["Assignment"]
    )
async def evaluation_test() -> dict[str, Any]:
    base_dir = Path(__file__).parent.parent.parent.parent
    output_dir = base_dir / "output"
    
    ads = await load_parsed_ads(output_dir)
    
    evaluator = AircraftEvaluator()
    
    test_aircraft = await create_test_aircraft()
    test_results = []
    
    for aircraft in test_aircraft:
        result = await evaluator.evaluate_against_multiple_ads(
            aircraft, 
            list(ads.values())
        )
        
        test_results.append(result.model_dump())

    
    verification_aircraft = await create_verification_aircraft()
    expected_results = [
        {"FAA-2025-23-53": True, "EASA-2025-0254R1": False},
        {"FAA-2025-23-53": False, "EASA-2025-0254R1": False},
        {"FAA-2025-23-53": False, "EASA-2025-0254R1": True},
    ]
    
    verification_results = []
    
    for i, aircraft in enumerate(verification_aircraft):
        result = await evaluator.evaluate_against_multiple_ads(
            aircraft, 
            list(ads.values())
        )
        
        verification_result = await create_verification_result_dict(
            aircraft,
            result,
            expected_results[i]
        )
        verification_results.append(verification_result.model_dump())

    
    formatted_verification = await format_verification_output(verification_results)
    all_passed = await check_all_verification_passed(verification_results)
    
    response = await save_evaluation_results(
        output_dir,
        test_results,
        formatted_verification,
        all_passed
    )

    return response


@router.get(
        "/existing_evaluation_results",
        description="Get existing evaluation result docs"
    )
async def evaluation_results() -> dict[str, Any]:
    base_dir = Path(__file__).parent.parent.parent.parent
    output_dir = base_dir / "output"
    results_file = output_dir / "evaluation_results.json"
    
    if not results_file.exists():
        return {"status": "No evaluation results found"}
    with open(results_file, 'r', encoding='utf-8') as f:
        results_data = json.load(f)
    return results_data


@router.post(
        "/cases",
        description="Evaluate a list of aircraft configurations against all parsed ADs."
    )
async def evaluate_cases(aircrafts: list[AircraftConfiguration]) -> EvaluationResponse:
    base_dir = Path(__file__).parent.parent.parent.parent
    output_dir = base_dir / "output"
    
    ads = await load_parsed_ads(output_dir)
    
    if not ads:
        return EvaluationResponse(status="No parsed AD documents found")
    
    evaluator = AircraftEvaluator()
    
    all_results = []
    for aircraft in aircrafts:
        evaluation_result = await evaluator.evaluate_against_multiple_ads(
            aircraft,
            list(ads.values())
        )
        all_results.append(evaluation_result)
    
    return EvaluationResponse(status="success", evaluation_results=all_results)