#!/usr/bin/env python3
"""
Vue 프로젝트에서 Mermaid 다이어그램 자동 생성
Usage: python generate_diagrams.py /path/to/vue-project
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict

class DiagramGenerator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.src_path = self.project_path / "src"
    
    def generate_component_hierarchy(self) -> str:
        """컴포넌트 계층 다이어그램 생성"""
        
        # 디렉토리 구조 기반 계층 파악
        dirs = set()
        if self.src_path.exists():
            for d in self.src_path.iterdir():
                if d.is_dir() and not d.name.startswith('.'):
                    dirs.add(d.name)
        
        mermaid = "```mermaid\ngraph TD\n"
        mermaid += "    App[App.vue]\n"
        
        if "router" in dirs:
            mermaid += "    App --> Router[Router]\n"
        
        if "views" in dirs or "pages" in dirs:
            view_name = "views" if "views" in dirs else "pages"
            mermaid += f"    Router --> Views[{view_name}/]\n"
        
        if "components" in dirs:
            mermaid += "    Views --> Components[components/]\n"
        
        if "store" in dirs or "stores" in dirs:
            store_name = "stores" if "stores" in dirs else "store"
            mermaid += f"    Views --> Store[{store_name}/]\n"
        
        if "api" in dirs or "services" in dirs:
            api_name = "api" if "api" in dirs else "services"
            mermaid += f"    Store --> API[{api_name}/]\n"
        
        if "composables" in dirs or "hooks" in dirs:
            hook_name = "composables" if "composables" in dirs else "hooks"
            mermaid += f"    Views --> Composables[{hook_name}/]\n"
        
        if "utils" in dirs:
            mermaid += "    Components --> Utils[utils/]\n"
        
        mermaid += "```"
        return mermaid
    
    def generate_route_diagram(self) -> str:
        """라우트 구조 다이어그램 생성"""
        router_files = [
            self.src_path / "router" / "index.ts",
            self.src_path / "router" / "index.js",
        ]
        
        routes = []
        for rf in router_files:
            if rf.exists():
                content = rf.read_text(encoding="utf-8", errors="ignore")
                # path 추출
                paths = re.findall(r"path:\s*['\"]([^'\"]+)['\"]", content)
                routes = [p for p in paths if p and p != "/"]
                break
        
        if not routes:
            return "라우트 정보를 찾을 수 없습니다."
        
        mermaid = "```mermaid\ngraph LR\n"
        mermaid += "    Root[/]\n"
        
        # 라우트를 계층별로 그룹화
        for route in routes[:20]:  # 최대 20개
            parts = route.strip("/").split("/")
            safe_name = route.replace("/", "_").replace(":", "").replace("-", "_")
            if not safe_name:
                continue
            
            if len(parts) == 1:
                mermaid += f"    Root --> {safe_name}[{route}]\n"
            else:
                parent = parts[0].replace("-", "_").replace(":", "")
                mermaid += f"    {parent} --> {safe_name}[{route}]\n"
        
        mermaid += "```"
        return mermaid
    
    def generate_store_diagram(self) -> str:
        """스토어 구조 다이어그램 (Pinia/Vuex)"""
        
        store_paths = [
            self.src_path / "stores",
            self.src_path / "store" / "modules",
            self.src_path / "store"
        ]
        
        stores = []
        for sp in store_paths:
            if sp.exists():
                for f in sp.glob("*.ts"):
                    if f.name != "index.ts":
                        stores.append(f.stem)
                for f in sp.glob("*.js"):
                    if f.name != "index.js":
                        stores.append(f.stem)
                break
        
        if not stores:
            return "스토어 정보를 찾을 수 없습니다."
        
        mermaid = "```mermaid\ngraph TD\n"
        mermaid += "    subgraph Store\n"
        
        for store in stores[:15]:
            safe_name = store.replace("-", "_")
            mermaid += f"        {safe_name}[{store}]\n"
        
        mermaid += "    end\n"
        mermaid += "    Components --> Store\n"
        mermaid += "    Store --> API[API Layer]\n"
        mermaid += "```"
        return mermaid
    
    def generate_page_component_map(self, page_name: str = None) -> str:
        """특정 페이지의 컴포넌트 맵 생성"""
        
        views_path = self.src_path / "views"
        pages_path = self.src_path / "pages"
        
        target_path = views_path if views_path.exists() else pages_path
        if not target_path.exists():
            return "views/pages 폴더를 찾을 수 없습니다."
        
        # 첫 번째 페이지 분석 (예시)
        vue_files = list(target_path.glob("*.vue"))[:1]
        if not vue_files:
            vue_files = list(target_path.rglob("*.vue"))[:1]
        
        if not vue_files:
            return "Vue 파일을 찾을 수 없습니다."
        
        page_file = vue_files[0]
        content = page_file.read_text(encoding="utf-8", errors="ignore")
        
        # import된 컴포넌트 추출
        imports = re.findall(r"import\s+(\w+)\s+from", content)
        
        page_name = page_file.stem
        mermaid = "```mermaid\ngraph TD\n"
        mermaid += f"    subgraph \"{page_name} Page\"\n"
        mermaid += f"        {page_name}[{page_name}.vue]\n"
        
        for imp in imports[:10]:
            if imp[0].isupper():  # 컴포넌트는 대문자로 시작
                mermaid += f"        {page_name} --> {imp}[{imp}]\n"
        
        mermaid += "    end\n"
        mermaid += "```"
        return mermaid
    
    def generate_all(self) -> str:
        """모든 다이어그램 생성"""
        output = "# Vue 프로젝트 다이어그램\n\n"
        
        output += "## 1. 컴포넌트 계층 구조\n\n"
        output += self.generate_component_hierarchy()
        output += "\n\n"
        
        output += "## 2. 라우트 구조\n\n"
        output += self.generate_route_diagram()
        output += "\n\n"
        
        output += "## 3. 스토어 구조\n\n"
        output += self.generate_store_diagram()
        output += "\n\n"
        
        output += "## 4. 페이지-컴포넌트 맵 (예시)\n\n"
        output += self.generate_page_component_map()
        output += "\n"
        
        return output


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_diagrams.py /path/to/vue-project")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(project_path, "DIAGRAMS.md")
    
    generator = DiagramGenerator(project_path)
    output = generator.generate_all()
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    
    print(f"✅ DIAGRAMS.md generated: {output_path}")


if __name__ == "__main__":
    main()