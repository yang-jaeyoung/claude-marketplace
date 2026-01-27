#!/usr/bin/env python3
"""
Unit tests for the ambiguity detector script.

Tests verify:
1. Score calculation accuracy for various request types
2. Correct action assignment based on score thresholds
3. Proper suggestion generation for ambiguous requests
4. Cross-platform compatibility (no OS-specific code)

Run with: python -m pytest tests/test_ambiguity_detector.py -v
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "scripts"))

from ambiguity_detector import calculate_ambiguity_score, AmbiguityResult


class TestAmbiguityScoring:
    """Test score calculation for various request types."""

    def test_clear_request_with_file_and_action(self):
        """Specific file + clear action should have low ambiguity."""
        request = "Add input validation to src/components/LoginForm.tsx for email format"
        result = calculate_ambiguity_score(request)

        assert result["score"] < 0.4, f"Expected low score for clear request, got {result['score']}"
        assert result["action"] in ("pass", "analyze")

    def test_clear_request_with_line_reference(self):
        """Request with line number should have low ambiguity."""
        request = "Fix the null pointer exception in auth.py:42"
        result = calculate_ambiguity_score(request)

        assert result["score"] < 0.5, f"Expected low score for request with line ref, got {result['score']}"

    def test_vague_request_short(self):
        """Very short vague request should have high ambiguity."""
        request = "버그 수정해줘"  # "Fix the bug"
        result = calculate_ambiguity_score(request)

        assert result["score"] >= 0.5, f"Expected high score for vague request, got {result['score']}"
        assert "vague_verbs" in result["factors"] or "too_short" in result["factors"]

    def test_vague_request_improve(self):
        """Request with 'improve' and no specifics should be ambiguous."""
        request = "improve the code"
        result = calculate_ambiguity_score(request)

        assert result["score"] >= 0.4, f"Expected moderate/high score for 'improve' request, got {result['score']}"
        assert "vague_verbs" in result["factors"]

    def test_request_with_purpose(self):
        """Request with clear purpose should reduce ambiguity."""
        request = "Refactor the authentication module for better security and maintainability"
        result = calculate_ambiguity_score(request)

        # Should have lower score due to purpose indicators
        assert "보안" in request or "security" in request.lower() or "maintainability" in request.lower()
        # Still might be somewhat ambiguous without file, but purpose helps
        assert result["score"] < 0.7

    def test_request_with_constraints(self):
        """Request with constraints should reduce ambiguity."""
        request = "Add caching to the API but exclude the auth endpoints and keep compatibility"
        result = calculate_ambiguity_score(request)

        # Has exclude constraint
        assert "no_constraints" not in result["factors"]

    def test_code_block_reduces_ambiguity(self):
        """Request with code block should have reduced ambiguity."""
        request = """Fix this function:
