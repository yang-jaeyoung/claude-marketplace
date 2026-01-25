#!/usr/bin/env node
/**
 * 테스트 작성 강제 훅
 * 코드 변경 시 해당 테스트가 있는지 확인합니다.
 */

import { existsSync } from 'fs';
import { join, basename, dirname } from 'path';

const input = JSON.parse(process.argv[2] || '{}');
const filePath = input.file_path || '';

// 테스트 파일이나 설정 파일은 무시
if (filePath.includes('spec/') || filePath.includes('test/') ||
    filePath.includes('config/') || filePath.includes('.md')) {
  console.log(JSON.stringify({ result: 'continue' }));
  process.exit(0);
}

// Rails 소스 파일인지 확인
const isRailsSource = /app\/(models|controllers|services|jobs|mailers|helpers)\/.*\.rb$/.test(filePath);

if (!isRailsSource) {
  console.log(JSON.stringify({ result: 'continue' }));
  process.exit(0);
}

// 해당 spec 파일 경로 추론
const specPath = filePath
  .replace('app/', 'spec/')
  .replace('.rb', '_spec.rb');

if (!existsSync(specPath)) {
  console.log(JSON.stringify({
    result: 'continue',
    message: `💡 테스트 알림: ${basename(filePath)}에 대한 spec이 없습니다.\n   권장 경로: ${specPath}`
  }));
} else {
  console.log(JSON.stringify({ result: 'continue' }));
}
