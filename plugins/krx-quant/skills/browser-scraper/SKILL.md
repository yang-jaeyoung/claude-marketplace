---
name: browser-scraper
description: Intelligent web scraping orchestration for Korean financial data with automatic strategy selection, pagination handling, and session persistence
argument-hint: <URL> [query] [--mode=AUTO|MANUAL] [--discover-api] | status | resume [session-id] | list | export [session-id] | cancel [session-id]
aliases: [scrape, extract-web, web-data]
version: 1.0.0
domain: data-extraction
complexity: high
requires-mcp: [playwright, chrome-devtools, claude-in-chrome]
---

# Browser Scraper Skill

## Overview

The browser-scraper skill provides intelligent orchestration for extracting data from Korean financial websites. It follows a 6-phase protocol with automatic strategy selection, pagination handling, and robust error recovery.

### 6-Phase Protocol

```
RECONNAISSANCE → STRATEGY SELECTION → EXTRACTION → PAGINATION → EXPORT → VERIFICATION
     ↓                  ↓                  ↓            ↓          ↓           ↓
  explore          architect-low      executor      executor    writer    architect-low
  (haiku)            (haiku)        (haiku/sonnet)  (sonnet)   (haiku)     (haiku)
```

**Phase 1: Reconnaissance** - Analyze page structure, identify data patterns, detect anti-scraping measures
**Phase 2: Strategy Selection** - Choose optimal extraction strategy (DOM, API, hybrid)
**Phase 3: Extraction** - Execute data extraction with selected strategy
**Phase 4: Pagination** - Handle multi-page data collection
**Phase 5: Export** - Format and save extracted data
**Phase 6: Verification** - Validate completeness and data quality

---

## Usage Examples

### Korean Financial Sites

```bash
# Naver Finance - Market Cap Rankings
/browser-scraper https://finance.naver.com/sise/sise_market_sum.naver "시가총액 상위 100개"

# DART - Corporate Disclosures
/browser-scraper AUTO: https://dart.fss.or.kr "최근 공시 목록"

# KRX Data Portal - Discover Hidden API
/browser-scraper https://data.krx.co.kr/contents/MDC/MDI/mdiLoader "종목별 시세" --discover-api

# KRX Stock Statistics
/browser-scraper https://kind.krx.co.kr/investorstatistics/investorstatistics.do "투자자별 매매동향"

# Session Management
/browser-scraper status                    # Show active sessions
/browser-scraper resume scraper-20260129   # Resume interrupted session
/browser-scraper list                      # List all sessions
/browser-scraper export scraper-20260129   # Export session data
/browser-scraper cancel scraper-20260129   # Cancel session
```

### Mode Selection

| Mode | When to Use | Example |
|------|-------------|---------|
| `MANUAL` (default) | Single page, simple structure | Market cap table extraction |
| `AUTO` | Multi-page, complex navigation | Scraping all disclosures from DART |
| `--discover-api` | Suspected API behind UI | KRX data portal, dynamic charts |

---

## MCP Tool Selection Guide

The scraper automatically selects the best MCP tool for the job:

| Tool | Provider | Best For | Korean Sites |
|------|----------|----------|--------------|
| `browser_snapshot` | playwright | Initial reconnaissance | All sites |
| `browser_navigate` | playwright | Navigation, form submission | DART search, KRX filters |
| `browser_click` | playwright | Interactive elements | Pagination buttons |
| `browser_evaluate` | playwright | DOM extraction | Naver Finance tables |
| `browser_network_requests` | playwright | API discovery | KRX Data, Chart APIs |
| `browser_wait_for` | playwright | Dynamic content | AJAX-loaded tables |
| `read_page` | claude-in-chrome | Full page context | Complex layouts |
| `javascript_tool` | claude-in-chrome | Custom extraction logic | Non-standard structures |
| `get_network_requests` | chrome-devtools | Deep API analysis | Hidden XHR endpoints |

**Decision Matrix:**

```
Does page use infinite scroll? → claude-in-chrome:read_page
Does page load data via XHR? → playwright:browser_network_requests
Does page use pagination? → playwright:browser_click + browser_wait_for
Is structure simple/tabular? → playwright:browser_evaluate
Need custom scraping logic? → claude-in-chrome:javascript_tool
```

---

## Scraping Protocol

### Phase 1: Reconnaissance

**Objective:** Understand page structure and identify optimal extraction strategy

**Agent:** `explore` (haiku)
**Duration:** 30-60 seconds

**Tasks:**
1. Take initial snapshot with `browser_snapshot`
2. Analyze DOM structure for data-bearing elements
3. Detect anti-scraping measures (rate limits, CAPTCHAs, dynamic IDs)
4. Identify pagination mechanisms (buttons, infinite scroll, page numbers)
5. Check for network requests (XHR/Fetch) via `browser_network_requests`

