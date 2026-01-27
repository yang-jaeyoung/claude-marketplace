#!/usr/bin/env python3
"""
Ambiguity Detector for Intent-Based Skills Plugin

Analyzes user requests for ambiguity using rule-based scoring.
Output: JSON with score (0.0-1.0) and action recommendation.

Score thresholds:
- < 0.3: Clear request, pass through
- 0.3-0.7: Uncertain, needs agent analysis
- > 0.7: Ambiguous, generate clarification questions immediately

Cross-platform compatible (macOS, Linux, Windows)
"""

import io
import json
import re
import sys
from typing import Dict, List, TypedDict

# Windows UTF-8 stdin handling
if sys.platform == 'win32':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')


# Ambiguity score thresholds
THRESHOLD_CLEAR = 0.3  # Below this: clear request, pass through
THRESHOLD_AMBIGUOUS = 0.7  # Above this: very ambiguous, generate clarification questions immediately

# Scoring weights
WEIGHT_VAGUE_VERB = 0.1  # Weight per vague verb detected
WEIGHT_VAGUE_VERB_MAX = 0.3  # Maximum score from vague verbs
WEIGHT_TOO_SHORT = 0.2  # Score if request is very short (< 20 chars)
WEIGHT_SHORT = 0.1  # Score if request is somewhat short (< 40 chars)
WEIGHT_NO_TARGET = 0.2  # Score if no file/function specified
WEIGHT_NO_PURPOSE = 0.2  # Score if no purpose/reason specified
WEIGHT_NO_CONSTRAINTS = 0.1  # Score if no constraints/format specified
WEIGHT_HAS_CODE_OR_PATH = -0.2  # Negative score (reduces ambiguity) if code/path present
WEIGHT_MANY_QUESTIONS = 0.1  # Score if many question marks (> 2)

# Length thresholds for request text
LENGTH_VERY_SHORT = 20  # Characters
LENGTH_SHORT = 40  # Characters


class AmbiguityResult(TypedDict):
    score: float
    action: str  # "pass" | "analyze" | "clarify"
    factors: Dict[str, float]
    suggestions: List[str]


# Ambiguous verbs that indicate vague intent (Korean and English)
VAGUE_VERBS = {
    # Korean
    "개선", "수정", "고쳐", "바꿔", "해줘", "처리", "좀", "이것",
    "뭔가", "어떻게", "알아서", "잘", "좋게", "더", "다시",
    # English
    "fix", "improve", "update", "change", "handle", "do", "make",
    "better", "something", "somehow", "just", "quick", "simple",
}

# Words that indicate specificity (reduce ambiguity)
SPECIFIC_INDICATORS = {
    # File/code references
    "파일", "함수", "클래스", "메서드", "변수", "모듈", "컴포넌트",
    "file", "function", "class", "method", "variable", "module", "component",
    # Line numbers and paths
    "라인", "line", "줄", "행", ".py", ".ts", ".js", ".tsx", ".jsx",
    ".vue", ".svelte", ".go", ".rs", ".java", ".cs", ".cpp",
    # Specific actions
    "추가", "삭제", "생성", "이동", "복사", "리네임",
    "add", "delete", "create", "move", "copy", "rename",
}

# Purpose/goal indicators
PURPOSE_INDICATORS = {
    # Korean
    "위해", "때문에", "목적", "이유", "왜냐하면", "결과",
    "성능", "보안", "가독성", "유지보수", "테스트",
    # English
    "because", "purpose", "goal", "reason", "in order to", "so that",
    "performance", "security", "readability", "maintainability", "testing",
}

# Constraint indicators
CONSTRAINT_INDICATORS = {
    # Korean
    "제외", "포함", "반드시", "절대", "최대", "최소", "이내", "이상",
    # English
    "exclude", "include", "must", "never", "maximum", "minimum", "within", "at least",
}

# Format/output indicators
FORMAT_INDICATORS = {
    # Korean
    "형식", "포맷", "표", "목록", "코드", "설명", "요약", "상세",
    # English
    "format", "table", "list", "code", "explanation", "summary", "detailed",
}


