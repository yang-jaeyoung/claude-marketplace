# Pagination Strategy for Korean Financial Sites

Comprehensive guide for handling pagination across Korean financial data sources including Naver Finance, DART, and KRX platforms.

---

## 1. Pagination Types

| Type | Detection | Use Cases | Complexity |
|------|-----------|-----------|-----------|
| **Numbered** | URL params (`?page=1`, `?pageNum=1`), page buttons in DOM | Naver Finance, DART search, stock lists | LOW |
| **Infinite Scroll** | Dynamic content loading on scroll, no pagination buttons | KRX data, real-time feeds, mobile views | MEDIUM |
| **Load More** | Explicit "더보기" / "다음" button, incremental data fetch | DART disclosure list, news feeds | MEDIUM |
| **Cursor-Based** | Token/offset in API calls, no total page count | KRX API, historical data endpoints | HIGH |
| **None** | All data on single page or limited dataset | Small lookups, single-stock data | LOW |

---

## 2. Detection Strategy

### 2.1 URL Pattern Analysis

**Check for Pagination Signals:**

```javascript
// Pattern detection for Korean financial sites
const paginationPatterns = {
  numbered: /[\?&](page|pageNum|currentPage|p|pn)=(\d+)/i,
  infinite: /(infinite|lazy|scroll|dynamic)/i,
  loadMore: /page|offset|cursor|start|limit/i,
  api: /(api\.|v\d+\/|ajax)/i
};

function detectPaginationType(url) {
  if (paginationPatterns.api.test(url)) return 'cursor-based';
  if (paginationPatterns.numbered.test(url)) return 'numbered';
  if (paginationPatterns.infinite.test(url)) return 'infinite-scroll';
  return 'load-more'; // fallback
}
```

### 2.2 UI Elements Check

**DOM Inspection for Pagination Controls:**

```javascript
const uiChecks = {
  numbered: [
    '.paging', '.pagination', '.page-navigation',
    'button[aria-label*="페이지"]', 'a[href*="page="]'
  ],
  loadMore: [
    '.load-more', '.more-btn', '.btn-more',
    'button:contains("더보기")', 'button:contains("다음")'
  ],
  infinite: [
    '[data-infinite="true"]', '.lazy-load',
    '[class*="intersection-observer"]'
  ]
};

function detectUIType(document) {
  for (const [type, selectors] of Object.entries(uiChecks)) {
    const found = selectors.some(sel => document.querySelector(sel));
    if (found) return type;
  }
  return 'none';
}
```

---

## 3. Numbered Pagination Workflow

**Best For:** Naver Finance, stock lists, disclosure search

### 3.1 Example: Naver Finance Stock List

URL Pattern: `https://finance.naver.com/sise/sise_market.naver?&page=1`

### 3.2 Workflow Implementation

```javascript
async function scrapNumberedPagination(startUrl, maxPages = 50) {
  const results = [];
  const state = initPaginationState('numbered', startUrl);

  for (let page = 1; page <= maxPages; page++) {
    try {
      // Construct page URL
      const url = new URL(startUrl);
      url.searchParams.set('page', page);

      console.log(`[PAGE ${page}] Fetching: ${url}`);
      state.currentPage = page;
      state.lastFetched = new Date().toISOString();

      // Fetch and parse
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          'Accept-Language': 'ko-KR,ko;q=0.9'
        }
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const html = await response.text();
      const pageData = parsePageContent(html);

      // Check if empty (end of pagination)
      if (pageData.length === 0) {
        console.log(`[STOP] Empty page detected at page ${page}`);
        state.status = 'completed';
        break;
      }

      results.push(...pageData);
      state.pagesCompleted++;
      state.itemsCollected += pageData.length;

      // Rate limiting
      await delay(PAGINATION_DELAY_MS);

      // Checkpoint every 10 pages
      if (page % 10 === 0) {
        saveState(state);
      }

    } catch (error) {
      state.errors.push({
        page,
        error: error.message,
        timestamp: new Date().toISOString()
      });

      if (error.message.includes('429')) {
        state.status = 'rate-limited';
        break;
      }

      // Retry logic for transient errors
      if (shouldRetry(error, page)) {
        page--; // Retry same page
        await delay(RETRY_DELAY_MS);
      }
    }
  }

  saveState(state);
  return { results, state };
}

function parsePageContent(html) {
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const rows = doc.querySelectorAll('table tbody tr');

  return Array.from(rows).map(row => {
    const cols = row.querySelectorAll('td');
    return {
      symbol: cols[0]?.textContent.trim(),
      name: cols[1]?.textContent.trim(),
      price: cols[2]?.textContent.trim(),
      change: cols[3]?.textContent.trim(),
      volume: cols[4]?.textContent.trim()
    };
  });
}
```