**Deliverable:** Reconnaissance report with:
- Data location (CSS selectors, XPath)
- Pagination type
- Anti-scraping indicators
- Recommended strategy

**Example Prompt:**
```
Task(
  subagent_type="oh-my-claudecode:explore",
  model="haiku",
  prompt="""
  Perform reconnaissance on https://finance.naver.com/sise/sise_market_sum.naver

  Analyze:
  1. DOM structure for stock table
  2. Pagination mechanism (button, infinite scroll, URL params)
  3. Anti-scraping measures (rate limits, dynamic class names)
  4. Network requests for hidden APIs

  Deliver: Structured report with recommended extraction strategy
  """
)
```

---

### Phase 2: Strategy Selection

**Objective:** Choose optimal scraping approach based on reconnaissance

**Agent:** `architect-low` (haiku)
**Duration:** 10-20 seconds

**Strategies:**

| Strategy | When to Use | Tools | Pros | Cons |
|----------|-------------|-------|------|------|
| **DOM Direct** | Static HTML tables | `browser_evaluate` | Simple, fast | Breaks if structure changes |
| **API Discovery** | XHR/Fetch detected | `browser_network_requests` | Clean data, reliable | Requires auth handling |
| **Hybrid** | Partial API, partial DOM | Both | Best of both | More complex |
| **Scroll-and-Extract** | Infinite scroll | `read_page` + scroll | Handles dynamic load | Slower |
| **Click-and-Wait** | Paginated buttons | `browser_click` + `browser_wait_for` | Reliable for pagination | Sequential only |

**Selection Criteria:**

```javascript
if (networkRequests.includes('api') && networkRequests.data.isJSON) {
  return 'API Discovery';
} else if (paginationType === 'infinite-scroll') {
  return 'Scroll-and-Extract';
} else if (dom.structure === 'table' && !antiScraping.detected) {
  return 'DOM Direct';
} else {
  return 'Hybrid';
}
```

**Deliverable:** Strategy document with:
- Selected strategy name
- Tool chain
- Expected data schema
- Estimated pages/records

**Example Prompt:**
```
Task(
  subagent_type="oh-my-claudecode:architect-low",
  model="haiku",
  prompt="""
  Given reconnaissance report, select scraping strategy.

  Inputs:
  - Page has XHR requests to /api/sise_market_sum
  - Table structure with <tr> rows
  - Pagination via "다음" button

  Decide: DOM Direct vs API Discovery vs Hybrid
  Output: Strategy name + tool chain + rationale
  """
)
```

---

### Phase 3: Extraction

**Objective:** Execute data extraction with selected strategy

**Agent:** `executor-low` (haiku) for simple DOM, `executor` (sonnet) for complex/hybrid
**Duration:** Variable (30s - 5min per page)

**Execution by Strategy:**

#### DOM Direct
```javascript
// Tool: browser_evaluate
const data = await browser_evaluate(`
  Array.from(document.querySelectorAll('.type_2 tr')).slice(1).map(row => ({
    rank: row.cells[0]?.innerText.trim(),
    name: row.cells[1]?.innerText.trim(),
    price: row.cells[2]?.innerText.trim(),
    change: row.cells[3]?.innerText.trim(),
    marketCap: row.cells[6]?.innerText.trim()
  }))
`);
```

#### API Discovery
```javascript
// Tool: browser_network_requests
const requests = await browser_network_requests();
const apiCall = requests.find(r => r.url.includes('/sise_market_sum'));
const response = JSON.parse(apiCall.response);
const data = response.result.map(item => ({
  rank: item.rank,
  name: item.hname,
  price: item.nv,
  marketCap: item.mks
}));
```

#### Scroll-and-Extract
```javascript
// Tool: read_page + javascript_tool
await javascript_tool(`
  window.scrollTo(0, document.body.scrollHeight);
  await new Promise(r => setTimeout(r, 2000));
`);
const html = await read_page();
// Parse HTML for newly loaded content
```

**Error Handling:**
- Retry on network failure (3 attempts, exponential backoff)
- Fallback to DOM if API fails
- Save partial results before crash

**Deliverable:** Extracted data array with schema:
```json
{
  "records": [...],
  "schema": {"rank": "number", "name": "string", ...},
  "extractedAt": "2026-01-29T10:30:00Z",
  "source": "https://...",
  "strategy": "DOM Direct"
}
```

**Example Prompt:**
```
Task(
  subagent_type="oh-my-claudecode:executor",
  model="sonnet",
  prompt="""
  Extract data using API Discovery strategy.

  Strategy: Intercept XHR to /api/sise_market_sum, parse JSON response

  Steps:
  1. browser_network_requests to capture API calls
  2. Find request matching /sise_market_sum
  3. Parse JSON response
  4. Map to schema: {rank, name, price, change, marketCap}
  5. Save to .omc/krx-quant/scraper/{session-id}/data-page-1.json

  Handle errors: Retry 3x, fallback to DOM if API blocked
  """
)
```

