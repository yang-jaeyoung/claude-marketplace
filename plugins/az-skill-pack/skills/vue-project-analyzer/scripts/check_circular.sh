#!/bin/bash
# 순환 의존성 체크 (간단 버전)
# Usage: ./check_circular.sh /path/to/vue-project

PROJECT_PATH="${1:-.}"
SRC_PATH="$PROJECT_PATH/src"

echo "🔄 순환 의존성 체크"
echo "================================"
echo ""

# madge 설치 확인
if ! command -v npx &> /dev/null; then
    echo "❌ npx가 설치되어 있지 않습니다."
    exit 1
fi

# madge로 순환 의존성 체크
echo "madge 실행 중..."
cd "$PROJECT_PATH"

# madge 설치 (없으면)
if ! npx madge --version &> /dev/null; then
    echo "madge 설치 중..."
    npm install -g madge 2>/dev/null || npm install madge --save-dev
fi

# 순환 의존성 체크
echo ""
echo "📊 순환 의존성 결과:"
echo "-------------------"
npx madge --circular --extensions ts,js,vue "$SRC_PATH" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 순환 의존성이 발견되지 않았습니다."
fi

echo ""
echo "📈 의존성 그래프 생성 (선택사항):"
echo "   npx madge --image graph.svg src/"