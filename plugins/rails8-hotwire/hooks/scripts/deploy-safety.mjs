#!/usr/bin/env node
/**
 * 배포 명령 안전성 검사 훅
 * 위험한 배포 명령을 감지하고 차단합니다.
 */

const input = JSON.parse(process.argv[2] || '{}');
const command = input.command || '';

const dangerousPatterns = [
  {
    pattern: /kamal\s+app\s+exec.*rails\s+db:drop/i,
    level: 'critical',
    warning: '⛔ 프로덕션 데이터베이스 삭제 명령입니다!'
  },
  {
    pattern: /kamal\s+app\s+exec.*rails\s+db:reset/i,
    level: 'critical',
    warning: '⛔ 프로덕션 데이터베이스 리셋 명령입니다!'
  },
  {
    pattern: /kamal\s+deploy.*--skip-push/i,
    level: 'warning',
    warning: '⚠️ --skip-push는 이미지가 최신인지 확인하세요.'
  },
  {
    pattern: /kamal\s+remove/i,
    level: 'critical',
    warning: '⛔ 전체 서비스 제거 명령입니다. 정말 필요한지 확인하세요.'
  },
  {
    pattern: /RAILS_ENV=production.*db:migrate:down/i,
    level: 'critical',
    warning: '⛔ 프로덕션에서 마이그레이션 롤백은 위험합니다.'
  },
  {
    pattern: /kamal\s+app\s+exec.*console|kamal\s+app\s+exec.*c\b/i,
    level: 'warning',
    warning: '⚠️ 프로덕션 콘솔 접근입니다. 읽기 전용 작업만 수행하세요.'
  }
];

const issues = dangerousPatterns.filter(p => p.pattern.test(command));

if (issues.some(i => i.level === 'critical')) {
  console.log(JSON.stringify({
    result: 'block',
    message: issues.map(i => i.warning).join('\n') + '\n\n이 명령을 실행하려면 명시적으로 확인해주세요.'
  }));
} else if (issues.length > 0) {
  console.log(JSON.stringify({
    result: 'continue',
    message: issues.map(i => i.warning).join('\n')
  }));
} else {
  console.log(JSON.stringify({ result: 'continue' }));
}