---

### Phase 4: Pagination

**Objective:** Collect data across multiple pages

**Agent:** `executor` (sonnet)
**Duration:** Variable (depends on page count)

**Pagination Patterns:**

| Pattern | Detection | Tool Chain | Example Site |
|---------|-----------|------------|--------------|
| **Button Next** | `<a>다음</a>` exists | `browser_click` + `browser_wait_for` | Naver Finance |
| **Page Numbers** | `<a>1</a><a>2</a>...` | Click each number | DART |
| **Infinite Scroll** | `onscroll` listener | `javascript_tool` scroll loop | KRX charts |
| **URL Parameters** | `?page=N` in URL | `browser_navigate` with params | KRX data tables |
| **Load More Button** | `<button>더보기</button>` | Click until disabled | KIND |

**Loop Control:**

```javascript
let page = 1;
const maxPages = config.maxPages || 50;
const data = [];

while (page <= maxPages) {
  // Extract current page
  const pageData = await extractCurrentPage();
  data.push(...pageData);

  // Check for next page
  const hasNext = await browser_evaluate(`
    document.querySelector('.pgRR') !== null
  `);

  if (!hasNext) break;

  // Navigate to next page
  await browser_click('.pgRR'); // "다음" button
  await browser_wait_for('table.type_2', {timeout: 5000});

  page++;

  // Rate limiting
  await sleep(config.delayBetweenPages || 1000);
}
```

**Early Exit Conditions:**
- No more pages detected
- Max pages reached (default: 50)
- Max records reached (default: 10,000)
- Duplicate data detected (loop detection)
- Rate limit encountered (429 status)

**Deliverable:** Combined dataset from all pages

**Example Prompt:**
```
Task(
  subagent_type="oh-my-claudecode:executor",
  model="sonnet",
  prompt="""
  Handle pagination for Naver Finance market cap rankings.

  Pagination: Button with class 'pgRR' for next page
  Max pages: 20
  Delay: 1500ms between pages

  Loop:
  1. Extract current page data
  2. Click next button (.pgRR)
  3. Wait for table reload (table.type_2)
  4. Repeat until button disabled or max pages

  Save incremental results after each page to:
  .omc/krx-quant/scraper/{session-id}/data-page-{N}.json
  """
)
```

---

### Phase 5: Export

**Objective:** Format and save extracted data in requested formats

**Agent:** `writer` (haiku)
**Duration:** 10-30 seconds

**Export Formats:**

| Format | Use Case | File Extension | Example |
|--------|----------|----------------|---------|
| **JSON** | API consumption, analysis | `.json` | Stock data for Python scripts |
| **CSV** | Excel, spreadsheets | `.csv` | Market cap rankings for Excel |
| **Markdown Table** | Documentation, reports | `.md` | Summary for AGENTS.md |
| **SQL Insert** | Database import | `.sql` | Bulk insert to PostgreSQL |
| **Parquet** | Big data, analytics | `.parquet` | Large datasets for pandas |

**Output Directory Structure:**

```
.omc/krx-quant/scraper/{session-id}/
├── metadata.json          # Session info, strategy used
├── data-page-1.json       # Raw page 1 data
├── data-page-2.json       # Raw page 2 data
├── ...
├── combined.json          # All pages merged
├── export.csv             # CSV export
├── export.md              # Markdown table
└── logs.txt               # Execution log
```

**Data Transformations:**

```javascript
// Clean Korean number formats
function cleanKoreanNumber(str) {
  return str
    .replace(/,/g, '')           // Remove commas
    .replace(/억/g, '00000000')  // Convert 억 to zeros
    .replace(/만/g, '0000');     // Convert 만 to zeros
}

// Parse date formats
function parseKoreanDate(str) {
  // "2026.01.29" → "2026-01-29"
  return str.replace(/\./g, '-');
}
```

**Deliverable:** Exported files in `.omc/krx-quant/scraper/{session-id}/`

**Example Prompt:**
```
Task(
  subagent_type="oh-my-claudecode:writer",
  model="haiku",
  prompt="""
  Export scraped data to CSV and Markdown.

  Input: .omc/krx-quant/scraper/scraper-20260129/combined.json
  Output formats: CSV, Markdown table

  Transformations:
  1. Clean Korean numbers (remove 억/만, convert to integers)
  2. Parse dates (YYYY.MM.DD → YYYY-MM-DD)
  3. Sort by market cap descending

  Files:
  - export.csv (UTF-8 with BOM for Excel)
  - export.md (formatted table with alignment)
  """
)
```

---

### Phase 6: Verification

**Objective:** Validate data completeness and quality

**Agent:** `architect-low` (haiku)
**Duration:** 10-20 seconds

