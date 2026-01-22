"""Base agent class for Research Orchestrator."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum
import re


class AgentStatus(Enum):
    """에이전트 실행 상태."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentResult:
    """에이전트 실행 결과."""
    status: AgentStatus
    output_files: list[Path]
    error_message: Optional[str] = None
    execution_time: int = 0  # seconds


class BaseAgent(ABC):
    """에이전트 기본 클래스.

    각 에이전트는 프롬프트 템플릿을 로드하고,
    컨텍스트로 렌더링한 후 실행합니다.
    """

    # 서브클래스에서 오버라이드
    PROMPT_TEMPLATE_FILE: str = ""

    def __init__(self, prompts_dir: Path, output_dir: Path):
        self.prompts_dir = Path(prompts_dir)
        self.output_dir = Path(output_dir)
        self._template_cache: Optional[str] = None

    def load_prompt_template(self) -> str:
        """프롬프트 템플릿 로드."""
        if self._template_cache:
            return self._template_cache

        template_path = self.prompts_dir / self.PROMPT_TEMPLATE_FILE
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        self._template_cache = template_path.read_text(encoding="utf-8")
        return self._template_cache

    def render_prompt(self, context: dict) -> str:
        """프롬프트 렌더링.

        {{VARIABLE}} 형식의 플레이스홀더를 context 값으로 치환.
        """
        template = self.load_prompt_template()

        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, list):
                value = "\n".join(f"- {item}" for item in value)
            template = template.replace(placeholder, str(value))

        return template

    @abstractmethod
    def build_context(self, **kwargs) -> dict:
        """실행 컨텍스트 구성.

        서브클래스에서 구현해야 함.
        """
        pass

    @abstractmethod
    def get_expected_outputs(self) -> list[str]:
        """예상 출력 파일 패턴 반환.

        서브클래스에서 구현해야 함.
        """
        pass

    def validate_output(self, result: dict) -> tuple[bool, list[str]]:
        """출력 검증.

        Returns:
            (valid, errors)
        """
        errors = []

        # 기본 검증: 필수 파일 존재 확인
        for pattern in self.get_expected_outputs():
            matches = list(self.output_dir.glob(pattern))
            if not matches:
                errors.append(f"Expected output not found: {pattern}")

        return len(errors) == 0, errors

    def execute(self, **kwargs) -> AgentResult:
        """에이전트 실행.

        NOTE: 실제 실행은 Claude Code의 Task 도구를 통해 이루어집니다.
        이 메서드는 프롬프트 생성 및 결과 검증을 담당합니다.
        """
        context = self.build_context(**kwargs)
        prompt = self.render_prompt(context)

        # 프롬프트 반환 (실제 실행은 오케스트레이터가 Task 도구로 수행)
        return AgentResult(
            status=AgentStatus.PENDING,
            output_files=[],
        )

    def get_prompt(self, **kwargs) -> str:
        """실행 가능한 프롬프트 생성."""
        context = self.build_context(**kwargs)
        return self.render_prompt(context)

    @staticmethod
    def sanitize_name(name: str) -> str:
        """파일명 안전 변환 (snake_case)."""
        # 공백을 언더스코어로
        name = name.replace(" ", "_")
        # 특수문자 제거
        name = re.sub(r"[^a-zA-Z0-9_가-힣]", "", name)
        # 소문자로
        name = name.lower()
        return name
