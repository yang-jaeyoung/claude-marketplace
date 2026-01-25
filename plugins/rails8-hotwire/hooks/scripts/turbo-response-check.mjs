#!/usr/bin/env node
/**
 * Turbo 응답 검증 훅
 * Turbo Stream 응답 형식이 올바른지 확인합니다.
 */

const input = JSON.parse(process.argv[2] || '{}');
const filePath = input.file_path || '';
const content = input.content || input.new_string || '';

// Turbo Stream 템플릿인지 확인
if (!filePath.endsWith('.turbo_stream.erb')) {
  console.log(JSON.stringify({ result: 'continue' }));
  process.exit(0);
}

const issues = [];

// 필수 turbo_stream 태그 확인
if (!content.includes('turbo_stream')) {
  issues.push('turbo_stream 헬퍼가 없습니다.');
}

// 유효한 액션 확인
const validActions = ['append', 'prepend', 'replace', 'update', 'remove', 'before', 'after', 'refresh'];
const actionMatch = content.match(/turbo_stream\.(\w+)/g);

if (actionMatch) {
  actionMatch.forEach(match => {
    const action = match.replace('turbo_stream.', '');
    if (!validActions.includes(action)) {
      issues.push(`'${action}'은 유효한 Turbo Stream 액션이 아닙니다.`);
    }
  });
}

// target 확인
if (content.includes('turbo_stream.') && !content.includes('target:') && !content.includes('_tag')) {
  const needsTarget = ['append', 'prepend', 'replace', 'update', 'remove', 'before', 'after'];
  if (needsTarget.some(a => content.includes(`turbo_stream.${a}`))) {
    issues.push('target이 지정되지 않았을 수 있습니다.');
  }
}

if (issues.length > 0) {
  console.log(JSON.stringify({
    result: 'continue',
    message: `⚠️ Turbo Stream 검증:\n${issues.map(i => `  - ${i}`).join('\n')}`
  }));
} else {
  console.log(JSON.stringify({ result: 'continue' }));
}