### 3.3 Resume from Checkpoint

```javascript
async function resumeNumberedPagination(stateFile, maxPages = 50) {
  const state = loadState(stateFile);
  const results = [];

  console.log(`[RESUME] Starting from page ${state.currentPage + 1}`);
  console.log(`[PROGRESS] Already collected: ${state.itemsCollected} items`);

  for (let page = state.currentPage + 1; page <= maxPages; page++) {
    // Same scraping logic as above
    const pageData = await fetchPage(page);
    if (pageData.length === 0) break;

    results.push(...pageData);
    state.pagesCompleted++;
    state.itemsCollected += pageData.length;
  }

  return { results, state };
}
```

---

## 4. Infinite Scroll Workflow

**Best For:** KRX data feeds, real-time stock charts, mobile views

### 4.1 Example: KRX Market Data

Endpoint: `https://data.krx.co.kr/comm/fileDn.do?type=json&bld=DBMS&mktId=ALL`

### 4.2 Implementation

```javascript
async function scrapInfiniteScroll(startUrl, maxScrolls = 100) {
  const results = [];
  const state = initPaginationState('infinite-scroll', startUrl);

  // Launch headless browser for scroll simulation
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  try {
    await page.goto(startUrl, { waitUntil: 'networkidle2', timeout: 30000 });
    state.status = 'scrolling';

    let scrollCount = 0;
    let lastHeight = 0;
    let emptyScrolls = 0;

    while (scrollCount < maxScrolls && emptyScrolls < 3) {
      // Get current scroll height
      const currentHeight = await page.evaluate(() => {
        return Math.max(
          document.body.scrollHeight,
          document.documentElement.scrollHeight
        );
      });

      if (currentHeight === lastHeight) {
        emptyScrolls++;
        console.log(`[SCROLL ${scrollCount}] No new content (${emptyScrolls}/3)`);
      } else {
        emptyScrolls = 0;
      }

      lastHeight = currentHeight;

      // Scroll down
      await page.evaluate(() => window.scrollBy(0, window.innerHeight));
      console.log(`[SCROLL ${scrollCount + 1}] Height: ${currentHeight}px`);

      // Wait for content to load
      await page.waitForTimeout(SCROLL_DELAY_MS);

      // Extract data
      const pageData = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('[data-row]')).map(el => ({
          symbol: el.querySelector('[data-symbol]')?.textContent,
          price: el.querySelector('[data-price]')?.textContent,
          change: el.querySelector('[data-change]')?.textContent
        }));
      });

      const newItems = pageData.filter(item =>
        !results.some(existing => existing.symbol === item.symbol)
      );

      if (newItems.length > 0) {
        results.push(...newItems);
        state.itemsCollected += newItems.length;
        console.log(`[DATA] Collected ${newItems.length} new items`);
      }

      scrollCount++;
      state.scrollCount = scrollCount;
      state.lastFetched = new Date().toISOString();

      // Checkpoint every 20 scrolls
      if (scrollCount % 20 === 0) {
        saveState(state);
      }
    }

    state.status = 'completed';
    console.log(`[COMPLETE] Stopped after ${scrollCount} scrolls (${emptyScrolls} empty)`);

  } catch (error) {
    state.status = 'error';
    state.errors.push({
      scroll: scrollCount,
      error: error.message,
      timestamp: new Date().toISOString()
    });
    console.error(`[ERROR] Scroll failed: ${error.message}`);
  } finally {
    await browser.close();
    saveState(state);
  }

  return { results, state };
}
```

### 4.3 Resume from Checkpoint

```javascript
async function resumeInfiniteScroll(stateFile, maxScrolls = 100) {
  const state = loadState(stateFile);
  const results = state.cachedResults || [];

  console.log(`[RESUME] Scrolled ${state.scrollCount}/${maxScrolls}`);
  console.log(`[PROGRESS] Items: ${state.itemsCollected}`);

  // Continue from current state
  const additionalResults = await continueScrolling(
    state.url,
    maxScrolls - state.scrollCount,
    state.lastScrollHeight
  );

  return { results: [...results, ...additionalResults], state };
}
```

---

## 5. Load More Button Workflow

**Best For:** DART disclosure list, news feeds, comment threads

### 5.1 Example: DART Disclosure Search

