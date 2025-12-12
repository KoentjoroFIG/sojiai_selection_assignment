from typing import Any, Optional
from pydantic import BaseModel, Field


class MSNConstraint(BaseModel):
    min_msn: Optional[int] = Field(default=None, description="Minimum MSN (inclusive)")
    max_msn: Optional[int] = Field(default=None, description="Maximum MSN (inclusive)")
    exclude_msns: Optional[list[Any]] = Field(default=None, description="List of MSNs to exclude")
    include_msns: Optional[list[Any]] = Field(default=None, description="Specific MSN list")


class ExcludeIfModification(BaseModel):
    modification: str = Field(..., description="Modification/SB that provides exemption")
    applicable_models: Optional[list[str]] = Field(default=None, description="Models this exclusion applies to. None means all models.")


class ApplicabilityRules(BaseModel):
    aircraft_models: list[str] = Field(default_factory=list, description="List of affected aircraft models")
    msn_constraints: Optional[MSNConstraint] = Field(default=None, description="MSN range/list constraints")
    excluded_if_modifications: list[ExcludeIfModification] = Field(default_factory=list, description="Modifications that exempt aircraft. If applicable_models is None, applies to all models.")
    required_modifications: list[str] = Field(default_factory=list, description="Required fixes if affected")
    additional_conditions: Optional[str] = Field(default=None, description="Any other conditions in plain text")


class ADDocument(BaseModel):
    ad_id: str = Field(..., description="AD identifier (e.g., 'FAA-2025-23-53')")
    title: Optional[str] = Field(default=None, description="AD title/subject")
    effective_date: Optional[str] = Field(default=None, description="When AD becomes effective")
    applicability_rules: ApplicabilityRules = Field(..., description="Extracted applicability rules")
    raw_applicability_text: Optional[str] = Field(default=None, description="Original text for reference")


class AircraftConfiguration(BaseModel):
    aircraft_model: str = Field(..., description="Aircraft model (e.g., 'MD-11')")
    msn: Optional[int] = Field(default=None, description="Manufacturer Serial Number")
    modifications_applied: Optional[list[str]] = Field(default_factory=list, description="List of mods/SBs already applied")

class EvaluationKey(BaseModel):
    ad_id: str = Field(..., description="The AD evaluated against")
    is_affected: bool = Field(..., description="True if aircraft is affected by AD")
    reason: str = Field(..., description="Explanation of why affected/not affected")

class EvaluationResult(BaseModel):
    aircraft: Optional[AircraftConfiguration] = Field(default=None, description="The aircraft evaluated")
    results: list[EvaluationKey] = Field(..., description="List of evaluation results per AD")

class ValidationKey(BaseModel):
    ad_id: str = Field(..., description="The AD evaluated against")
    is_affected: Optional[bool] = Field(default=None, description="True if aircraft is affected by AD")
    expected: Optional[bool] = Field(default=None, description="Expected result for validation")
    pass_check: Optional[bool] = Field(default=None, description="True if evaluation matches expected")

class VerificationResult(BaseModel):
    aircraft: Optional[AircraftConfiguration] = Field(default=None, description="The aircraft evaluated")
    results: list[ValidationKey] = Field(..., description="List of verification results per AD")    