def calculate_ambiguity_score(text: str) -> AmbiguityResult:
    """
    Calculate ambiguity score for the given text.

    Returns a score between 0.0 (very clear) and 1.0 (very ambiguous).
    """
    # Handle empty input
    if not text or not text.strip():
        return {
            "score": 0.0,
            "action": "pass",
            "factors": {},
            "suggestions": [],
        }

    text_lower = text.lower()
    words = set(re.findall(r'\w+', text_lower))

    factors: Dict[str, float] = {}

    # Factor 1: Vague verbs usage
    # For English: check word boundaries
    # For Korean: check if vague verb appears in text (substring match)
    vague_verb_count = len(words & VAGUE_VERBS)

    # Also check Korean vague verbs as substrings (Korean doesn't have word boundaries)
    korean_vague_count = sum(1 for verb in VAGUE_VERBS if verb in text_lower and len(verb) > 1)
    total_vague = max(vague_verb_count, korean_vague_count)

    if total_vague > 0:
        factors["vague_verbs"] = min(WEIGHT_VAGUE_VERB_MAX, total_vague * WEIGHT_VAGUE_VERB)

    # Factor 2: Request length too short
    char_count = len(text.strip())
    if char_count < LENGTH_VERY_SHORT:
        factors["too_short"] = WEIGHT_TOO_SHORT
    elif char_count < LENGTH_SHORT:
        factors["short"] = WEIGHT_SHORT

    # Factor 3: No file/function specification
    specific_count = len(words & SPECIFIC_INDICATORS)
    has_path_pattern = bool(re.search(r'[/\\][\w\-\.]+\.\w+', text))  # path/file.ext
    has_line_ref = bool(re.search(r':\d+', text))  # :123 line reference

    if specific_count == 0 and not has_path_pattern and not has_line_ref:
        factors["no_target"] = WEIGHT_NO_TARGET

    # Factor 4: No purpose/reason specified
    purpose_count = len(words & PURPOSE_INDICATORS)
    if purpose_count == 0:
        factors["no_purpose"] = WEIGHT_NO_PURPOSE

    # Factor 5: No constraints specified
    constraint_count = len(words & CONSTRAINT_INDICATORS)
    format_count = len(words & FORMAT_INDICATORS)
    if constraint_count == 0 and format_count == 0:
        factors["no_constraints"] = WEIGHT_NO_CONSTRAINTS

    # Negative factors (reduce ambiguity)
    # Code blocks or file paths indicate specificity
    if "```" in text or has_path_pattern:
        factors["has_code_or_path"] = WEIGHT_HAS_CODE_OR_PATH

    # Question marks might indicate exploration (slightly more ambiguous)
    if text.count("?") > 2:
        factors["many_questions"] = WEIGHT_MANY_QUESTIONS

    # Calculate total score
    total_score = sum(factors.values())
    score = max(0.0, min(1.0, total_score))

    # Determine action
    if score < THRESHOLD_CLEAR:
        action = "pass"
        suggestions = []
    elif score > THRESHOLD_AMBIGUOUS:
        action = "clarify"
        suggestions = generate_suggestions(factors)
    else:
        action = "analyze"
        suggestions = generate_suggestions(factors)

    return {
        "score": round(score, 2),
        "action": action,
        "factors": {k: round(v, 2) for k, v in factors.items()},
        "suggestions": suggestions,
    }


def generate_suggestions(factors: Dict[str, float]) -> List[str]:
    """Generate clarification suggestions based on detected factors."""
    suggestions = []

    if "no_target" in factors:
        suggestions.append("specify_target")  # Ask about file/function

    if "no_purpose" in factors:
        suggestions.append("specify_purpose")  # Ask about goal/reason

    if "vague_verbs" in factors:
        suggestions.append("clarify_action")  # Ask for specific action

    if "no_constraints" in factors:
        suggestions.append("specify_constraints")  # Ask about format/limits

    if "too_short" in factors or "short" in factors:
        suggestions.append("provide_context")  # Ask for more details

    return suggestions


def main():
    """Main entry point - reads from stdin and outputs JSON."""
    # Read input from stdin
    try:
        input_text = sys.stdin.read().strip()
    except Exception as e:
        print(f"Error reading stdin: {e}", file=sys.stderr)
        input_text = ""

    if not input_text:
        # No input, pass through
        result: AmbiguityResult = {
            "score": 0.0,
            "action": "pass",
            "factors": {},
            "suggestions": [],
        }
    else:
        result = calculate_ambiguity_score(input_text)

    # Output JSON
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