URL: `https://dart.fss.or.kr/cgi-bin/browse_news.cgi?match=&order=&lang=ko`

Button Selector: `button.btn-more, .load-more-btn, a:contains("다음")`

### 5.2 Implementation

```javascript
async function scrapLoadMorePagination(startUrl, maxClicks = 50) {
  const results = [];
  const state = initPaginationState('load-more', startUrl);

  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  try {
    await page.goto(startUrl, { waitUntil: 'networkidle2' });
    state.status = 'loading';
    console.log(`[LOAD-MORE] Started: ${startUrl}`);

    let clickCount = 0;
    let consecutiveNoData = 0;

    while (clickCount < maxClicks && consecutiveNoData < 2) {
      // Extract current page data
      const pageData = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('table tbody tr')).map(row => ({
          date: row.querySelector('td:nth-child(1)')?.textContent.trim(),
          title: row.querySelector('td:nth-child(2)')?.textContent.trim(),
          company: row.querySelector('td:nth-child(3)')?.textContent.trim(),
          category: row.querySelector('td:nth-child(4)')?.textContent.trim()
        }));
      });

      if (pageData.length === 0) {
        consecutiveNoData++;
        console.log(`[LOAD-MORE ${clickCount}] No data found`);
      } else {
        consecutiveNoData = 0;
        results.push(...pageData);
        state.itemsCollected += pageData.length;
      }

      // Check if "Load More" button exists
      const hasMoreButton = await page.$('button.btn-more, .load-more-btn, a.next') !== null;

      if (!hasMoreButton) {
        console.log(`[STOP] No more button found`);
        state.status = 'completed';
        break;
      }

      // Click the button
      try {
        console.log(`[LOAD-MORE ${clickCount + 1}] Clicking button...`);
        await page.click('button.btn-more, .load-more-btn, a.next', { visible: true });

        // Wait for new content to load
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {
          // Navigation might not trigger for AJAX loads
          return page.waitForTimeout(LOAD_MORE_DELAY_MS);
        });

        clickCount++;
        state.loadMoreClicks++;
        state.lastFetched = new Date().toISOString();

        // Checkpoint every 10 clicks
        if (clickCount % 10 === 0) {
          saveState(state);
        }

      } catch (clickError) {
        console.error(`[ERROR] Click failed: ${clickError.message}`);
        state.errors.push({
          click: clickCount,
          error: clickError.message,
          timestamp: new Date().toISOString()
        });

        if (shouldRetryClick(clickError)) {
          await page.waitForTimeout(RETRY_DELAY_MS);
          clickCount--; // Retry same click
        } else {
          break;
        }
      }
    }

  } catch (error) {
    state.status = 'error';
    state.errors.push({
      click: clickCount,
      error: error.message,
      timestamp: new Date().toISOString()
    });
    console.error(`[ERROR] Load more failed: ${error.message}`);
  } finally {
    await browser.close();
    saveState(state);
  }

  return { results, state };
}
```

### 5.3 Resume from Checkpoint

```javascript
async function resumeLoadMore(stateFile, maxClicks = 50) {
  const state = loadState(stateFile);
  const results = state.cachedResults || [];

  console.log(`[RESUME] Clicked ${state.loadMoreClicks}/${maxClicks}`);
  console.log(`[PROGRESS] Items: ${state.itemsCollected}`);

  // Return cached results with ability to continue
  return { results, state, canContinue: true };
}
```

---

## 6. Cursor-Based Pagination (API)

**Best For:** KRX API, historical data endpoints, large datasets

### 6.1 Example: KRX Historical Data API

```
https://data.krx.co.kr/api/v1/market/stocks?cursor=0&limit=1000
https://data.krx.co.kr/api/v1/market/stocks?cursor=eyJvZmZzZXQiOjEwMDB9&limit=1000
```

### 6.2 Implementation

