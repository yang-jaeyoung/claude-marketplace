# Static Scraping Strategy

Comprehensive guide for scraping server-rendered, static HTML content from Korean financial sites.

## Table of Contents

1. [When to Use](#when-to-use)
2. [Detection Criteria](#detection-criteria)
3. [Workflow](#workflow)
4. [Common Patterns](#common-patterns)
5. [Selector Priority](#selector-priority)
6. [Error Handling](#error-handling)
7. [Optimization Tips](#optimization-tips)
8. [Output Format](#output-format)
9. [Fallback to Dynamic](#fallback-to-dynamic)
10. [Korean Financial Examples](#korean-financial-examples)

---

## When to Use

Static scraping is optimal for:

- **Server-rendered HTML** - Content present in initial page load
- **No JavaScript execution required** - No dynamic content loading
- **High performance needs** - Fastest extraction method (10-50ms)
- **Stability required** - No timing issues or race conditions
- **Korean financial disclosures** - DART, KRX, Naver Finance listings
- **Archived/historical data** - Financial reports, SEC filings
- **High-volume extraction** - Thousands of records per session
- **No login/authentication** - Public pages, no session-dependent content

**Estimated Coverage: 70-80% of Korean financial sites**

---

## Detection Criteria

### [STATIC_CANDIDATE] Rules

Before attempting dynamic scraping, check these criteria:

```
1. INITIAL_RENDER_CHECK
   ✓ PASS: Content visible in snapshot without delay
   ✗ FAIL: Content only appears after wait() calls

2. NO_JAVASCRIPT_FRAMEWORK
   ✓ PASS: No React/Vue/Angular data attributes
   ✓ PASS: <script> tags are analytics/GA only
   ✗ FAIL: <script> contains main app logic

3. STABLE_SELECTORS
   ✓ PASS: data-* attributes are semantic and consistent
   ✓ PASS: Semantic HTML5 tags (table, nav, section)
   ✗ FAIL: Selectors use only div[id="abc123"] (obfuscated)

4. NO_INFINITE_SCROLL
   ✓ PASS: Fixed list, pagination with <a href>
   ✗ FAIL: "scroll to load more" behavior

5. NO_AJAX_PAGINATION
   ✓ PASS: Pagination via URL parameters (?page=2)
   ✓ PASS: Server-side rendered page links
   ✗ FAIL: Pagination via AJAX/XHR requests

6. STATIC_DATA_STRUCTURE
   ✓ PASS: HTML structure consistent across pages
   ✓ PASS: Data follows repeating pattern (tables, lists)
   ✗ FAIL: Dynamic layout based on user actions

7. NO_REQUIRED_TIMING
   ✓ PASS: All content available immediately
   ✗ FAIL: Data appears after 500ms+ delay
```

**Scoring:**
- 6-7 PASS → **STATIC_OPTIMAL** - Use static scraping
- 4-5 PASS → **STATIC_VIABLE** - Try static first, fallback to dynamic
- 0-3 PASS → **DYNAMIC_REQUIRED** - Skip static, use dynamic strategy

---

## Workflow

Static scraping follows a linear, predictable 5-step process:

### Step 1: Navigate

```typescript
// Navigate to target URL
await page.navigate(url, {
  timeout: 5000,        // Korean sites often slow
  waitUntil: 'load'     // Wait for all resources
})

// Common Korean site delays:
// - Naver Finance: 2-3s
// - DART: 1-2s
// - KRX: 2-4s
```

**Key considerations:**
- Use `waitUntil: 'load'` (not 'networkidle2' - too aggressive)
- Set 5-10s timeout for Korean sites (higher latency)
- Handle redirects (Korean finance sites often redirect)

---

### Step 2: Snapshot

```typescript
// Take accessibility snapshot
const snapshot = await page.snapshot()

// Snapshot includes:
// - All visible HTML elements
// - Element refs for targeting
// - Accessibility tree (semantics)
```

**Why snapshot?**
- Captures current DOM state
- Provides element refs for selectors
- Shows structure without screenshot overhead
- ~100ms operation

**When NOT to snapshot:**
- Page hasn't finished rendering (do navigate again)
- Waiting for async content (not static scenario)

---

### Step 3: Analyze

```typescript
// Analyze snapshot structure
// Identify:
// - Root container (table, list, card layout)
// - Row/item pattern (TR, DIV.row, LI)
// - Data cells (TD, DIV.value, SPAN.price)
// - Headers (TH, DIV.header, LABEL)

// Example Naver Finance table:
// <table class="type_2">
//   <thead>
//     <tr><th>종목명</th><th>현재가</th>...</tr>
//   </thead>
//   <tbody>
//     <tr data-code="005930">
//       <td class="title">삼성전자</td>
//       <td class="number">75,000</td>
//     </tr>
//   </tbody>
// </table>
```

**Key observations:**
- Semantic HTML5 elements present
- Consistent class patterns
- data-* attributes for identification
- No dynamic event listeners needed

---

### Step 4: Extract

```typescript
// Use read_page with specific depth
const content = await page.read_page({
  depth: 5,
  filter: 'all'
})

// Parse extracted content:
// 1. Identify table/list root via CSS selector
// 2. Iterate rows/items
// 3. Extract cells using column order
// 4. Clean and normalize values

// Static extraction (no JavaScript):
// - Direct CSS selector targeting
// - No dynamic calculations
// - No waiting for renders
```

**Performance:**
- Extraction time: 10-50ms per 1000 items
- Memory usage: Minimal (streaming parse)
- Predictable latency

---

### Step 5: Validate

```typescript
// Validate extracted data:
// 1. Type checking (numbers, dates, currencies)
// 2. Range checking (prices > 0, dates in range)
// 3. Completeness (required fields present)
// 4. Consistency (column counts match header)

// Example validation for financial data:
if (!row.price || isNaN(parseFloat(row.price))) {
  throw new ValidationError('Invalid price: ' + row.price)
}
if (row.date && !isValidKoreanDate(row.date)) {
  throw new ValidationError('Invalid date format: ' + row.date)
}
```

**Validation rules:**
- Fail fast on first error row
- Report row number + value
- Attempt recovery (clean formatting) before reject

---

## Common Patterns

### Pattern 1: Korean Financial Tables (Naver, KRX)

**Identifier:** `<table class="type_2">` or `<table class="tbl_data">`

```html
<table class="type_2" summary="주식 시세 정보">
  <thead>
    <tr>
      <th scope="col">종목명</th>
      <th scope="col">현재가</th>
      <th scope="col">전일대비</th>
      <th scope="col">등락률</th>
    </tr>
  </thead>
  <tbody>
    <tr data-code="005930">
      <td class="title"><a href="/stock/?symbol=005930">삼성전자</a></td>
      <td class="number">75,000</td>
      <td class="down"><em>-500</em></td>
      <td class="rate">-0.66%</td>
    </tr>
    <tr data-code="000660">
      <td class="title"><a href="/stock/?symbol=000660">SK하이닉스</a></td>
      <td class="number">180,000</td>
      <td class="up"><em>+1,500</em></td>
      <td class="rate">+0.84%</td>
    </tr>
  </tbody>
</table>
```

**Extraction pattern:**

```typescript
// Get table root
const table = page.find('table.type_2')

// Extract headers
const headers = Array.from(table.find('thead th')).map(th => {
  return th.textContent.trim()
})
// Result: ['종목명', '현재가', '전일대비', '등락률']

// Extract rows
const rows = Array.from(table.find('tbody tr')).map(tr => {
  const cells = tr.querySelectorAll('td')
  return {
    code: tr.dataset.code,
    name: cells[0].textContent.trim(),
    price: parseFloat(cells[1].textContent.replace(/,/g, '')),
    change: parseFloat(cells[2].textContent.replace(/,/g, '')),
    changeRate: parseFloat(cells[3].textContent)
  }
})
```

**Challenges:**
- Korean number formatting: `1,234,567` (comma separators)
- Decimal separators: percentage uses `.` (예: -0.66%)
- Encoded HTML entities: `&lt;`, `&amp;`, `&quot;`
- Font rendering issues: Price display via web fonts

**Solutions:**
- Always trim() and replace(/,/g, '')
- Decode HTML entities before parsing
- Handle span color codes (색상 span, class="up"/"down")

---

### Pattern 2: DART Disclosure List

**Identifier:** DART site uses class-based layout (`class="rst_tbl"`)

```html
<table class="rst_tbl">
  <caption>전자공시시스템 상세 공시내용</caption>
  <colgroup>
    <col style="width:15%">
    <col style="width:40%">
    <col style="width:15%">
    <col style="width:15%">
    <col style="width:15%">
  </colgroup>
  <thead>
    <tr>
      <th scope="col">공시대상회사</th>
      <th scope="col">공시명</th>
      <th scope="col">접수일자</th>
      <th scope="col">공시일자</th>
      <th scope="col">조회</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="left">삼성전자</td>
      <td class="left"><a href="/dsaf001/view.do?docno=20240115001234">사업보고서</a></td>
      <td class="center">2024.01.15</td>
      <td class="center">2024.01.15</td>
      <td class="center"><a href="/view">View</a></td>
    </tr>
  </tbody>
</table>
```

**Extraction pattern:**

```typescript
const rows = Array.from(page.find('table.rst_tbl tbody tr')).map(tr => {
  const cells = tr.querySelectorAll('td')
  const titleLink = cells[1].querySelector('a')

  return {
    company: cells[0].textContent.trim(),
    title: titleLink?.textContent.trim(),
    docLink: titleLink?.href,
    reportDate: parseKoreanDate(cells[2].textContent),
    disclosureDate: parseKoreanDate(cells[3].textContent)
  }
})

function parseKoreanDate(dateStr) {
  // "2024.01.15" -> Date object
  const [year, month, day] = dateStr.split('.')
  return new Date(year, month - 1, day)
}
```

**Challenges:**
- Multiple date formats: YYYY.MM.DD, YYYY-MM-DD, YYYYMMDD
- Links contain document IDs (필요한 정보)
- Pagination: Page numbers in URL params (?page=2)

**Solutions:**
- Normalize date format using regex + Date parsing
- Extract href attributes for document access
- Loop through pagination URLs

---

### Pattern 3: KRX Data Cards/Lists

**Identifier:** Modernized KRX uses div-based layout with semantic HTML

```html
<div class="result-data">
  <div class="item" data-id="005930">
    <h3 class="item-title">삼성전자 (005930)</h3>
    <dl class="item-meta">
      <dt>상장일</dt>
      <dd>1975.06.11</dd>
      <dt>업종</dt>
      <dd>전기전자</dd>
      <dt>시가총액</dt>
      <dd>2,850,000백만원</dd>
    </dl>
    <div class="item-price">
      <span class="label">현재가</span>
      <strong class="value">75,000</strong>
      <span class="currency">원</span>
    </div>
  </div>
</div>
```

**Extraction pattern:**

```typescript
const rows = Array.from(page.find('div.result-data .item')).map(item => {
  const meta = {}

  // Extract dl (definition list) pairs
  Array.from(item.querySelectorAll('dl.item-meta'))
    .forEach(dl => {
      const dts = dl.querySelectorAll('dt')
      const dds = dl.querySelectorAll('dd')
      dts.forEach((dt, idx) => {
        meta[dt.textContent.trim()] = dds[idx].textContent.trim()
      })
    })

  return {
    id: item.dataset.id,
    name: item.querySelector('.item-title').textContent.trim(),
    listingDate: parseKoreanDate(meta['상장일']),
    sector: meta['업종'],
    marketCap: meta['시가총액'],
    price: parseFloat(
      item.querySelector('.item-price .value').textContent.replace(/,/g, '')
    )
  }
})
```

**Challenges:**
- Mixed data-* attributes and semantic HTML
- dl/dt/dd structure requires paired parsing
- Multiple nested levels

**Solutions:**
- Build metadata object from dt/dd pairs
- Use data-* attributes for IDs
- Handle nested divs carefully

---

## Selector Priority

Use this priority order when choosing selectors:

### Priority 1: Data Attributes (HIGHEST CONFIDENCE)

```typescript
// Use if available
const row = page.find('tr[data-code="005930"]')
const item = page.find('div[data-id="stock_001"]')
const cell = page.find('td[data-field="price"]')
```

**Why:** Explicitly designed for data extraction, stable across updates

**Example - Naver Finance:**
```html
<tr data-code="005930" data-key="stocks_005930">
```

---

### Priority 2: Semantic HTML5 Tags (HIGH CONFIDENCE)

```typescript
// Use if data-* not available
const table = page.find('table[summary*="주식"]')
const headers = page.findAll('table thead th')
const rows = page.findAll('table tbody tr')
const cells = page.findAll('td, th')
```

**Why:** Built for parsing, accessible, semantic meaning

**Example - DART disclosure:**
```html
<table class="rst_tbl" scope="col">
  <thead>
    <tr><th scope="col">공시명</th></tr>
  </thead>
</table>
```

---

### Priority 3: Class-based Selectors (MEDIUM CONFIDENCE)

```typescript
// Use consistent, financial-domain class patterns
const row = page.find('div.list-item')
const price = page.find('span.price, span.stock-price')
const change = page.find('span.change, span.change-up, span.change-down')
```

**Why:** Class names often persistent across design updates

**Example - KRX modern layout:**
```html
<div class="result-data">
  <div class="item">
    <div class="item-price">
      <strong class="value">75,000</strong>
    </div>
  </div>
</div>
```

---

### Priority 4: ARIA Attributes (MEDIUM CONFIDENCE)

```typescript
// Use if semantic meaning important
const data = page.find('[role="grid"]')
const cells = page.findAll('[role="gridcell"]')
const headers = page.findAll('[role="columnheader"]')
```

**Why:** Accessibility markup indicates structure intent

**Example:**
```html
<div role="grid">
  <div role="row">
    <div role="columnheader">종목명</div>
    <div role="gridcell">삼성전자</div>
  </div>
</div>
```

---

### Priority 5: Combination Selectors (LOW CONFIDENCE)

```typescript
// Use only as fallback
const row = page.find('table tr:nth-child(n+2)') // skip header
const price = page.find('tr > td:nth-child(2)')   // 2nd column
const link = page.find('a[href*="/stock/"]')       // href pattern
```

**Why:** Fragile, breaks easily with layout changes

**Avoid entirely:**
```typescript
// DON'T USE - Too specific, brittle
const price = page.find('body > div > div > table > tr > td')
const cell = page.find('div.unknown_class_xyz')
```

---

### Priority 6: Text Content Match (LAST RESORT)

```typescript
// Use only when no other option
const priceCell = Array.from(page.findAll('td'))
  .find(td => td.textContent.includes('현재가'))?.nextElementSibling

// Extract by position relative to known text
const name = page.find('*:contains("삼성전자")')
```

**Why:** Fragile, language/content dependent

---

## Error Handling

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| **Table not found** | Selector doesn't match HTML structure | Run snapshot, re-analyze HTML, verify selector |
| **Empty rows extracted** | Row selector matches but cells are empty | Check for lazy-loaded content, add dynamic fallback |
| **Garbled Korean text** | Encoding issue or font rendering | Ensure UTF-8 encoding, decode HTML entities |
| **Missing columns** | Column count mismatch | Verify headers, count actual cells, handle colspan |
| **Parse errors on numbers** | Korean formatting (1,234,567) | Always use replace(/,/g, '') before parseFloat |
| **Date format inconsistent** | Mixed formats (YYYY.MM.DD vs YYYYMMDD) | Use normalization function with regex |
| **Stale references** | DOM changed between snapshot and extract | Re-snapshot before extraction |
| **Timeout on navigation** | Slow server or network | Increase timeout to 10-15s, retry with backoff |
| **Pagination not found** | Next page button hidden or AJAX | Check URL params, look for link elements |
| **Data truncated** | HTML shows "..." or hidden overflow | Text still present in HTML, extract as-is |

### Error Handling Code

```typescript
async function extractWithErrorHandling(page, selector, rowExtractor) {
  try {
    // Step 1: Verify table exists
    const table = page.find(selector)
    if (!table) {
      throw new Error(`Table selector not found: ${selector}`)
    }

    // Step 2: Extract rows with validation
    const rows = []
    const rowElements = page.findAll(`${selector} tbody tr`)

    if (rowElements.length === 0) {
      throw new Error(`No rows found in ${selector}`)
    }

    for (let i = 0; i < rowElements.length; i++) {
      try {
        const row = rowExtractor(rowElements[i], i)

        // Step 3: Validate extracted data
        if (!row.name || !row.price) {
          console.warn(`Row ${i} missing required fields:`, row)
          continue // Skip invalid rows
        }

        rows.push(row)
      } catch (rowError) {
        console.error(`Error extracting row ${i}:`, rowError.message)
        // Continue to next row instead of failing completely
        continue
      }
    }

    // Step 4: Ensure minimum data
    if (rows.length === 0) {
      throw new Error('No valid rows extracted')
    }

    return rows

  } catch (error) {
    if (error.message.includes('timeout')) {
      throw new Error('Page load timeout - increase waitUntil timeout')
    }
    if (error.message.includes('UTF-8')) {
      throw new Error('Encoding issue - ensure UTF-8 headers')
    }
    throw error
  }
}
```

---

## Optimization Tips

### 1. Parallel Extraction (Multiple Tables)

```typescript
// Extract multiple tables simultaneously
const [stocks, indices, sectors] = await Promise.all([
  extractStockTable(page, 'table.type_2'),
  extractIndicesTable(page, 'div.indices-data'),
  extractSectorTable(page, 'table.sector-tbl')
])
```

**Speedup:** 2-3x faster when extracting 3+ independent data sources

---

### 2. Incremental Parsing

```typescript
// Process large results incrementally (avoid full parse)
async function* extractRowsIncremental(page, selector, pageSize = 100) {
  const rows = []
  let processed = 0

  for (const tr of page.findAll(`${selector} tbody tr`)) {
    rows.push(parseRow(tr))
    processed++

    if (rows.length >= pageSize) {
      yield rows
      rows.length = 0 // Clear for next batch
    }
  }

  if (rows.length > 0) {
    yield rows
  }
}

// Usage:
for await (const batch of extractRowsIncremental(page, 'table.type_2')) {
  await processBatch(batch) // Send to database, API, etc.
}
```

**Memory efficiency:** Processes 10,000+ rows without loading into memory

---

### 3. Lazy Selector Evaluation

```typescript
// Cache snapshot, evaluate selectors on demand
const snapshot = await page.snapshot()

// Only parse when needed
const lazyExtractor = {
  getStocks: () => parseStockTable(snapshot),
  getIndices: () => parseIndices(snapshot),
  getPrices: () => parsePriceMap(snapshot)
}

// Usage: Only compute needed data
const stocks = lazyExtractor.getStocks()
```

**Performance:** Avoid parsing unused data

---

### 4. Selector Caching

```typescript
// Cache compiled selectors
const selectors = {
  stockTable: 'table.type_2',
  tableRows: 'table.type_2 tbody tr',
  priceCell: (rowIndex) => `table.type_2 tbody tr:nth-child(${rowIndex + 1}) td.number`,
  nameCell: (rowIndex) => `table.type_2 tbody tr:nth-child(${rowIndex + 1}) td.title`
}

// Reuse across multiple pages
for (const url of urls) {
  const page = await navigate(url)
  const stocks = extract(page, selectors)
}
```

**Performance:** 10-15% faster with selector caching

---

### 5. Format Normalization (Single Pass)

```typescript
// Normalize Korean financial formats once
const formatNormalizers = {
  number: (s) => parseFloat(s.replace(/,/g, '').replace(/[^\d.-]/g, '')),
  percentage: (s) => parseFloat(s.replace(/[^\d.-]/g, '')) / 100,
  date: (s) => {
    const match = s.match(/(\d{4})[./-](\d{1,2})[./-](\d{1,2})/)
    if (match) {
      return new Date(match[1], match[2] - 1, match[3])
    }
    return null
  },
  currency: (s) => ({
    value: parseFloat(s.replace(/[^\d.]/g, '')),
    unit: s.includes('조') ? 'trillion' : s.includes('억') ? 'hundred-million' : 'won'
  })
}

// Apply to row:
const row = {
  price: formatNormalizers.number(cellText),
  changeRate: formatNormalizers.percentage(cellText),
  date: formatNormalizers.date(cellText),
  marketCap: formatNormalizers.currency(cellText)
}
```

---

## Output Format

### JSON Schema

```typescript
interface StaticScrapingResult {
  metadata: {
    timestamp: ISO8601String        // "2024-01-29T14:30:00.000Z"
    url: string                      // "https://finance.naver.com/..."
    strategy: 'static'
    site: 'naver-finance' | 'dart' | 'krx' | 'other'
    confidence: number               // 0.0 - 1.0
    duration_ms: number
  }

  data: {
    type: 'table' | 'list' | 'card'
    rows: Array<Record<string, unknown>>
    count: number
    columns: string[]
  }

  validation: {
    passed: boolean
    errors: Array<{
      row_index: number
      field: string
      error: string
      value: unknown
    }>
    warnings: string[]
  }

  pagination?: {
    current_page: number
    total_pages: number
    next_url?: string
    has_next: boolean
  }
}
```

### Example Output

```json
{
  "metadata": {
    "timestamp": "2024-01-29T14:30:00.000Z",
    "url": "https://finance.naver.com/sise/siseList.naver",
    "strategy": "static",
    "site": "naver-finance",
    "confidence": 0.98,
    "duration_ms": 342
  },
  "data": {
    "type": "table",
    "rows": [
      {
        "code": "005930",
        "name": "삼성전자",
        "price": 75000,
        "change": -500,
        "changeRate": -0.66,
        "volume": 12345678
      },
      {
        "code": "000660",
        "name": "SK하이닉스",
        "price": 180000,
        "change": 1500,
        "changeRate": 0.84,
        "volume": 23456789
      }
    ],
    "count": 2,
    "columns": ["code", "name", "price", "change", "changeRate", "volume"]
  },
  "validation": {
    "passed": true,
    "errors": [],
    "warnings": []
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "next_url": "https://finance.naver.com/sise/siseList.naver?page=2",
    "has_next": true
  }
}
```

---

## Fallback to Dynamic

When to switch from static to dynamic scraping:

### Fallback Triggers

```typescript
interface FallbackCriteria {
  // Trigger dynamic if:
  emptyResults: boolean        // 0 rows extracted from expected data
  missingColumns: boolean      // Expected columns not found
  inconsistentStructure: boolean // Row counts don't match
  frequentTimeouts: boolean    // >2 navigation timeouts
  partialContent: boolean      // Content appears after delay
  javascriptRequired: boolean  // Page has data-react-root, #app, etc.
}

async function decideScrapeStrategy(page, url) {
  // Try static first
  const staticResult = await tryStaticScrape(page, url)

  // Check fallback criteria
  const shouldFallback =
    staticResult.data.rows.length === 0 ||
    staticResult.validation.errors.length > (staticResult.data.count * 0.1) || // >10% errors
    staticResult.data.columns.length < 3 // Less than 3 columns found

  if (shouldFallback) {
    console.log('[Fallback] Static extraction failed, switching to dynamic')
    return await tryDynamicScrape(page, url)
  }

  return staticResult
}
```

### When Fallback is Mandatory

| Condition | Reason | Use Dynamic |
|-----------|--------|------------|
| 0 rows extracted | Content not in initial HTML | Yes |
| >30% validation errors | Unparseable format | Yes |
| Content appears after wait | Requires JavaScript execution | Yes |
| AJAX pagination | Dynamic list loading | Yes |
| Infinite scroll | Requires scroll events | Yes |
| Login required | Session/authentication state | Manual intervention |

---

## Korean Financial Examples

### Example 1: Naver Finance Stock List

**URL:** `https://finance.naver.com/sise/siseList.naver`

**Selector:** `table.type_2`

```typescript
async function extractNaverStockList(page) {
  const snapshot = await page.snapshot()

  // Verify static candidate
  const table = page.find('table.type_2')
  if (!table) throw new Error('Naver stock table not found')

  // Extract headers
  const headers = Array.from(table.querySelectorAll('thead th'))
    .map(th => th.textContent.trim())

  // Extract rows
  const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
    const cells = tr.querySelectorAll('td')
    return {
      code: tr.dataset.code,
      name: cells[0].textContent.trim(),
      price: parseFloat(cells[1].textContent.replace(/,/g, '')),
      change: parseFloat(cells[2].textContent.replace(/,/g, '')),
      changeRate: parseFloat(cells[3].textContent),
      volume: parseFloat(cells[4].textContent.replace(/,/g, ''))
    }
  })

  return {
    metadata: {
      timestamp: new Date().toISOString(),
      url: page.url,
      strategy: 'static',
      site: 'naver-finance'
    },
    data: {
      type: 'table',
      rows,
      count: rows.length,
      columns: headers
    },
    validation: {
      passed: rows.length > 0,
      errors: [],
      warnings: []
    }
  }
}
```

---

### Example 2: DART Disclosure Search

**URL:** `https://dart.fss.or.kr/dsaf001/main.do`

**Selector:** `table.rst_tbl`

```typescript
async function extractDartDisclosures(page, companyName) {
  // Navigate to DART
  await page.navigate('https://dart.fss.or.kr/dsaf001/main.do')

  // Verify table exists
  const table = page.find('table.rst_tbl')
  if (!table) throw new Error('DART disclosure table not found')

  // Extract rows
  const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
    const cells = tr.querySelectorAll('td')
    const reportLink = cells[1].querySelector('a')

    return {
      company: cells[0].textContent.trim(),
      reportTitle: reportLink?.textContent.trim(),
      reportLink: reportLink?.href,
      reportDate: parseKoreanDate(cells[2].textContent),
      disclosureDate: parseKoreanDate(cells[3].textContent),
      viewLink: cells[4].querySelector('a')?.href
    }
  })

  return {
    metadata: {
      timestamp: new Date().toISOString(),
      url: page.url,
      strategy: 'static',
      site: 'dart'
    },
    data: {
      type: 'table',
      rows,
      count: rows.length,
      columns: ['company', 'reportTitle', 'reportDate', 'disclosureDate']
    },
    validation: {
      passed: rows.length > 0,
      errors: [],
      warnings: []
    },
    pagination: {
      current_page: 1,
      has_next: !!page.find('a.next-page')
    }
  }
}

function parseKoreanDate(dateStr) {
  // "2024.01.15" or "2024-01-15" -> Date
  const normalized = dateStr.replace(/-/g, '.')
  const [year, month, day] = normalized.split('.')
  return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}
```

---

### Example 3: KRX Listed Companies

**URL:** `https://kind.krx.co.kr/corpgeneral/`

**Selector:** `table.MEM0` or `div[data-code]`

```typescript
async function extractKRXCompanies(page) {
  const snapshot = await page.snapshot()

  // KRX uses modern div-based layout
  const companies = Array.from(page.findAll('tr[data-ccp_code]')).map(tr => {
    const cells = tr.querySelectorAll('td')

    return {
      code: tr.dataset.ccp_code,
      name: cells[0].textContent.trim(),
      market: cells[1].textContent.trim(), // KOSPI, KOSDAQ, KONEX
      sector: cells[2].textContent.trim(),
      listingDate: parseKoreanDate(cells[3].textContent),
      ceo: cells[4].textContent.trim(),
      website: cells[5].querySelector('a')?.href
    }
  })

  return {
    metadata: {
      timestamp: new Date().toISOString(),
      url: page.url,
      strategy: 'static',
      site: 'krx',
      confidence: 0.95
    },
    data: {
      type: 'table',
      rows: companies,
      count: companies.length,
      columns: ['code', 'name', 'market', 'sector', 'listingDate', 'ceo', 'website']
    },
    validation: {
      passed: companies.length > 100, // KRX should have many companies
      errors: companies
        .map((c, i) => (!c.code || !c.name ? { row_index: i, error: 'Missing code or name' } : null))
        .filter(Boolean),
      warnings: []
    }
  }
}
```

---

## Best Practices Checklist

- [ ] Verify [STATIC_CANDIDATE] criteria pass (6/7 rules)
- [ ] Navigate with appropriate timeout (5-10s for Korean sites)
- [ ] Take snapshot before extraction
- [ ] Use Priority 1 selectors (data-* attributes) when available
- [ ] Handle Korean number formatting (commas, decimals)
- [ ] Normalize date formats to ISO 8601
- [ ] Decode HTML entities (&amp;, &lt;, etc.)
- [ ] Validate extracted data before returning
- [ ] Handle pagination via URL params
- [ ] Test fallback to dynamic if static fails
- [ ] Log confidence score with metadata
- [ ] Cache selectors for multiple pages
- [ ] Process large results incrementally
- [ ] Use Promise.all() for parallel extraction
- [ ] Include detailed error messages with row/column info

---

## Related Strategies

- **Dynamic Scraping Strategy** - Use when content requires JavaScript execution
- **API Integration** - Korean financial APIs (KRX, DART REST endpoints)
- **Performance Tuning** - Parallel extraction, caching, batch processing
- **Error Recovery** - Retry logic, fallback selectors, partial results

