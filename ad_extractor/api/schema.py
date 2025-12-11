from typing import Any, Optional
from pydantic import BaseModel, Field


class MSNConstraint(BaseModel):
    """
    Represents affected MSN (Manufacturer Serial Number) constraints.
    
    Think of it like a filter: "Only planes with serial numbers in this range"
    - min_msn: lowest serial number affected (inclusive)
    - max_msn: highest serial number affected (inclusive)
    - exclude_msns: list of MSNs to exclude
    - include_msns: explicit list of serial numbers (if range doesn't apply)
    """
    min_msn: Optional[int] = Field(default=None, description="Minimum MSN (inclusive)")
    max_msn: Optional[int] = Field(default=None, description="Maximum MSN (inclusive)")
    exclude_msns: Optional[list[Any]] = Field(default=None, description="List of MSNs to exclude")
    include_msns: Optional[list[Any]] = Field(default=None, description="Specific MSN list")


class ApplicabilityRules(BaseModel):
    """
    Core applicability rules extracted from an AD.
    
    Analogy: Like a "who this applies to" section in a recall notice.
    - aircraft_models: Which plane types? (e.g., ["MD-11", "MD-11F"])
    - msn_constraints: Which serial numbers?
    - excluded_if_modifications: "You're safe if you already have these fixes"
    - required_modifications: "You need these fixes if affected"
    """
    aircraft_models: list[str] = Field(default_factory=list, description="List of affected aircraft models")
    msn_constraints: Optional[MSNConstraint] = Field(default=None, description="MSN range/list constraints")
    excluded_if_modifications: list[str] = Field(default_factory=list, description="Modifications that exempt aircraft")
    required_modifications: list[str] = Field(default_factory=list, description="Required fixes if affected")
    additional_conditions: Optional[str] = Field(default=None, description="Any other conditions in plain text")


class ADDocument(BaseModel):
    """
    Complete parsed AD document with metadata and rules.
    
    This is the main output of our extraction pipeline.
    """
    ad_id: str = Field(..., description="AD identifier (e.g., 'FAA-2025-23-53')")
    title: Optional[str] = Field(default=None, description="AD title/subject")
    effective_date: Optional[str] = Field(default=None, description="When AD becomes effective")
    applicability_rules: ApplicabilityRules = Field(..., description="Extracted applicability rules")
    raw_applicability_text: Optional[str] = Field(default=None, description="Original text for reference")


class AircraftConfiguration(BaseModel):
    """
    Represents a specific aircraft to evaluate against ADs.
    
    Like a "patient record" - we check if this specific plane needs the "treatment" (AD).
    """
    aircraft_model: str = Field(..., description="Aircraft model (e.g., 'MD-11')")
    msn: Optional[int] = Field(default=None, description="Manufacturer Serial Number")
    modifications_applied: Optional[list[str]] = Field(default_factory=list, description="List of mods/SBs already applied")

class EvaluationKey(BaseModel):
    ad_id: str = Field(..., description="The AD evaluated against")
    is_affected: bool = Field(..., description="True if aircraft is affected by AD")
    reason: str = Field(..., description="Explanation of why affected/not affected")

class EvaluationResult(BaseModel):
    """
    Result of evaluating one aircraft against one AD.
    
    The final verdict: Is this plane affected by this AD?
    """
    aircraft: Optional[AircraftConfiguration] = Field(default=None, description="The aircraft evaluated")
    results: list[EvaluationKey] = Field(..., description="List of evaluation results per AD")

class ValidationKey(BaseModel):
    ad_id: str = Field(..., description="The AD evaluated against")
    is_affected: Optional[bool] = Field(default=None, description="True if aircraft is affected by AD")
    expected: Optional[bool] = Field(default=None, description="Expected result for validation")
    pass_check: Optional[bool] = Field(default=None, description="True if evaluation matches expected")

class VerificationResult(BaseModel):
    """
    Result of verifying evaluation results against expected outcomes.
    
    Like a "test report card" for our evaluator.
    """
    aircraft: Optional[AircraftConfiguration] = Field(default=None, description="The aircraft evaluated")
    results: list[ValidationKey] = Field(..., description="List of verification results per AD")    