**Verification Checks:**

| Check | Pass Criteria | Failure Action |
|-------|---------------|----------------|
| **Record Count** | >= Expected count (90% tolerance) | Warn user, suggest re-run |
| **Schema Validity** | All required fields present | Flag missing fields |
| **Data Types** | Numbers are numeric, dates parseable | Show type errors |
| **Duplicates** | < 5% duplicate records | Deduplicate and warn |
| **Nulls** | < 10% null values in key fields | Show null percentage |
| **Range Validation** | Prices > 0, dates <= today | Flag outliers |

**Verification Report:**

```json
{
  "session": "scraper-20260129",
  "timestamp": "2026-01-29T10:45:00Z",
  "checks": {
    "recordCount": {"expected": 500, "actual": 487, "pass": true},
    "schemaValid": {"pass": true},
    "dataTypes": {"errors": 0, "pass": true},
    "duplicates": {"count": 12, "percentage": 2.4, "pass": true},
    "nulls": {"marketCap": 0, "price": 3, "pass": true},
    "rangeValid": {"outliers": 0, "pass": true}
  },
  "status": "PASS",
  "warnings": ["3 records have null prices"],
  "dataQualityScore": 0.97
}
```

**Deliverable:** Verification report + recommendation (PASS/WARN/FAIL)

**Example Prompt:**
```
Task(
  subagent_type="oh-my-claudecode:architect-low",
  model="haiku",
  prompt="""
  Verify scraped data quality.

  Input: .omc/krx-quant/scraper/scraper-20260129/combined.json
  Expected: ~500 records (시가총액 상위 500)

  Check:
  1. Record count (allow 90% threshold)
  2. Required fields: rank, name, price, marketCap
  3. Data types (rank/price/marketCap should be numbers)
  4. Duplicates by 'name' field
  5. Null percentages
  6. Price range (should be > 0)

  Output: Verification report JSON + PASS/WARN/FAIL status
  """
)
```

---

## AUTO Mode

**AUTO Mode** enables fully autonomous multi-page scraping with loop control and promise tracking.

### Activation

```bash
# Explicit AUTO prefix
/browser-scraper AUTO: https://dart.fss.or.kr "공시 목록 전체"

# Or via flag
/browser-scraper https://finance.naver.com/sise --mode=AUTO
```

### Loop Control Protocol

**Iteration Tracking:**

```json
{
  "session": "scraper-20260129",
  "mode": "AUTO",
  "iteration": 1,
  "maxIterations": 50,
  "pagesExtracted": 0,
  "recordsExtracted": 0,
  "status": "IN_PROGRESS",
  "promises": {
    "SCRAPER_COMPLETE": false,
    "SCRAPER_BLOCKED": false
  }
}
```

**Loop Rules:**

| Condition | Action | State Update |
|-----------|--------|--------------|
| Successful page extraction | Continue to next page | `pagesExtracted++`, `iteration++` |
| No more pages detected | Set `PROMISE:SCRAPER_COMPLETE` | `status = "COMPLETED"` |
| Rate limit (429) | Wait 60s, retry | `retries++` |
| Max iterations reached | Set `PROMISE:SCRAPER_COMPLETE` | `status = "MAX_ITERATIONS"` |
| CAPTCHA detected | Set `PROMISE:SCRAPER_BLOCKED` | `status = "BLOCKED"` |
| Max retries (3) exceeded | Set `PROMISE:SCRAPER_BLOCKED` | `status = "FAILED"` |

### Promise Tags

**PROMISE:SCRAPER_COMPLETE**
```
Triggered when:
- Pagination exhausted (no "다음" button)
- Max pages reached (default: 50)
- Max records reached (default: 10,000)
- Duplicate detection (circular pagination)

Action: Proceed to Phase 5 (Export)
```

**PROMISE:SCRAPER_BLOCKED**
```
Triggered when:
- CAPTCHA detected
- 403 Forbidden (IP banned)
- Rate limit exceeded after retries
- Anti-scraping measure detected

Action: Save partial results, notify user with recovery options
```

### AUTO Mode Rules

```javascript
const AUTO_CONFIG = {
  maxIterations: 50,        // Max pages to scrape
  maxRecords: 10000,        // Max records to collect
  maxRetries: 3,            // Retries per page
  delayBetweenPages: 1500,  // ms delay (rate limiting)
  timeout: 300000,          // 5 min max session time
  duplicateThreshold: 0.8,  // 80% duplicates = circular loop
  enablePartialSave: true,  // Save data after each page
  fallbackStrategy: true    // Try alternate strategy on failure
};
```

**Loop Implementation:**

