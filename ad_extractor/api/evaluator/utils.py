import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from api.schema import AircraftConfiguration, EvaluationResult, ValidationKey, VerificationResult


async def create_verification_result_dict(
    aircraft: AircraftConfiguration,
    ad_evaluation_result: Optional[EvaluationResult],
    expected_results: Dict[str, bool],
) -> VerificationResult:
    """
        Create a verification result dictionary comparing evaluation results against expected results.
    """
    validation_result = []
    
    if ad_evaluation_result and ad_evaluation_result.results:
        for eval_key in ad_evaluation_result.results:
            for expected_ad, expected_result in expected_results.items():
                if eval_key.ad_id == expected_ad:
                    pass_check = eval_key.is_affected == expected_result
                    validation_result.append(
                        ValidationKey(
                            ad_id=eval_key.ad_id,
                            is_affected=eval_key.is_affected,
                            expected=expected_result,
                            pass_check=pass_check
                        )
                    )
                
    return VerificationResult(
        aircraft=aircraft,
        results=validation_result
    )


async def format_verification_output(
        verification_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
        Format the verification results for better readability.
    """
    formatted_results = []
    for result in verification_results:
        aircraft = result.get("aircraft", {})
        validation_keys = result.get("results", [])
        
        formatted_result = {
            "aircraft": {
                "model": aircraft.get("aircraft_model"),
                "msn": aircraft.get("msn"),
                "modifications": ", ".join(aircraft.get("modifications_applied", [])) if aircraft.get("modifications_applied") else "None"
            },
            "ad_results": []
        }
        
        for val_key in validation_keys:
            formatted_result["ad_results"].append({
                "ad_id": val_key.get("ad_id"),
                "affected": val_key.get("is_affected"),
                "expected": val_key.get("expected"),
                "passed": val_key.get("pass_check")
            })
        
        formatted_results.append(formatted_result)
    return formatted_results


async def check_all_verification_passed(
        verification_results: List[Dict[str, Any]]
) -> bool:
    """
        Check if all verification results have passed.
    """
    for result in verification_results:
        validation_keys = result.get("results", [])
        for val_key in validation_keys:
            if not val_key.get("pass_check", False):
                return False
    return True


async def save_evaluation_results(
    output_dir: Path,
    test_results: List[Dict[str, Any]],
    verification_results: List[Dict[str, Any]],
    all_passed: bool,
    filename: str = "evaluation_results.json"
) -> dict[str, Any]:
    """
        Save evaluation results to a JSON file.
    """
    results_output = {
        "test_aircraft_results": test_results,
        "verification_results": verification_results,
        "all_verification_passed": all_passed
    }
    
    results_file = output_dir / filename
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results_output, f, indent=2)
    
    return {
        "test_aircraft_results": test_results,
        "verification_results": verification_results,
        "all_verification_passed": all_passed
    }
