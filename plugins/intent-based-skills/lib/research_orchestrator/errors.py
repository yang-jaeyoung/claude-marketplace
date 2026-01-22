"""Custom errors for Research Orchestrator."""

from typing import Optional


class OrchestratorError(Exception):
    """Base error for orchestrator."""

    def __init__(self, message: str, recoverable: bool = False):
        super().__init__(message)
        self.message = message
        self.recoverable = recoverable


class DecompositionError(OrchestratorError):
    """연구 분해 단계 오류."""

    def __init__(self, message: str, partial_result: Optional[dict] = None):
        super().__init__(message, recoverable=True)
        self.partial_result = partial_result


class ExecutionError(OrchestratorError):
    """Stage 실행 오류."""

    # Error codes
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    AGENT_FAILURE = "AGENT_FAILURE"
    OUTPUT_INVALID = "OUTPUT_INVALID"
    DEPENDENCY_FAILED = "DEPENDENCY_FAILED"

    def __init__(
        self,
        message: str,
        stage_id: int,
        error_code: str,
        recoverable: bool = True,
    ):
        super().__init__(message, recoverable=recoverable)
        self.stage_id = stage_id
        self.error_code = error_code


class ValidationError(OrchestratorError):
    """검증 오류."""

    def __init__(
        self,
        message: str,
        consistency_score: float = 0.0,
        critical_issues: Optional[list[str]] = None,
    ):
        super().__init__(message, recoverable=True)
        self.consistency_score = consistency_score
        self.critical_issues = critical_issues or []


class SynthesisError(OrchestratorError):
    """결과 통합 오류."""

    def __init__(self, message: str, partial_report: Optional[str] = None):
        super().__init__(message, recoverable=True)
        self.partial_report = partial_report


class TotalTimeoutError(OrchestratorError):
    """전체 시간 초과."""

    def __init__(self, elapsed_minutes: int, limit_minutes: int):
        message = f"Total timeout exceeded: {elapsed_minutes}min > {limit_minutes}min limit"
        super().__init__(message, recoverable=False)
        self.elapsed_minutes = elapsed_minutes
        self.limit_minutes = limit_minutes


class GuardrailViolationError(OrchestratorError):
    """가드레일 위반."""

    def __init__(self, guardrail_name: str, current_value: int, limit: int):
        message = f"Guardrail violation: {guardrail_name} = {current_value} (limit: {limit})"
        super().__init__(message, recoverable=False)
        self.guardrail_name = guardrail_name
        self.current_value = current_value
        self.limit = limit