```javascript
let iteration = 0;
const state = loadState(sessionId);

while (iteration < AUTO_CONFIG.maxIterations) {
  iteration++;
  state.iteration = iteration;

  // Extract current page
  const result = await extractPage(state.strategy);

  if (result.success) {
    state.pagesExtracted++;
    state.recordsExtracted += result.records.length;
    savePartialData(sessionId, result.records);

    // Check exit conditions
    if (state.recordsExtracted >= AUTO_CONFIG.maxRecords) {
      setPromise('SCRAPER_COMPLETE', 'Max records reached');
      break;
    }

    // Check for next page
    const hasNext = await checkNextPage();
    if (!hasNext) {
      setPromise('SCRAPER_COMPLETE', 'Pagination exhausted');
      break;
    }

    // Navigate to next page
    await navigateNext();
    await sleep(AUTO_CONFIG.delayBetweenPages);

  } else {
    // Handle errors
    state.retries++;
    if (state.retries >= AUTO_CONFIG.maxRetries) {
      setPromise('SCRAPER_BLOCKED', result.error);
      break;
    }
    await sleep(5000 * state.retries); // Exponential backoff
  }

  saveState(sessionId, state);
}
```

---

## Session Management

### Directory Structure

```
.omc/krx-quant/scraper/
├── scraper-20260129-103045/          # Session ID: scraper-{YYYYMMDD}-{HHMMSS}
│   ├── metadata.json                 # Session metadata
│   ├── state.json                    # Current state (for resume)
│   ├── reconnaissance.json           # Phase 1 output
│   ├── strategy.json                 # Phase 2 output
│   ├── data-page-1.json              # Phase 3 outputs
│   ├── data-page-2.json
│   ├── combined.json                 # Phase 4 output
│   ├── export.csv                    # Phase 5 outputs
│   ├── export.md
│   ├── verification.json             # Phase 6 output
│   └── logs.txt                      # Execution log
└── sessions.json                     # Session index
```

### State File Format

**state.json:**

```json
{
  "sessionId": "scraper-20260129-103045",
  "url": "https://finance.naver.com/sise/sise_market_sum.naver",
  "query": "시가총액 상위 500",
  "mode": "AUTO",
  "createdAt": "2026-01-29T10:30:45Z",
  "updatedAt": "2026-01-29T10:35:12Z",
  "status": "IN_PROGRESS",
  "currentPhase": "EXTRACTION",
  "progress": {
    "phase": 3,
    "totalPhases": 6,
    "pagesExtracted": 5,
    "recordsExtracted": 250,
    "currentPage": 6,
    "iteration": 6
  },
  "strategy": {
    "name": "DOM Direct",
    "tools": ["browser_evaluate"],
    "confidence": 0.9
  },
  "config": {
    "maxPages": 50,
    "maxRecords": 10000,
    "delayBetweenPages": 1500,
    "exportFormats": ["json", "csv", "md"]
  },
  "errors": [],
  "warnings": ["Slow response time detected"],
  "promises": {
    "SCRAPER_COMPLETE": false,
    "SCRAPER_BLOCKED": false
  }
}
```

**metadata.json:**

```json
{
  "sessionId": "scraper-20260129-103045",
  "url": "https://finance.naver.com/sise/sise_market_sum.naver",
  "query": "시가총액 상위 500",
  "mode": "AUTO",
  "createdAt": "2026-01-29T10:30:45Z",
  "completedAt": "2026-01-29T10:45:22Z",
  "duration": 877,
  "status": "COMPLETED",
  "phases": {
    "reconnaissance": {"duration": 45, "status": "COMPLETED"},
    "strategy": {"duration": 12, "status": "COMPLETED"},
    "extraction": {"duration": 680, "status": "COMPLETED"},
    "pagination": {"duration": 0, "status": "SKIPPED"},
    "export": {"duration": 28, "status": "COMPLETED"},
    "verification": {"duration": 15, "status": "COMPLETED"}
  },
  "results": {
    "pagesExtracted": 10,
    "recordsExtracted": 500,
    "exportedFiles": ["combined.json", "export.csv", "export.md"],
    "dataQualityScore": 0.98
  },
  "strategy": "DOM Direct",
  "mcpTools": ["browser_snapshot", "browser_evaluate", "browser_click"]
}
```

### Session Commands

#### `/browser-scraper status`

Shows all active and recent sessions:

```
ACTIVE SESSIONS:
┌──────────────────────────┬─────────────────────────────────────────┬────────────┬──────────┬──────────┐
│ Session ID               │ URL                                     │ Mode       │ Status   │ Progress │
├──────────────────────────┼─────────────────────────────────────────┼────────────┼──────────┼──────────┤
│ scraper-20260129-103045  │ finance.naver.com/sise/...              │ AUTO       │ ACTIVE   │ 6/50 pg  │
└──────────────────────────┴─────────────────────────────────────────┴────────────┴──────────┴──────────┘

RECENT COMPLETED:
┌──────────────────────────┬─────────────────────────────────────────┬───────────┬──────────┐
│ Session ID               │ URL                                     │ Records   │ Duration │
├──────────────────────────┼─────────────────────────────────────────┼───────────┼──────────┤
│ scraper-20260129-095530  │ dart.fss.or.kr/...                      │ 1,234     │ 12m 34s  │
└──────────────────────────┴─────────────────────────────────────────┴───────────┴──────────┘
```

