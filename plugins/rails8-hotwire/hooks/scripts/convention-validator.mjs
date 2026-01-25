#!/usr/bin/env node
/**
 * Rails 컨벤션 검증 훅
 * 사용자 프롬프트에서 안티패턴을 감지하고 경고합니다.
 */

const input = JSON.parse(process.argv[2] || '{}');
const prompt = input.prompt || '';

const antiPatterns = [
  {
    pattern: /fat\s*controller/i,
    warning: '컨트롤러에 비즈니스 로직을 넣지 마세요. Service Object를 사용하세요.'
  },
  {
    pattern: /callback.*before_save.*after/i,
    warning: '콜백 체인이 복잡해질 수 있습니다. Service Object 고려해주세요.'
  },
  {
    pattern: /api.*json.*react/i,
    warning: 'Rails 8에서는 Hotwire를 먼저 고려하세요. JSON API가 정말 필요한지 확인해주세요.'
  },
  {
    pattern: /redis.*sidekiq/i,
    warning: 'Rails 8에서는 Solid Queue를 권장합니다. Redis 없이 작동합니다.'
  },
  {
    pattern: /select\s*\*|find_by_sql/i,
    warning: 'Raw SQL보다 ActiveRecord 쿼리 인터페이스를 권장합니다.'
  }
];

const warnings = antiPatterns
  .filter(ap => ap.pattern.test(prompt))
  .map(ap => ap.warning);

if (warnings.length > 0) {
  console.log(JSON.stringify({
    result: 'continue',
    message: `⚠️ Rails 컨벤션 알림:\n${warnings.map(w => `  - ${w}`).join('\n')}`
  }));
} else {
  console.log(JSON.stringify({ result: 'continue' }));
}
