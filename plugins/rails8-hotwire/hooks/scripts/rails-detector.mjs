#!/usr/bin/env node
/**
 * Rails 프로젝트 감지 훅
 * SessionStart 시 Rails 프로젝트 여부를 확인하고 컨텍스트를 주입합니다.
 */

import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

const cwd = process.cwd();

function detectRailsProject() {
  const indicators = [
    'Gemfile',
    'config/application.rb',
    'config/routes.rb',
    'app/controllers/application_controller.rb'
  ];

  return indicators.every(file => existsSync(join(cwd, file)));
}

function getRailsVersion() {
  try {
    const gemfileLock = readFileSync(join(cwd, 'Gemfile.lock'), 'utf8');
    const match = gemfileLock.match(/^\s+rails\s+\(([^)]+)\)/m);
    return match ? match[1] : 'unknown';
  } catch {
    return 'unknown';
  }
}

function detectStack() {
  const stack = [];
  const gemfile = existsSync(join(cwd, 'Gemfile'))
    ? readFileSync(join(cwd, 'Gemfile'), 'utf8')
    : '';

  if (gemfile.includes('turbo-rails')) stack.push('Turbo');
  if (gemfile.includes('stimulus-rails')) stack.push('Stimulus');
  if (gemfile.includes('solid_queue')) stack.push('Solid Queue');
  if (gemfile.includes('solid_cache')) stack.push('Solid Cache');
  if (gemfile.includes('solid_cable')) stack.push('Solid Cable');
  if (gemfile.includes('devise')) stack.push('Devise');
  if (gemfile.includes('pundit')) stack.push('Pundit');
  if (gemfile.includes('rspec-rails')) stack.push('RSpec');
  if (existsSync(join(cwd, 'config/deploy.yml'))) stack.push('Kamal');

  return stack;
}

if (detectRailsProject()) {
  const version = getRailsVersion();
  const stack = detectStack();

  console.log(JSON.stringify({
    result: 'continue',
    message: `Rails ${version} 프로젝트 감지됨. 스택: ${stack.join(', ') || 'vanilla'}`,
    context: {
      railsVersion: version,
      stack: stack,
      isRails8: version.startsWith('8.')
    }
  }));
} else {
  console.log(JSON.stringify({ result: 'continue' }));
}