#### `/browser-scraper resume [session-id]`

Resumes an interrupted session from last saved state:

```bash
# Resume most recent session
/browser-scraper resume

# Resume specific session
/browser-scraper resume scraper-20260129-103045
```

**Resume Logic:**

```javascript
const state = loadState(sessionId);

// Validate resumability
if (state.status === 'COMPLETED') {
  return error('Session already completed');
}
if (state.promises.SCRAPER_BLOCKED) {
  return error('Session blocked, cannot resume');
}

// Resume from last checkpoint
switch (state.currentPhase) {
  case 'RECONNAISSANCE':
    // Restart from Phase 1
    break;
  case 'EXTRACTION':
    // Load partial data, continue from current page
    const currentPage = state.progress.currentPage;
    await navigateToPage(currentPage);
    break;
  case 'PAGINATION':
    // Continue pagination loop
    break;
  // ... other phases
}
```

#### `/browser-scraper list`

Lists all sessions (active and completed):

```bash
/browser-scraper list                 # All sessions
/browser-scraper list --active        # Active only
/browser-scraper list --completed     # Completed only
/browser-scraper list --failed        # Failed only
```

#### `/browser-scraper export [session-id]`

Exports session data to requested formats:

```bash
# Export to default formats (JSON, CSV)
/browser-scraper export scraper-20260129-103045

# Specify formats
/browser-scraper export scraper-20260129-103045 --formats=json,csv,md,sql

# Export to custom path
/browser-scraper export scraper-20260129-103045 --output=/Users/urd/data/
```

#### `/browser-scraper cancel [session-id]`

Cancels an active session:

```bash
# Cancel specific session
/browser-scraper cancel scraper-20260129-103045

# Cancel all active sessions
/browser-scraper cancel --all
```

---

## Error Handling

### Blocker Detection

| Blocker Type | Detection Signal | Recovery Strategy |
|--------------|------------------|-------------------|
| **CAPTCHA** | `#captcha` element, "사람인지 확인" text | Set PROMISE:SCRAPER_BLOCKED, notify user |
| **Rate Limit (429)** | HTTP 429 status | Wait 60s, retry (max 3x) |
| **IP Ban (403)** | HTTP 403 with "차단" message | Set PROMISE:SCRAPER_BLOCKED, suggest proxy |
| **Session Expired** | Redirect to login | Set PROMISE:SCRAPER_BLOCKED, require auth |
| **Page Structure Change** | Selector not found | Fallback to alternate strategy |
| **Network Timeout** | Request timeout > 30s | Retry with increased timeout |
| **Data Format Change** | JSON parse error | Attempt schema migration |
| **Infinite Loop** | 80%+ duplicate records | Exit loop, set PROMISE:SCRAPER_COMPLETE |

### Recovery Strategies

**Automatic Recovery (No User Intervention):**
- Network timeout → Retry 3x with exponential backoff
- Transient 5xx error → Retry 3x
- Selector not found → Try alternate selectors from strategy
- Rate limit → Wait + retry

**User Notification Required:**
- CAPTCHA detected → "Manual CAPTCHA solving required. Resume with /browser-scraper resume after completing CAPTCHA in browser."
- IP ban → "IP blocked. Use VPN or wait 24h. Session saved for resume."
- Auth required → "Login required. Please authenticate, then /browser-scraper resume {session-id}"

**Fallback Strategies:**

```javascript
const STRATEGY_FALLBACKS = {
  'API Discovery': 'Hybrid',      // If API blocked, fall back to hybrid
  'DOM Direct': 'Scroll-and-Extract',  // If selectors fail, try scrolling
  'Scroll-and-Extract': 'Click-and-Wait'  // If scroll fails, try pagination
};
```

---

## Configuration

Settings are stored in `.claude/settings.json` under `browser-scraper` key:

```json
{
  "browser-scraper": {
    "defaultMode": "MANUAL",
    "maxPagesDefault": 50,
    "maxRecordsDefault": 10000,
    "delayBetweenPages": 1500,
    "retryAttempts": 3,
    "timeout": 300000,
    "exportFormats": ["json", "csv", "md"],
    "sessionDirectory": ".omc/krx-quant/scraper",
    "enablePartialSave": true,
    "autoCleanupDays": 30,
    "preferredMCPTool": "playwright",
    "koreanNumberParsing": true,
    "dateFormat": "YYYY-MM-DD"
  }
}
```

