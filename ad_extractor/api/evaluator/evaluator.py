import re
from typing import Optional
from api.schema import (
    ADDocument,
    AircraftConfiguration,
    EvaluationResult,
    EvaluationKey,
    MSNConstraint,
    ExcludeIfModification,
)


class AircraftEvaluator:    
    async def evaluate(
            self, 
            aircraft: AircraftConfiguration, 
            ad: ADDocument
    ) -> EvaluationResult:
        """
            Method to evaluate the single given aircraft configuration against the AD's applicability rules.
        """
        rules = ad.applicability_rules
        
        model_matched, model_reason = await self._check_model_match(
            aircraft.aircraft_model, 
            rules.aircraft_models
        )
        
        if not model_matched:
            return EvaluationResult(
                aircraft=aircraft,
                results=[EvaluationKey(
                    ad_id=ad.ad_id,
                    is_affected=False,
                    reason=f"Aircraft model '{aircraft.aircraft_model}' not in affected models: {rules.aircraft_models}"
                )]
            )
        
        msn_passed, msn_reason = await self._check_msn_constraints(
            aircraft.msn, 
            rules.msn_constraints
        )
        
        if not msn_passed:
            return EvaluationResult(
                aircraft=aircraft,
                results=[EvaluationKey(
                    ad_id=ad.ad_id,
                    is_affected=False,
                    reason=msn_reason
                )]
            )
        
        exempted, exemption_reason = await self._check_modification_exemptions(
            aircraft.aircraft_model,
            aircraft.modifications_applied or [],
            rules.excluded_if_modifications
        )
        
        if exempted:
            return EvaluationResult(
                aircraft=aircraft,
                results=[EvaluationKey(
                    ad_id=ad.ad_id,
                    is_affected=False,
                    reason=exemption_reason
                )]
            )
        
        return EvaluationResult(
            aircraft=aircraft,
            results=[EvaluationKey(
                ad_id=ad.ad_id,
                is_affected=True,
                reason=f"Aircraft matches affected model '{model_reason}' and meets all AD criteria"
            )]
        )
    
    async def _check_model_match(
        self, 
        aircraft_model: str, 
        affected_models: list[str]
    ) -> tuple[bool, str]:
        """
            Method to check if the aircraft model matches any of the affected models.
        """
        if not affected_models:
            return False, "No affected models specified"
        
        aircraft_upper = aircraft_model.upper()
        
        for affected in affected_models:
            affected_upper = affected.upper()
            
            if aircraft_upper == affected_upper:
                return True, affected
            
            if await self._is_model_variant(aircraft_upper, affected_upper):
                return True, affected
        
        return False, ""
    
    async def _is_model_variant(self, aircraft: str, base_model: str) -> bool:
        aircraft = aircraft.replace(" ", "").replace("-", "")
        base = base_model.replace(" ", "").replace("-", "")
        
        if aircraft.startswith(base):
            return True
        
        if base.startswith(aircraft):
            return True
            
        return False
    
    async def _check_msn_constraints(
        self, 
        msn: Optional[int], 
        constraints: Optional[MSNConstraint]
    ) -> tuple[bool, str]:
        """
            Method to check if the aircraft MSN falls within the AD's MSN constraints.
        """
        if constraints is None:
            return True, "No MSN constraints (all affected)"
        
        if msn is None:
            return True, "No MSN provided, assuming affected"
        
        if constraints.include_msns is not None and len(constraints.include_msns) > 0:
            if msn in constraints.include_msns:
                return True, f"MSN {msn} in affected list"
            return False, f"MSN {msn} not in specific affected list"
        
        if constraints.exclude_msns is not None and msn in constraints.exclude_msns:
            return False, f"MSN {msn} explicitly excluded"
        
        min_msn = constraints.min_msn
        max_msn = constraints.max_msn
        
        if min_msn is None and max_msn is None:
            return True, "No MSN range specified (all affected)"
        
        if min_msn is not None and msn < min_msn:
            return False, f"MSN {msn} outside affected range (min: {min_msn})"
        
        if max_msn is not None and msn > max_msn:
            return False, f"MSN {msn} outside affected range (max: {max_msn})"
        
        return True, f"MSN {msn} within affected range"
    
    async def _check_modification_exemptions(
        self,
        aircraft_model: str,
        applied_mods: list[str],
        excluded_if_modifications: list[ExcludeIfModification]
    ) -> tuple[bool, str]:
        if not applied_mods:
            return False, "No modifications applied"
        
        if not excluded_if_modifications:
            return False, "No exempting modifications defined"
        
        for exclusion in excluded_if_modifications:
            if not await self._exclusion_applies_to_model(exclusion, aircraft_model):
                continue
            
            for applied in applied_mods:
                if await self._fuzzy_mod_match(applied, exclusion.modification):
                    return True, f"Has exempting modification: '{applied}' matches '{exclusion.modification}'"
        
        return False, "No applicable exempting modifications found"
    
    async def _exclusion_applies_to_model(
        self,
        exclusion: ExcludeIfModification,
        aircraft_model: str
    ) -> bool:
        if not exclusion.applicable_models:
            return True
        
        for applicable_model in exclusion.applicable_models:
            match_result, _ = await self._check_model_match(aircraft_model, [applicable_model])
            if match_result:
                return True
        
        return False
    
    async def _fuzzy_mod_match(
            self, 
            applied: str, 
            exempting: str
    ) -> bool:
        """
            Method to perform fuzzy matching between applied and exempting modification names.
        """
        applied_norm = await self._normalize_mod_name(applied)
        exempting_norm = await self._normalize_mod_name(exempting)
        
        if applied_norm == exempting_norm:
            return True
        
        if exempting_norm in applied_norm:
            return True
        
        if applied_norm in exempting_norm:
            return True
        
        applied_ids = await self._extract_identifiers(applied_norm)
        exempting_ids = await self._extract_identifiers(exempting_norm)
        
        common = applied_ids & exempting_ids
        if common:
            return True
        
        return False
    
    async def _normalize_mod_name(self, name: str) -> str:
        """
            Method to normalize modification names for comparison.
        """
        normalized = name.upper()
        normalized = re.sub(r'\s*\([^)]*\)\s*', ' ', normalized)
        normalized = ' '.join(normalized.split())
        return normalized.strip()
    
    async def _extract_identifiers(self, text: str) -> set[str]:
        """
            Method to extract numeric and alphanumeric identifiers from modification names.
        """
        identifiers = set()
        
        numbers = re.findall(r'\d+', text)
        identifiers.update(numbers)
        
        codes = re.findall(r'[A-Z]+\d+', text)
        identifiers.update(codes)
        
        alphanum = re.sub(r'[^A-Z0-9]', '', text)
        if alphanum:
            identifiers.add(alphanum)
        
        return identifiers
    
    async def evaluate_against_multiple_ads(
        self,
        aircraft: AircraftConfiguration,
        ads: list[ADDocument]
    ) -> EvaluationResult:
        """
            Method to evaluate a single aircraft configuration against multiple ADs.
            Returns a single EvaluationResult with multiple EvaluationKey entries.
        """
        evaluation_keys = []
        for ad in ads:
            result = await self.evaluate(aircraft, ad)
            if result.results:
                evaluation_keys.extend(result.results)
        
        return EvaluationResult(
            aircraft=aircraft,
            results=evaluation_keys
        )
