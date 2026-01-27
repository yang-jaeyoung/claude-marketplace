#!/usr/bin/env python3
"""
Shared utilities for intent analysis in the intent-based-skills plugin.

Cross-platform compatible (macOS, Linux, Windows)
"""

from typing import List, Optional, TypedDict

# Question categories for clarification
QUESTION_CATEGORIES = {
    "specify_target": {
        "ko": "어떤 파일이나 함수에 적용할까요?",
        "en": "Which file or function should this apply to?",
        "category": "target",
    },
    "specify_purpose": {
        "ko": "이 작업의 목적이나 목표는 무엇인가요?",
        "en": "What is the purpose or goal of this task?",
        "category": "purpose",
    },
    "clarify_action": {
        "ko": "구체적으로 어떤 작업을 원하시나요?",
        "en": "What specific action do you want?",
        "category": "action",
    },
    "specify_constraints": {
        "ko": "형식이나 제약 조건이 있나요?",
        "en": "Are there any format requirements or constraints?",
        "category": "constraint",
    },
    "provide_context": {
        "ko": "좀 더 상세한 맥락을 알려주시겠어요?",
        "en": "Could you provide more context?",
        "category": "context",
    },
}


class ClarificationQuestion(TypedDict):
    question: str
    category: str
    options: Optional[List[str]]


def get_clarification_questions(
    suggestions: List[str],
    language: str = "ko"
) -> List[ClarificationQuestion]:
    """
    Convert suggestion codes to human-readable clarification questions.

    Args:
        suggestions: List of suggestion codes from ambiguity detector
        language: "ko" for Korean, "en" for English

    Returns:
        List of clarification question dictionaries
    """
    questions: List[ClarificationQuestion] = []

    for suggestion in suggestions:
        if suggestion in QUESTION_CATEGORIES:
            q_data = QUESTION_CATEGORIES[suggestion]
            question_text = q_data.get(language, q_data["en"])

            questions.append({
                "question": question_text,
                "category": q_data["category"],
                "options": get_options_for_category(q_data["category"]),
            })

    return questions


def get_options_for_category(category: str) -> Optional[List[str]]:
    """Get predefined options for a question category."""
    options_map = {
        "purpose": [
            "버그 수정 / Bug fix",
            "기능 추가 / Add feature",
            "리팩토링 / Refactoring",
            "성능 개선 / Performance",
            "보안 강화 / Security",
        ],
        "constraint": [
            "성능 우선 / Performance priority",
            "가독성 우선 / Readability priority",
            "유지보수성 우선 / Maintainability priority",
            "최소 변경 / Minimal changes",
        ],
    }
    return options_map.get(category)


def detect_language(text: str) -> str:
    """
    Simple language detection based on character ranges.

    Returns "ko" for Korean, "en" for English.
    """
    korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7af' or '\u3131' <= c <= '\u318e')
    total_alpha = sum(1 for c in text if c.isalpha())

    if total_alpha == 0:
        return "en"

    korean_ratio = korean_chars / total_alpha
    return "ko" if korean_ratio > 0.3 else "en"


def format_clarification_prompt(questions: List[ClarificationQuestion]) -> str:
    """
    Format clarification questions into a user-friendly prompt.
    """
    if not questions:
        return ""

    lines = ["Before proceeding, I need some clarification:", ""]

    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q['question']}")
        if q.get("options"):
            for opt in q["options"]:
                lines.append(f"   - {opt}")
        lines.append("")

    return "\n".join(lines)