**Config Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `defaultMode` | string | `"MANUAL"` | Default mode (MANUAL/AUTO) |
| `maxPagesDefault` | number | `50` | Default max pages in AUTO mode |
| `maxRecordsDefault` | number | `10000` | Default max records in AUTO mode |
| `delayBetweenPages` | number | `1500` | ms delay between pages (rate limiting) |
| `retryAttempts` | number | `3` | Max retries per page |
| `timeout` | number | `300000` | Max session time (ms) |
| `exportFormats` | array | `["json", "csv", "md"]` | Default export formats |
| `sessionDirectory` | string | `.omc/krx-quant/scraper` | Session storage path |
| `enablePartialSave` | boolean | `true` | Save data after each page |
| `autoCleanupDays` | number | `30` | Auto-delete old sessions |
| `preferredMCPTool` | string | `"playwright"` | Preferred MCP provider |
| `koreanNumberParsing` | boolean | `true` | Parse 억/만 in numbers |
| `dateFormat` | string | `"YYYY-MM-DD"` | Output date format |

---

## Korean Financial Sites Guide

### Naver Finance

**URL Pattern:** `https://finance.naver.com/sise/*`

**Common Pages:**

| Page | URL | Data Available |
|------|-----|----------------|
| Market Cap Rankings | `/sise/sise_market_sum.naver` | 시가총액 순위 |
| Trading Volume | `/sise/sise_quant.naver` | 거래량 순위 |
| Price Change | `/sise/sise_rise.naver` | 상승/하락 순위 |
| Sector Index | `/sise/sise_group.naver?type=group` | 업종별 지수 |

**Recommended Strategy:** DOM Direct
**Pagination:** Button click (`.pgRR` for next)
**Anti-scraping:** Dynamic class names (use data-attributes)

**Example Selectors:**

```javascript
const selectors = {
  table: 'table.type_2',
  rows: 'table.type_2 tr',
  rank: 'td:nth-child(1)',
  name: 'td:nth-child(2) a',
  price: 'td:nth-child(3)',
  change: 'td:nth-child(4)',
  marketCap: 'td:nth-child(7)',
  nextButton: '.pgRR'
};
```

---

### DART (전자공시시스템)

**URL Pattern:** `https://dart.fss.or.kr/*`

**Common Pages:**

| Page | URL | Data Available |
|------|-----|----------------|
| Disclosure List | `/dsaf001/main.do` | 공시 목록 |
| Company Info | `/dsac001/main.do` | 기업 정보 |
| Financial Statements | `/dsae001/main.do` | 재무제표 |

**Recommended Strategy:** Hybrid (API + DOM)
**Pagination:** Page numbers (`<a>1</a><a>2</a>...`)
**Anti-scraping:** Session-based, requires cookies

**API Endpoint Discovery:**

```javascript
// Common DART API patterns
const endpoints = {
  disclosureList: '/api/search.json',
  companyInfo: '/api/company.json',
  financials: '/api/fnltt.json'
};
```

**Example Extraction:**

```javascript
// Wait for dynamic table load
await browser_wait_for('table.tb', {timeout: 5000});

const data = await browser_evaluate(`
  Array.from(document.querySelectorAll('table.tb tr')).slice(1).map(row => ({
    date: row.cells[0]?.innerText.trim(),
    company: row.cells[1]?.innerText.trim(),
    title: row.cells[2]?.innerText.trim(),
    type: row.cells[3]?.innerText.trim()
  }))
`);
```

---

### KRX Data Portal

**URL Pattern:** `https://data.krx.co.kr/contents/MDC/MDI/*`

**Recommended Strategy:** API Discovery
**Why:** All data loaded via XHR, clean JSON responses

**API Discovery Steps:**

```bash
/browser-scraper https://data.krx.co.kr/contents/MDC/MDI/mdiLoader --discover-api
```

**Expected API Pattern:**

```
POST /comm/bldAttendant/getJsonData.cmd
Headers:
  - Content-Type: application/x-www-form-urlencoded
Body:
  - bld=dbms/MDC/STAT/standard/MDCSTAT01501
  - locale=ko_KR
  - trdDd=20260129
```

**Response Format:**

```json
{
  "OutBlock_1": [
    {"ISU_SRT_CD": "005930", "ISU_ABBRV": "삼성전자", "TDD_CLSPRC": "75000", ...}
  ]
}
```

**Extraction Strategy:**

```javascript
const requests = await browser_network_requests();
const apiCall = requests.find(r => r.url.includes('getJsonData.cmd'));
const data = JSON.parse(apiCall.response).OutBlock_1;
```

---

### KIND (KRX 정보데이터시스템)

**URL Pattern:** `https://kind.krx.co.kr/*`

**Common Pages:**

| Page | URL | Data Available |
|------|-----|----------------|
| Investor Stats | `/investorstatistics/investorstatistics.do` | 투자자별 매매 |
| Short Selling | `/shortsell/shortsell.do` | 공매도 현황 |

