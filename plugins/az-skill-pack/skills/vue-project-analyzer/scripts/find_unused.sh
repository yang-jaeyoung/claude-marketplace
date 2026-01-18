#!/bin/bash
# 미사용 컴포넌트 후보 탐지
# Usage: ./find_unused.sh /path/to/vue-project

PROJECT_PATH="${1:-.}"
SRC_PATH="$PROJECT_PATH/src"

echo "🔍 미사용 컴포넌트 후보 탐지"
echo "================================"
echo ""

# 모든 Vue 컴포넌트 파일 목록
components=$(find "$SRC_PATH/components" -name "*.vue" 2>/dev/null)

if [ -z "$components" ]; then
    echo "❌ components 폴더를 찾을 수 없습니다."
    exit 1
fi

unused_count=0

for component in $components; do
    # 컴포넌트 파일명 추출 (확장자 제외)
    filename=$(basename "$component" .vue)
    
    # 해당 컴포넌트가 다른 파일에서 import되는지 확인
    # 자기 자신은 제외
    import_count=$(grep -rl "$filename" "$SRC_PATH" --include="*.vue" --include="*.ts" --include="*.js" 2>/dev/null | grep -v "$component" | wc -l)
    
    if [ "$import_count" -eq 0 ]; then
        echo "⚠️  $component"
        ((unused_count++))
    fi
done

echo ""
echo "================================"
echo "총 미사용 후보: $unused_count 개"
echo ""
echo "⚠️  주의: 동적 import, global 등록 컴포넌트는 미감지될 수 있음"