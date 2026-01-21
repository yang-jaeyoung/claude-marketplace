# Analysis Commands Template

공통 분석 명령어 패턴입니다.

## 프로젝트 구조 분석

```bash
# 디렉토리 구조
tree -L 3 -I "node_modules|bin|obj|.git|dist|__pycache__"

# 파일 통계
find . -type f -name "*.ts" | wc -l
find . -type f -name "*.vue" | wc -l
find . -type f -name "*.cs" | wc -l
```

## 기술 스택 감지

| 파일 | 기술 |
|------|------|
| `package.json` | Node.js |
| `*.csproj` | .NET |
| `requirements.txt` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |

## 의존성 분석

```bash
# Node.js
cat package.json | jq '.dependencies, .devDependencies'

# .NET
dotnet list package

# Python
pip list
```
