#!/usr/bin/env node
/**
 * 마이그레이션 안전성 검사 훅
 * 위험한 마이그레이션 작업을 감지하고 경고합니다.
 */

const input = JSON.parse(process.argv[2] || '{}');
const filePath = input.file_path || '';
const content = input.content || input.new_string || '';

// 마이그레이션 파일인지 확인
if (!filePath.includes('db/migrate')) {
  console.log(JSON.stringify({ result: 'continue' }));
  process.exit(0);
}

const dangerousPatterns = [
  {
    pattern: /remove_column|drop_table/i,
    level: 'critical',
    warning: '⛔ 컬럼/테이블 삭제는 데이터 손실을 유발합니다. 프로덕션에서 주의하세요.'
  },
  {
    pattern: /change_column.*null:\s*false/i,
    level: 'warning',
    warning: '⚠️ NOT NULL 제약 추가 시 기존 NULL 값이 있으면 실패합니다.'
  },
  {
    pattern: /rename_column|rename_table/i,
    level: 'warning',
    warning: '⚠️ 이름 변경은 코드 전체 업데이트가 필요합니다. zero-downtime 배포 고려하세요.'
  },
  {
    pattern: /add_index(?!.*concurrent)/i,
    level: 'info',
    warning: '💡 대용량 테이블에서는 CONCURRENTLY 옵션을 고려하세요 (PostgreSQL).'
  },
  {
    pattern: /execute\s*["'].*DELETE|UPDATE/i,
    level: 'critical',
    warning: '⛔ 직접 SQL로 데이터 수정은 위험합니다. 배치 처리와 트랜잭션을 사용하세요.'
  }
];

const issues = dangerousPatterns.filter(p => p.pattern.test(content));

if (issues.some(i => i.level === 'critical')) {
  console.log(JSON.stringify({
    result: 'block',
    message: issues.map(i => i.warning).join('\n') + '\n\n계속하려면 명시적으로 확인해주세요.'
  }));
} else if (issues.length > 0) {
  console.log(JSON.stringify({
    result: 'continue',
    message: issues.map(i => i.warning).join('\n')
  }));
} else {
  console.log(JSON.stringify({ result: 'continue' }));
}