```javascript
async function scrapCursorPagination(apiEndpoint, maxRequests = 100) {
  const results = [];
  const state = initPaginationState('cursor-based', apiEndpoint);

  let cursor = null;
  let requestCount = 0;
  let emptyResponses = 0;

  while (requestCount < maxRequests && emptyResponses < 2) {
    try {
      // Build request URL with cursor
      const url = new URL(apiEndpoint);
      if (cursor) {
        url.searchParams.set('cursor', cursor);
      }
      url.searchParams.set('limit', '1000'); // Optimal batch size

      console.log(`[REQUEST ${requestCount + 1}] Cursor: ${cursor || 'START'}`);
      state.currentCursor = cursor;
      state.lastFetched = new Date().toISOString();

      // API call with retry logic
      const response = await fetchWithRetry(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0',
          'Accept': 'application/json',
          'Accept-Language': 'ko-KR'
        }
      }, 3);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      // Extract items
      const items = data.data || data.records || [];
      if (items.length === 0) {
        emptyResponses++;
        console.log(`[DATA] Empty response (${emptyResponses}/2)`);
        state.status = 'completed';
        break;
      }

      emptyResponses = 0;
      results.push(...items);
      state.itemsCollected += items.length;
      state.requestsCompleted++;

      // Get next cursor
      cursor = data.nextCursor || data.pagination?.nextCursor;
      if (!cursor) {
        console.log(`[STOP] No next cursor provided`);
        state.status = 'completed';
        break;
      }

      requestCount++;

      // Rate limiting
      await delay(PAGINATION_DELAY_MS);

      // Checkpoint every 10 requests
      if (requestCount % 10 === 0) {
        saveState(state);
      }

    } catch (error) {
      state.errors.push({
        request: requestCount,
        cursor: cursor,
        error: error.message,
        timestamp: new Date().toISOString()
      });

      if (error.message.includes('429')) {
        state.status = 'rate-limited';
        console.log(`[RATE-LIMITED] Backing off...`);
        await delay(RATE_LIMIT_BACKOFF_MS);
      } else if (error.message.includes('401') || error.message.includes('403')) {
        state.status = 'unauthorized';
        break;
      } else if (shouldRetryCursorRequest(error, requestCount)) {
        requestCount--; // Retry same cursor
        await delay(RETRY_DELAY_MS);
      }
    }
  }

  saveState(state);
  return { results, state };
}

async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fetch(url, options);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await delay(1000 * Math.pow(2, i)); // Exponential backoff
    }
  }
}
```

### 6.3 Resume from Checkpoint

```javascript
async function resumeCursorPagination(stateFile, maxRequests = 100) {
  const state = loadState(stateFile);
  const results = state.cachedResults || [];

  console.log(`[RESUME] Cursor: ${state.currentCursor || 'START'}`);
  console.log(`[PROGRESS] Requests: ${state.requestsCompleted}, Items: ${state.itemsCollected}`);

  // Continue from saved cursor
  const additionalResults = await continueCursorFetch(
    state.apiEndpoint,
    state.currentCursor,
    maxRequests - state.requestsCompleted
  );

  return { results: [...results, ...additionalResults], state };
}
```

---

## 7. State Management

### 7.1 Track Progress JSON

**Location:** `.krx-quant/scrape-state/{sessionId}.json`

```json
{
  "sessionId": "naver-finance-20240115-1430",
  "source": "naver-finance",
  "paginationType": "numbered",
  "url": "https://finance.naver.com/sise/sise_market.naver?page=",
  "status": "in-progress",
  "startTime": "2024-01-15T14:30:00Z",
  "lastFetched": "2024-01-15T14:45:32Z",
  "currentPage": 5,
  "pagesCompleted": 5,
  "itemsCollected": 2500,
  "errors": [
    {
      "page": 3,
      "error": "Network timeout",
      "timestamp": "2024-01-15T14:35:12Z",
      "retried": true
    }
  ],
  "cachedResults": [
    {
      "symbol": "005930",
      "name": "삼성전자",
      "price": "70000",
      "change": "+1.5%"
    }
  ],
  "checkpoint": {
    "page": 5,
    "itemsSinceCheckpoint": 500,
    "timestamp": "2024-01-15T14:45:00Z"
  }
}
```

### 7.2 State Initialization

```javascript
function initPaginationState(type, url) {
  return {
    sessionId: generateSessionId(),
    source: extractSource(url),
    paginationType: type,
    url: url,
    status: 'pending',
    startTime: new Date().toISOString(),
    lastFetched: null,
    currentPage: 0,
    currentCursor: null,
    scrollCount: 0,
    loadMoreClicks: 0,
    requestsCompleted: 0,
    pagesCompleted: 0,
    itemsCollected: 0,
    errors: [],
    cachedResults: [],
    checkpoint: null
  };
}

function saveState(state) {
  const stateDir = '.krx-quant/scrape-state';
  ensureDir(stateDir);

  const filePath = `${stateDir}/${state.sessionId}.json`;
  fs.writeFileSync(filePath, JSON.stringify(state, null, 2));

  console.log(`[STATE] Saved: ${filePath}`);
}

function loadState(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}
```

