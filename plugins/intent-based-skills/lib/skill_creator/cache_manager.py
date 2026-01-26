"""Research cache management for skill creation."""

import json
import hashlib
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Windows UTF-8 지원
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


@dataclass
class CacheMeta:
    """캐시 메타정보."""
    domain: str
    domain_hash: str
    created_at: str
    research_depth: str
    skill_name: Optional[str] = None
    expires_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "domain_hash": self.domain_hash,
            "created_at": self.created_at,
            "research_depth": self.research_depth,
            "skill_name": self.skill_name,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CacheMeta":
        return cls(
            domain=data["domain"],
            domain_hash=data["domain_hash"],
            created_at=data["created_at"],
            research_depth=data["research_depth"],
            skill_name=data.get("skill_name"),
            expires_at=data.get("expires_at"),
        )

    def is_expired(self) -> bool:
        """캐시 만료 여부 확인."""
        if not self.expires_at:
            return False
        return datetime.now() > datetime.fromisoformat(self.expires_at)


class ResearchCacheManager:
    """리서치 결과 캐시 관리자."""

    DEFAULT_CACHE_DIR = Path(".research-cache")
    DEFAULT_TTL_DAYS = 7

    def __init__(self, cache_dir: Optional[Path] = None, ttl_days: int = DEFAULT_TTL_DAYS):
        self.cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        self.ttl_days = ttl_days

    @staticmethod
    def compute_domain_hash(domain: str) -> str:
        """도메인 문자열의 해시 생성."""
        return hashlib.sha256(domain.encode()).hexdigest()[:12]

    def get_cache_path(self, domain: str) -> Path:
        """도메인에 해당하는 캐시 경로 반환."""
        domain_hash = self.compute_domain_hash(domain)
        return self.cache_dir / domain_hash

    def exists(self, domain: str) -> bool:
        """해당 도메인의 캐시 존재 여부."""
        cache_path = self.get_cache_path(domain)
        meta_path = cache_path / "meta.json"
        return cache_path.exists() and meta_path.exists()

    def is_valid(self, domain: str) -> bool:
        """캐시 유효성 확인 (존재 + 만료되지 않음)."""
        if not self.exists(domain):
            return False

        meta = self.load_meta(domain)
        if meta is None:
            return False

        return not meta.is_expired()

    def load_meta(self, domain: str) -> Optional[CacheMeta]:
        """캐시 메타정보 로드."""
        cache_path = self.get_cache_path(domain)
        meta_path = cache_path / "meta.json"

        if not meta_path.exists():
            return None

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CacheMeta.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def save_meta(self, domain: str, depth: str, skill_name: Optional[str] = None) -> CacheMeta:
        """캐시 메타정보 저장."""
        cache_path = self.get_cache_path(domain)
        cache_path.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        expires = now + timedelta(days=self.ttl_days)

        meta = CacheMeta(
            domain=domain,
            domain_hash=self.compute_domain_hash(domain),
            created_at=now.isoformat(),
            research_depth=depth,
            skill_name=skill_name,
            expires_at=expires.isoformat(),
        )

        meta_path = cache_path / "meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta.to_dict(), f, ensure_ascii=False, indent=2)

        return meta

    def get_research_data_path(self, domain: str) -> Optional[Path]:
        """리서치 데이터 파일 경로 반환."""
        cache_path = self.get_cache_path(domain)
        data_path = cache_path / "research-data.json"
        return data_path if data_path.exists() else None

    def get_research_report_path(self, domain: str) -> Optional[Path]:
        """리서치 리포트 파일 경로 반환."""
        cache_path = self.get_cache_path(domain)
        report_path = cache_path / "RESEARCH-REPORT.md"
        return report_path if report_path.exists() else None

    def get_key_insights_path(self, domain: str) -> Optional[Path]:
        """key-insights.json 파일 경로 반환."""
        cache_path = self.get_cache_path(domain)
        insights_path = cache_path / "key-insights.json"
        return insights_path if insights_path.exists() else None

    def invalidate(self, domain: str) -> bool:
        """특정 도메인 캐시 삭제."""
        cache_path = self.get_cache_path(domain)
        if cache_path.exists():
            shutil.rmtree(cache_path)
            return True
        return False

    def cleanup_expired(self) -> int:
        """만료된 캐시 정리. 삭제된 캐시 수 반환."""
        if not self.cache_dir.exists():
            return 0

        deleted_count = 0
        for cache_subdir in self.cache_dir.iterdir():
            if not cache_subdir.is_dir():
                continue

            meta_path = cache_subdir / "meta.json"
            if not meta_path.exists():
                # 메타 없는 캐시는 삭제
                shutil.rmtree(cache_subdir)
                deleted_count += 1
                continue

            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                meta = CacheMeta.from_dict(data)
                if meta.is_expired():
                    shutil.rmtree(cache_subdir)
                    deleted_count += 1
            except (json.JSONDecodeError, KeyError):
                shutil.rmtree(cache_subdir)
                deleted_count += 1

        return deleted_count

    def list_caches(self) -> list[CacheMeta]:
        """모든 캐시 목록 반환."""
        if not self.cache_dir.exists():
            return []

        caches = []
        for cache_subdir in self.cache_dir.iterdir():
            if not cache_subdir.is_dir():
                continue

            meta_path = cache_subdir / "meta.json"
            if meta_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    caches.append(CacheMeta.from_dict(data))
                except (json.JSONDecodeError, KeyError):
                    pass

        return caches

    def copy_to_skill_references(self, domain: str, skill_dir: Path) -> bool:
        """리서치 결과를 스킬의 references/ 폴더로 복사."""
        cache_path = self.get_cache_path(domain)
        if not cache_path.exists():
            return False

        references_dir = skill_dir / "references"
        references_dir.mkdir(parents=True, exist_ok=True)

        # 주요 파일 복사
        files_to_copy = [
            ("RESEARCH-REPORT.md", "RESEARCH-REPORT.md"),
            ("research-data.json", "research-data.json"),
            ("key-insights.json", "key-insights.json"),
        ]

        copied = False
        for src_name, dst_name in files_to_copy:
            src_path = cache_path / src_name
            if src_path.exists():
                shutil.copy2(src_path, references_dir / dst_name)
                copied = True

        return copied