**Recommended Strategy:** Scroll-and-Extract
**Pagination:** "더보기" (Load More) button
**Anti-scraping:** Aggressive rate limiting (1 req/2s)

**Example:**

```javascript
// Click "더보기" until disabled
while (true) {
  const hasMore = await browser_evaluate(`
    document.querySelector('.btn-more') &&
    !document.querySelector('.btn-more').disabled
  `);
  if (!hasMore) break;

  await browser_click('.btn-more');
  await browser_wait_for('.data-table', {timeout: 3000});
  await sleep(2000); // Strict rate limit
}
```

---

## Ethical Guidelines

**Respect robots.txt:**
- Always check `/robots.txt` before scraping
- Honor `Crawl-delay` directives
- Respect `Disallow` paths

**Rate Limiting:**
- Default: 1.5s between requests
- Increase delay if server shows signs of stress
- Never exceed 1 request/second without explicit permission

**Data Usage:**
- Only scrape publicly available data
- Do not scrape personal information (email, phone, etc.)
- Respect copyright and terms of service

**Attribution:**
- Credit data sources in exported files
- Include URL and scrape timestamp in metadata

**Good Citizenship:**
- Use descriptive User-Agent header
- Provide contact info in case of issues
- Stop immediately if requested by site owner

---

## Cancellation

To cancel an active scraping session:

```bash
/browser-scraper cancel [session-id]
```

**What Happens:**
1. Current page extraction completes (graceful exit)
2. Partial data saved to session directory
3. Session state marked as `CANCELLED`
4. User notified with resume instructions

**Resume After Cancel:**
```bash
/browser-scraper resume [session-id]
```

---

## Strategy References

Detailed strategy implementations are documented in separate files:

- [DOM Direct Strategy](./strategies/dom-direct.md)
- [API Discovery Strategy](./strategies/api-discovery.md)
- [Hybrid Strategy](./strategies/hybrid.md)
- [Scroll-and-Extract Strategy](./strategies/scroll-and-extract.md)
- [Click-and-Wait Strategy](./strategies/click-and-wait.md)

---

## Examples

### Example 1: Naver Finance Market Cap (MANUAL)

```bash
/browser-scraper https://finance.naver.com/sise/sise_market_sum.naver "상위 100개"
```

**Execution:**
1. Phase 1: Reconnaissance (45s) - Identifies table structure
2. Phase 2: Strategy (12s) - Selects "DOM Direct"
3. Phase 3: Extraction (30s) - Extracts first page
4. Phase 4: Pagination (180s) - Clicks through 5 pages
5. Phase 5: Export (15s) - Generates CSV/JSON
6. Phase 6: Verification (10s) - Validates 100 records

**Output:**
```
.omc/krx-quant/scraper/scraper-20260129-103045/
├── combined.json (100 records)
├── export.csv
└── export.md
```

---

### Example 2: DART Disclosures (AUTO)

```bash
/browser-scraper AUTO: https://dart.fss.or.kr "최근 공시 1000건"
```

**Execution:**
1. AUTO mode detects pagination (page numbers)
2. Loops through 50 pages autonomously
3. Extracts 1000 disclosures
4. Sets PROMISE:SCRAPER_COMPLETE when target reached
5. Exports to JSON/CSV/Markdown

**Output:** 1000 disclosure records with company, date, title, type

---

### Example 3: KRX API Discovery

```bash
/browser-scraper https://data.krx.co.kr/contents/MDC/MDI/mdiLoader "종목별 시세" --discover-api
```

**Execution:**
1. Phase 1: Captures network requests via `browser_network_requests`
2. Identifies POST to `/comm/bldAttendant/getJsonData.cmd`
3. Extracts request parameters and response format
4. Phase 2: Selects "API Discovery" strategy
5. Phase 3: Replicates API call directly (bypasses DOM)
6. Phase 4: Discovers pagination in API parameters

**Output:** Clean JSON dataset + documented API endpoint

---

## Troubleshooting

**Issue:** "CAPTCHA detected, scraper blocked"
**Fix:** Complete CAPTCHA manually in browser, then `/browser-scraper resume {session-id}`

**Issue:** "Rate limit exceeded (429)"
**Fix:** Increase `delayBetweenPages` in config to 3000ms

**Issue:** "Selectors not found"
**Fix:** Page structure changed. Re-run reconnaissance or try `--discover-api`

**Issue:** "Session timeout"
**Fix:** Increase `timeout` in config or reduce `maxPages`

**Issue:** "Duplicate records detected"
**Fix:** Circular pagination detected. Check pagination logic or set lower `maxPages`

---

## Version History

- **v1.0.0** (2026-01-29) - Initial release with 6-phase protocol, AUTO mode, session management