### 7.3 Resume Support

```javascript
async function resumeSession(sessionId) {
  const stateFile = `.krx-quant/scrape-state/${sessionId}.json`;
  const state = loadState(stateFile);

  console.log(`[RESUME] Session: ${sessionId}`);
  console.log(`[INFO] Type: ${state.paginationType}`);
  console.log(`[PROGRESS] Status: ${state.status}`);
  console.log(`[PROGRESS] Items collected: ${state.itemsCollected}`);

  switch (state.paginationType) {
    case 'numbered':
      return await resumeNumberedPagination(stateFile);
    case 'infinite-scroll':
      return await resumeInfiniteScroll(stateFile);
    case 'load-more':
      return await resumeLoadMore(stateFile);
    case 'cursor-based':
      return await resumeCursorPagination(stateFile);
    default:
      throw new Error(`Unknown pagination type: ${state.paginationType}`);
  }
}
```

---

## 8. Error Handling

| Error Type | Cause | Detection | Recovery |
|------------|-------|-----------|----------|
| **404 Not Found** | Page deleted, outdated URL | `HTTP 404` response | Stop pagination, return collected data |
| **Rate Limited** | Too many requests | `HTTP 429`, `HTTP 503` | Exponential backoff, wait 60-300s |
| **Timeout** | Network latency, slow server | Request timeout >30s | Retry 2-3x with exponential backoff |
| **Loop Detection** | Same data repeatedly, empty pages | No new items for 3+ iterations | Stop, return results |
| **Network Error** | Connection dropped | Socket error, ECONNREFUSED | Retry with exponential backoff |
| **Memory Full** | Too many results cached | Array size >1GB | Flush to disk, clear cache |
| **Session Expired** | Auth token invalid | `HTTP 401` response | Re-authenticate or stop |
| **Invalid Cursor** | Cursor format changed | `HTTP 400`, invalid cursor format | Reset to initial cursor or stop |

### 8.1 Error Handling Code

```javascript
function shouldRetry(error, attemptNumber) {
  const retryableErrors = [408, 429, 500, 502, 503, 504];
  const statusCode = error.response?.status;

  if (retryableErrors.includes(statusCode)) {
    return attemptNumber < MAX_RETRIES;
  }

  if (error.code === 'ECONNRESET' || error.code === 'ETIMEDOUT') {
    return attemptNumber < MAX_RETRIES;
  }

  return false;
}

function calculateBackoffDelay(attemptNumber) {
  // Exponential backoff: 1s, 2s, 4s, 8s, 16s
  const baseDelay = 1000;
  const maxDelay = 60000; // 1 minute cap
  const delay = Math.min(baseDelay * Math.pow(2, attemptNumber - 1), maxDelay);

  // Add jitter (±10%)
  return delay + (Math.random() - 0.5) * delay * 0.2;
}

async function handlePaginationError(error, state) {
  if (error.response?.status === 429) {
    state.status = 'rate-limited';
    console.log(`[RATE-LIMIT] Waiting 60 seconds...`);
    await delay(60000);
    return 'retry';
  }

  if (error.response?.status === 404) {
    state.status = 'completed';
    console.log(`[404] Page not found, stopping`);
    return 'stop';
  }

  if (error.code === 'ETIMEDOUT' || error.message.includes('timeout')) {
    return 'retry';
  }

  // Default: record error and continue
  state.errors.push({
    timestamp: new Date().toISOString(),
    error: error.message
  });
  return 'continue';
}
```

---

## 9. Limits & Constraints

| Parameter | Default | Rationale | Adjustable |
|-----------|---------|-----------|-----------|
| **Max Pages (Numbered)** | 500 | Typical max for Korean finance sites | Yes, per source |
| **Max Scrolls (Infinite)** | 100 | Memory limits, diminishing returns | Yes |
| **Max Load More Clicks** | 50 | Button fatigue, memory issues | Yes |
| **Max API Requests** | 1000 | Rate limiting concerns | Yes |
| **Request Delay** | 500-1000ms | Respectful crawling, avoid bot detection | Per source |
| **Retry Delay** | 2-5s (exponential) | Don't hammer error endpoints | Adaptive |
| **Rate Limit Backoff** | 60-300s | Recovery time for 429 errors | Adaptive |
| **Request Timeout** | 30s | Reasonable per Korean site latency | Per source |
| **Empty Page Tolerance** | 3 consecutive | Stop if no new data | Yes |
| **Max Concurrent Requests** | 1 | Avoid rate limiting | Yes, for parallel sources |
| **Max Memory Cache** | 500MB | Prevent OOM, auto-flush to disk | Yes |

