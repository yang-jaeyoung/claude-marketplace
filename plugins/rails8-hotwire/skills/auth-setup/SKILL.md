---
name: auth-setup
description: Rails 8 인증을 단계별로 설정하는 마법사
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
---

# Auth Setup - 인증 설정 마법사

## Options

1. **Rails 8 내장 인증** (권장) - `bin/rails generate authentication`
2. **Devise** - 풍부한 기능의 인증 라이브러리
3. **Devise + OAuth** - 소셜 로그인 통합

## Workflow

1. 인증 방식 선택
2. 사용자 모델 생성
3. 세션 관리 설정
4. 뷰 생성 (Turbo 호환)
5. 테스트 작성

## Instructions

devise-specialist 에이전트를 사용하여 사용자의 요구사항에 맞는 인증 시스템을 구현합니다.

## Example

```
/rails8-hotwire:auth-setup Rails 8 내장 인증으로 설정해주세요
/rails8-hotwire:auth-setup Devise + Google OAuth를 사용하고 싶습니다
```
