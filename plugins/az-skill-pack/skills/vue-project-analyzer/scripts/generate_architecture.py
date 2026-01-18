#!/usr/bin/env python3
"""
Vue 프로젝트 분석 후 ARCHITECTURE.md 자동 생성
Usage: python generate_architecture.py /path/to/vue-project
"""

import os
import sys
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class VueProjectAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.src_path = self.project_path / "src"
        self.analysis = {
            "meta": {},
            "structure": {},
            "routes": [],
            "components": {},
            "stores": [],
            "api_endpoints": [],
            "dependencies": {}
        }
    
    def analyze(self):
        """전체 분석 실행"""
        self._analyze_package_json()
        self._analyze_structure()
        self._analyze_routes()
        self._analyze_components()
        self._analyze_stores()
        self._analyze_api()
        return self.analysis
    
    def _analyze_package_json(self):
        """package.json에서 메타 정보 추출"""
        pkg_path = self.project_path / "package.json"
        if not pkg_path.exists():
            return
        
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        
        # Vue 버전 감지
        vue_version = deps.get("vue", "unknown")
        is_vue3 = vue_version.startswith("^3") or vue_version.startswith("3")
        
        self.analysis["meta"] = {
            "name": pkg.get("name", "unknown"),
            "vue_version": "3.x" if is_vue3 else "2.x",
            "typescript": "typescript" in deps,
            "state_management": self._detect_state_management(deps),
            "ui_framework": self._detect_ui_framework(deps),
            "build_tool": self._detect_build_tool(deps),
            "router": "vue-router" in deps
        }
        
        self.analysis["dependencies"] = {
            k: v for k, v in deps.items() 
            if not k.startswith("@types/") and not k.startswith("@vue/")
        }
    
    def _detect_state_management(self, deps):
        if "pinia" in deps:
            return "Pinia"
        if "vuex" in deps:
            return "Vuex"
        return "None"
    
    def _detect_ui_framework(self, deps):
        frameworks = {
            "vuetify": "Vuetify",
            "element-plus": "Element Plus",
            "element-ui": "Element UI",
            "quasar": "Quasar",
            "ant-design-vue": "Ant Design Vue",
            "naive-ui": "Naive UI",
            "primevue": "PrimeVue"
        }
        for key, name in frameworks.items():
            if key in deps:
                return name
        return "None"
    
    def _detect_build_tool(self, deps):
        if "vite" in deps:
            return "Vite"
        if "nuxt" in deps or "@nuxt/core" in deps:
            return "Nuxt"
        return "Webpack (Vue CLI)"
    
    def _analyze_structure(self):
        """디렉토리 구조 분석"""
        if not self.src_path.exists():
            return
        
        structure = defaultdict(list)
        vue_files = list(self.src_path.rglob("*.vue"))
        
        for f in vue_files:
            rel_path = f.relative_to(self.src_path)
            parts = rel_path.parts
            if len(parts) > 1:
                structure[parts[0]].append(str(rel_path))
        
        self.analysis["structure"] = {
            "total_vue_files": len(vue_files),
            "directories": dict(structure),
            "pattern": self._detect_architecture_pattern(structure)
        }
    
    def _detect_architecture_pattern(self, structure):
        dirs = set(structure.keys())
        if "pages" in dirs:
            return "Pages-based (File-based routing)"
        if "features" in dirs or "modules" in dirs:
            return "Feature-based (Domain-driven)"
        if "atoms" in dirs or "molecules" in dirs:
            return "Atomic Design"
        if "views" in dirs and "components" in dirs:
            return "Views/Components (Classic)"
        return "Custom"
    
    def _analyze_routes(self):
        """라우터 파일에서 라우트 추출"""
        router_files = [
            self.src_path / "router" / "index.ts",
            self.src_path / "router" / "index.js",
            self.src_path / "router.ts",
            self.src_path / "router.js"
        ]
        
        for rf in router_files:
            if rf.exists():
                content = rf.read_text(encoding="utf-8")
                # 간단한 라우트 추출 (정규식)
                paths = re.findall(r"path:\s*['\"]([^'\"]+)['\"]", content)
                names = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", content)
                self.analysis["routes"] = [
                    {"path": p, "name": n if i < len(names) else ""}
                    for i, p in enumerate(paths)
                ]
                break
    
    def _analyze_components(self):
        """컴포넌트 import 분석"""
        if not self.src_path.exists():
            return
        
        import_counts = defaultdict(int)
        
        for vue_file in self.src_path.rglob("*.vue"):
            content = vue_file.read_text(encoding="utf-8", errors="ignore")
            # import ... from '@/components/...' 패턴
            imports = re.findall(r"import\s+\w+\s+from\s+['\"]@?/?components/([^'\"]+)['\"]", content)
            for imp in imports:
                import_counts[imp] += 1
        
        # 상위 20개
        sorted_components = sorted(import_counts.items(), key=lambda x: -x[1])[:20]
        self.analysis["components"] = {
            "most_used": sorted_components,
            "total_count": len(list(self.src_path.rglob("*.vue")))
        }
    
    def _analyze_stores(self):
        """스토어 파일 목록"""
        store_patterns = [
            self.src_path / "stores",
            self.src_path / "store",
            self.src_path / "store" / "modules"
        ]
        
        stores = []
        for pattern in store_patterns:
            if pattern.exists():
                for f in pattern.rglob("*.ts"):
                    stores.append(str(f.relative_to(self.src_path)))
                for f in pattern.rglob("*.js"):
                    stores.append(str(f.relative_to(self.src_path)))
        
        self.analysis["stores"] = stores
    
    def _analyze_api(self):
        """API 호출 패턴 분석"""
        api_dirs = [
            self.src_path / "api",
            self.src_path / "services",
            self.src_path / "http"
        ]
        
        endpoints = []
        for api_dir in api_dirs:
            if api_dir.exists():
                for f in api_dir.rglob("*.ts"):
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    # axios/fetch 패턴 추출
                    urls = re.findall(r"['\"`](/api/[^'\"` ]+)['\"`]", content)
                    endpoints.extend(urls)
                for f in api_dir.rglob("*.js"):
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    urls = re.findall(r"['\"`](/api/[^'\"` ]+)['\"`]", content)
                    endpoints.extend(urls)
        
        self.analysis["api_endpoints"] = list(set(endpoints))
    
    def generate_markdown(self) -> str:
        """ARCHITECTURE.md 생성"""
        meta = self.analysis["meta"]
        struct = self.analysis["structure"]
        
        md = f"""# {meta.get('name', 'Project')} Architecture

> 자동 생성: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 개요

| 항목 | 값 |
|------|-----|
| Vue 버전 | {meta.get('vue_version', 'N/A')} |
| 빌드 도구 | {meta.get('build_tool', 'N/A')} |
| 상태관리 | {meta.get('state_management', 'N/A')} |
| UI 프레임워크 | {meta.get('ui_framework', 'N/A')} |
| TypeScript | {'✅' if meta.get('typescript') else '❌'} |
| Router | {'✅' if meta.get('router') else '❌'} |

## 프로젝트 구조

- **총 Vue 파일**: {struct.get('total_vue_files', 0)}개
- **아키텍처 패턴**: {struct.get('pattern', 'Unknown')}

### 디렉토리별 파일 수

| 디렉토리 | 파일 수 |
|----------|---------|
"""
        for dir_name, files in struct.get("directories", {}).items():
            md += f"| {dir_name}/ | {len(files)} |\n"
        
        # 라우트 섹션
        if self.analysis["routes"]:
            md += "\n## 라우트 구조\n\n"
            md += "| Path | Name |\n|------|------|\n"
            for route in self.analysis["routes"][:30]:
                md += f"| `{route['path']}` | {route['name']} |\n"
        
        # 핵심 컴포넌트
        if self.analysis["components"].get("most_used"):
            md += "\n## 핵심 컴포넌트 (사용 빈도순)\n\n"
            md += "| 컴포넌트 | Import 횟수 |\n|----------|-------------|\n"
            for comp, count in self.analysis["components"]["most_used"][:15]:
                md += f"| {comp} | {count} |\n"
        
        # 스토어
        if self.analysis["stores"]:
            md += "\n## 스토어 모듈\n\n"
            for store in self.analysis["stores"]:
                md += f"- `{store}`\n"
        
        # API 엔드포인트
        if self.analysis["api_endpoints"]:
            md += "\n## API 엔드포인트\n\n"
            for endpoint in sorted(self.analysis["api_endpoints"])[:30]:
                md += f"- `{endpoint}`\n"
        
        # 컴포넌트 계층 다이어그램
        md += """
## 컴포넌트 계층도

```mermaid
graph TD
    App[App.vue] --> Router[Vue Router]
    Router --> Views[Views/Pages]
    Views --> Components[Components]
    Components --> BaseComponents[Base/UI Components]
    Views --> Store[Store/State]
    Store --> API[API Layer]
    API --> Backend[Backend Server]
```

## 데이터 흐름

```mermaid
flowchart LR
    subgraph "Frontend"
        C[Component] -->|action| S[Store]
        S -->|state| C
        S -->|request| A[API]
    end
    subgraph "Backend"
        A -->|HTTP| B[Server]
        B -->|response| A
    end
```
"""
        
        # 주요 의존성
        md += "\n## 주요 의존성\n\n"
        important_deps = {k: v for k, v in self.analysis["dependencies"].items() 
                         if not k.startswith("eslint") and not k.startswith("@babel")}
        for dep, version in list(important_deps.items())[:20]:
            md += f"- `{dep}`: {version}\n"
        
        return md


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_architecture.py /path/to/vue-project")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(project_path, "ARCHITECTURE.md")
    
    analyzer = VueProjectAnalyzer(project_path)
    analyzer.analyze()
    
    markdown = analyzer.generate_markdown()
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"✅ ARCHITECTURE.md generated: {output_path}")
    print(f"   - Vue files: {analyzer.analysis['structure'].get('total_vue_files', 0)}")
    print(f"   - Routes: {len(analyzer.analysis['routes'])}")
    print(f"   - Stores: {len(analyzer.analysis['stores'])}")


if __name__ == "__main__":
    main()