### 9.1 Configurable Limits

```javascript
const PAGINATION_CONFIG = {
  'naver-finance': {
    type: 'numbered',
    maxPages: 500,
    delay: 750,
    timeout: 30000,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
  },
  'dart': {
    type: 'load-more',
    maxClicks: 50,
    delay: 1000,
    timeout: 30000
  },
  'krx-api': {
    type: 'cursor-based',
    maxRequests: 1000,
    delay: 500,
    timeout: 15000,
    batchSize: 1000
  },
  'krx-data': {
    type: 'infinite-scroll',
    maxScrolls: 100,
    delay: 500,
    timeout: 30000,
    emptyTolerance: 3
  }
};

function getConfig(source) {
  return PAGINATION_CONFIG[source] || {
    delay: 750,
    timeout: 30000,
    maxRetries: 3
  };
}
```

---

## 10. Output Format

### 10.1 Standardized Result

```json
{
  "sessionId": "dart-disclosures-20240115-1430",
  "source": "dart",
  "paginationType": "load-more",
  "status": "completed",
  "summary": {
    "totalItems": 1250,
    "pagesProcessed": 13,
    "clicksRequired": 12,
    "duration": "2m 45s",
    "errors": 1,
    "successRate": 99.9
  },
  "data": [
    {
      "date": "2024-01-15",
      "title": "삼성전자 반기보고서",
      "company": "삼성전자",
      "category": "정기보고서",
      "url": "https://dart.fss.or.kr/...",
      "source": "dart",
      "scrapedAt": "2024-01-15T14:45:32Z"
    }
  ],
  "metadata": {
    "startTime": "2024-01-15T14:30:00Z",
    "endTime": "2024-01-15T14:32:45Z",
    "averageResponseTime": "1250ms",
    "checkpoints": 5,
    "resumed": false
  }
}
```

### 10.2 Export Functions

```javascript
function exportToJSON(results, state, filepath) {
  const output = {
    sessionId: state.sessionId,
    source: state.source,
    paginationType: state.paginationType,
    status: state.status,
    summary: {
      totalItems: results.length,
      pagesProcessed: state.pagesCompleted,
      clicksRequired: state.loadMoreClicks,
      duration: calculateDuration(state.startTime, new Date()),
      errors: state.errors.length,
      successRate: (1 - (state.errors.length / (state.pagesCompleted || 1))) * 100
    },
    data: results,
    metadata: {
      startTime: state.startTime,
      endTime: new Date().toISOString(),
      averageResponseTime: calculateAverageTime(state),
      checkpoints: Math.floor(state.requestsCompleted / 10)
    }
  };

  fs.writeFileSync(filepath, JSON.stringify(output, null, 2));
  console.log(`[EXPORT] Saved to: ${filepath}`);
}

function exportToCSV(results, filepath) {
  const headers = Object.keys(results[0]);
  const rows = results.map(obj => headers.map(h => obj[h]));

  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(v => `"${v}"`).join(','))
  ].join('\n');

  fs.writeFileSync(filepath, csv);
  console.log(`[EXPORT] Saved to: ${filepath}`);
}
```

---

## Implementation Checklist

- [ ] Detect pagination type from URL/UI
- [ ] Initialize pagination state
- [ ] Implement specific workflow (numbered/scroll/click/cursor)
- [ ] Add delay between requests (rate limiting)
- [ ] Track progress in checkpoint JSON
- [ ] Handle errors with retry logic
- [ ] Detect loop/completion conditions
- [ ] Save results periodically
- [ ] Support resume from checkpoint
- [ ] Export final results (JSON/CSV)
- [ ] Log all actions with timestamps

---

## Performance Notes

**Bandwidth Optimization:**
- Numbered: ~2-5 requests/sec = 2-5 MB/min (typical)
- Infinite: Scroll delay 500ms, content ~500KB/scroll = 1 MB/min
- Load More: Button click ~1s, content ~500KB = 500 KB/min
- Cursor: API efficient, ~10MB per request

**Time Estimates:**
- Numbered (100 pages): 2-5 minutes
- Infinite Scroll (100 scrolls): 1-2 minutes
- Load More (50 clicks): 1-2 minutes
- Cursor (1000 requests): 5-10 minutes

**Memory Usage:**
- 10K items: ~5-10 MB
- 100K items: ~50-100 MB
- 1M items: ~500-1000 MB (consider streaming to disk)