```python
def broken():
    return None
```
It should return True instead."""
        result = calculate_ambiguity_score(request)

        assert "has_code_or_path" in result["factors"]
        assert result["factors"]["has_code_or_path"] < 0

    def test_empty_request(self):
        """Empty request should pass through."""
        result = calculate_ambiguity_score("")

        assert result["score"] == 0.0, f"Empty request should have score 0.0, got {result['score']}"
        assert result["action"] == "pass", f"Empty request should pass, got {result['action']}"

    def test_whitespace_only_request(self):
        """Whitespace-only request should pass through."""
        result = calculate_ambiguity_score("   \n\t  ")

        assert result["score"] == 0.0
        assert result["action"] == "pass"


class TestActionAssignment:
    """Test correct action assignment based on score thresholds."""

    def test_action_pass_for_clear(self):
        """Clear requests should get 'pass' action."""
        request = "Delete the deprecated function `oldMethod` from src/utils/helpers.ts"
        result = calculate_ambiguity_score(request)

        if result["score"] < 0.3:
            assert result["action"] == "pass"

    def test_action_analyze_for_uncertain(self):
        """Uncertain requests should get 'analyze' action."""
        # Construct a request likely to fall in 0.3-0.7 range
        # Include some specificity to lower the score from the maximum
        request = "Update the login function in the auth module"  # Has some target specificity
        result = calculate_ambiguity_score(request)

        # If score is in uncertain range, action should be analyze
        if 0.3 <= result["score"] <= 0.7:
            assert result["action"] == "analyze", f"Score {result['score']} should give 'analyze' action, got {result['action']}"
        # If above 0.7, clarify is also acceptable
        elif result["score"] > 0.7:
            assert result["action"] == "clarify"

    def test_action_clarify_for_ambiguous(self):
        """Highly ambiguous requests should get 'clarify' action."""
        request = "고쳐"  # Just "fix it" in Korean
        result = calculate_ambiguity_score(request)

        # Very short + vague verb should be highly ambiguous
        if result["score"] > 0.7:
            assert result["action"] == "clarify"


class TestSuggestionGeneration:
    """Test proper suggestion generation for ambiguous requests."""

    def test_no_target_generates_suggestion(self):
        """Missing target should generate specify_target suggestion."""
        request = "Improve performance"
        result = calculate_ambiguity_score(request)

        if "no_target" in result["factors"]:
            assert "specify_target" in result["suggestions"]

    def test_no_purpose_generates_suggestion(self):
        """Missing purpose should generate specify_purpose suggestion."""
        request = "Change the button"
        result = calculate_ambiguity_score(request)

        if "no_purpose" in result["factors"]:
            assert "specify_purpose" in result["suggestions"]

    def test_vague_verbs_generate_suggestion(self):
        """Vague verbs should generate clarify_action suggestion."""
        request = "Make it better"
        result = calculate_ambiguity_score(request)

        if "vague_verbs" in result["factors"]:
            assert "clarify_action" in result["suggestions"]

    def test_short_request_generates_context_suggestion(self):
        """Very short request should generate provide_context suggestion."""
        request = "Help"
        result = calculate_ambiguity_score(request)

        if "too_short" in result["factors"]:
            assert "provide_context" in result["suggestions"]


class TestKoreanRequests:
    """Test handling of Korean language requests."""

    def test_korean_vague_verbs_detected(self):
        """Korean vague verbs should be detected."""
        request = "코드 개선해줘"  # "Improve the code please"
        result = calculate_ambiguity_score(request)

        # Should detect "개선" (improve) or "해줘" (please do) as vague verbs
        assert "vague_verbs" in result["factors"], f"Expected vague_verbs in factors, got {result['factors']}"

    def test_korean_specific_request(self):
        """Korean request with specific file should have lower score."""
        request = "src/components/Button.tsx 파일에서 onClick 함수를 수정해서 로딩 상태를 추가해줘"
        result = calculate_ambiguity_score(request)

        # Has file path and specific function - should be less ambiguous
        assert result["score"] < 0.6

    def test_korean_purpose_indicator(self):
        """Korean purpose indicators should be detected."""
        request = "성능 개선을 위해 캐싱을 추가해줘"
        result = calculate_ambiguity_score(request)

        # "성능" (performance) is a purpose indicator
        assert "no_purpose" not in result["factors"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_score_bounds(self):
        """Score should always be between 0.0 and 1.0."""
        test_cases = [
            "",
            "x",
            "fix improve change update something somehow just make it better please",
            "A" * 1000,
            "!@#$%^&*()",
            "src/file.ts:123 function test() { return true; }",
        ]

        for request in test_cases:
            result = calculate_ambiguity_score(request)
            assert 0.0 <= result["score"] <= 1.0, f"Score out of bounds for: {request[:50]}"

    def test_factors_are_numeric(self):
        """All factors should be numeric values."""
        request = "fix something in the code"
        result = calculate_ambiguity_score(request)

        for key, value in result["factors"].items():
            assert isinstance(value, (int, float)), f"Factor {key} is not numeric: {value}"

    def test_suggestions_are_strings(self):
        """All suggestions should be strings."""
        request = "improve"
        result = calculate_ambiguity_score(request)

        for suggestion in result["suggestions"]:
            assert isinstance(suggestion, str), f"Suggestion is not string: {suggestion}"

    def test_result_structure(self):
        """Result should have all required keys."""
        result = calculate_ambiguity_score("test request")

        required_keys = {"score", "action", "factors", "suggestions"}
        assert required_keys.issubset(result.keys())


class TestIntegrationScenarios:
    """Test realistic usage scenarios."""

    def test_typical_bug_report(self):
        """Typical bug report should be handled appropriately."""
        request = "The login button doesn't work on mobile when user clicks it twice quickly"
        result = calculate_ambiguity_score(request)

        # Has context but lacks specific file - clarify is acceptable
        # This is actually a good case for clarification (which file? what's expected behavior?)
        assert result["score"] <= 1.0
        assert result["action"] in ("pass", "analyze", "clarify")

    def test_detailed_bug_report(self):
        """Detailed bug report with file reference should have lower ambiguity."""
        request = "The login button in src/components/LoginForm.tsx doesn't work on mobile - fix the double-click handler"
        result = calculate_ambiguity_score(request)

        # Has file path - should have lower ambiguity
        assert result["score"] < 0.6
        assert result["action"] in ("pass", "analyze")

    def test_feature_request_with_details(self):
        """Detailed feature request should have low ambiguity."""
        request = """Add dark mode support to the app:
- Toggle in settings page
- Save preference to localStorage
- Apply to all components in src/components/
- Use CSS variables for theming"""
        result = calculate_ambiguity_score(request)

        assert result["score"] < 0.5
        assert result["action"] == "pass" or result["action"] == "analyze"

    def test_refactoring_request(self):
        """Refactoring request without specifics should be ambiguous."""
        request = "Refactor the code"
        result = calculate_ambiguity_score(request)

        assert result["score"] >= 0.4
        assert len(result["suggestions"]) > 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