# CLI 유틸리티 함수
def cache_cli():
    """캐시 관리 CLI."""
    manager = ResearchCacheManager()

    if len(sys.argv) < 2:
        print("Usage: python cache_manager.py <command> [args]")
        print("Commands:")
        print("  list              - List all cached research")
        print("  cleanup           - Remove expired caches")
        print("  invalidate <hash> - Remove specific cache")
        return

    command = sys.argv[1]

    if command == "list":
        caches = manager.list_caches()
        if not caches:
            print("No cached research found.")
            return

        print(f"Found {len(caches)} cached research:")
        for cache in caches:
            status = "EXPIRED" if cache.is_expired() else "VALID"
            print(f"  [{status}] {cache.domain_hash}: {cache.domain[:50]}")
            print(f"           Created: {cache.created_at}, Depth: {cache.research_depth}")

    elif command == "cleanup":
        deleted = manager.cleanup_expired()
        print(f"Removed {deleted} expired cache(s).")

    elif command == "invalidate":
        if len(sys.argv) < 3:
            print("Usage: python cache_manager.py invalidate <domain_or_hash>")
            return

        target = sys.argv[2]
        # 해시인지 도메인인지 판단
        if len(target) == 12 and all(c in "0123456789abcdef" for c in target):
            # 해시로 직접 삭제
            cache_path = manager.cache_dir / target
            if cache_path.exists():
                shutil.rmtree(cache_path)
                print(f"Removed cache: {target}")
            else:
                print(f"Cache not found: {target}")
        else:
            # 도메인으로 삭제
            if manager.invalidate(target):
                print(f"Removed cache for domain: {target}")
            else:
                print(f"Cache not found for domain: {target}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    cache_cli()
