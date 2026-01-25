---
name: rails8-background-imports
description: CSV/Excel import jobs with validation, error handling, and progress tracking
triggers:
  - import job
  - csv import
  - excel import
  - bulk import
  - data import
  - file import
  - 임포트 작업
  - CSV 임포트
  - 엑셀 임포트
  - 대량 임포트
  - 데이터 가져오기
summary: |
  대용량 CSV/Excel 파일 임포트를 위한 백그라운드 작업 패턴을 다룹니다.
  유효성 검사, 에러 처리, 진행률 추적을 포함합니다. 벌크 데이터 처리를
  안전하고 효율적으로 수행합니다.
token_cost: low
depth_files:
  shallow:
    - SKILL.md
  standard:
    - SKILL.md
    - "*.md"
  deep:
    - "**/*.md"
---

# Import Jobs

## Overview

Background jobs for importing large CSV/Excel files with validation, error handling, and progress tracking. Handle bulk data processing safely and efficiently.

## When to Use

- User data imports
- Product catalog uploads
- Bulk customer imports
- Migration from other systems
- Third-party data integration

## Quick Start

```ruby
# Trigger import
ImportJob.perform_later(upload.id)

# Job validates, processes, and reports results
```

## Available Patterns

| Pattern | Use Case | Key Features |
|---------|----------|--------------|
| [Basic CSV Import](./basic-csv.md) | Simple CSV processing | Streaming, error tracking, email notifications |
| [Batch Import with Progress](./batch-progress.md) | Large imports with UI feedback | Progress tracking, Turbo Stream updates |
| [Import with Validation](./validation.md) | Two-phase import (validate then import) | Pre-validation, early failure, duplicate detection |
| [Excel Import](./excel.md) | Processing .xlsx files | Roo gem integration, progress tracking |
| [Import with Relationships](./relationships.md) | Complex data with associations | Transactions, nested creates, error recovery |
| [Import Error Reporting](./error-reporting.md) | Detailed failure tracking | Error CSV generation, downloadable reports |
| [Idempotent Import](./idempotent.md) | Safe retry handling | Redis-based deduplication, resume capability |

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Loading entire file | Memory exhaustion | Stream with CSV.foreach |
| No validation | Bad data in database | Validate before saving |
| Single transaction | All-or-nothing failure | Transaction per row or batch |
| No error reporting | Can't fix issues | Generate error CSV |
| No progress tracking | User has no feedback | Broadcast progress updates |

```ruby
# Bad: Loads entire file into memory
csv = CSV.read(file.path, headers: true)
csv.each { |row| process(row) }

# Good: Streams row by row
CSV.foreach(file.path, headers: true) do |row|
  process(row)
end

# Bad: Single transaction
ActiveRecord::Base.transaction do
  CSV.foreach(file.path) { |row| create_record(row) }
end

# Good: Transaction per row/batch
CSV.foreach(file.path) do |row|
  ActiveRecord::Base.transaction do
    create_record(row)
  end
end
```

## Testing Import Jobs

```ruby
# spec/jobs/import_job_spec.rb
RSpec.describe ImportJob do
  let(:upload) { create(:upload, :with_csv_file) }

  it "imports valid records" do
    expect {
      ImportJob.perform_now(upload.id)
    }.to change(Customer, :count).by(3)

    upload.reload
    expect(upload.status).to eq("completed")
    expect(upload.results["created"]).to eq(3)
  end

  it "handles invalid records" do
    upload = create(:upload, :with_invalid_csv)

    ImportJob.perform_now(upload.id)

    upload.reload
    expect(upload.results["failed"]).to be > 0
    expect(upload.results["errors"]).to be_present
  end
end
```

## Related Skills

- [solid-queue/jobs](../solid-queue/jobs.md): Background job basics
- [exports](./exports.md): CSV export jobs
- [mailers](./mailers.md): Import notification emails
- [cleanup](./cleanup.md): Cleanup old uploads

## References

- [CSV Documentation](https://ruby-doc.org/stdlib/libdoc/csv/rdoc/CSV.html)
- [Roo Gem](https://github.com/roo-rb/roo) (Excel support)
- [Active Storage](https://guides.rubyonrails.org/active_storage_overview.html)
- [Background Jobs Best Practices](https://guides.rubyonrails.org/active_job_basics.html)
