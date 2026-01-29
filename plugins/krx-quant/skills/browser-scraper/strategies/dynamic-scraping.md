# Dynamic Scraping Strategy for Korean Financial Sites

## Overview

This guide covers scraping Single Page Applications (SPAs) and JavaScript-rendered content from Korean financial data sources, particularly KRX-related platforms that rely heavily on dynamic rendering.

---

## 1. When to Use Dynamic Scraping

Use dynamic scraping when:

| Condition | Indicator | Example |
|-----------|-----------|---------|
| **SPA Framework** | Initial HTML empty, content loads via JS | KRX official portal, real-time dashboards |
| **API Calls on Load** | Network requests populate data | Stock ticker data, OHLCV updates |
| **Client-Side Routing** | URL changes but page doesn't reload | Trading statistics by symbol |
| **Lazy Loading** | Content appears after scroll/interaction | Historical data tables, chart data |
| **Real-Time Updates** | WebSocket/polling for live data | Intra-day price feeds |
| **Protected by JavaScript** | HTML obfuscation or client-side rendering | Financial derivatives data |

**When NOT to use:**
- Static HTML page (use static scraping)
- Public API available (use API directly)
- Content loads in `<noscript>` tag (fallback to static)

---

## 2. Detection Criteria: [DYNAMIC_CANDIDATE]

Mark a site as dynamic candidate when ANY of these apply:

```
[DYNAMIC_CANDIDATE] if:
  a) view-source shows <div id="app"></div> or similar empty container
  b) Initial HTML has no stock/financial data, only script tags
  c) Network tab shows API calls to /api/* or graphql endpoints
  d) Page title in <head> is generic (e.g., "React App", "dashboard")
  e) CSS/JS files total >2MB or manifest.json present
  f) Network waterfall shows JS takes >3s before data appears
  g) Console shows "ReactDOM.render" or "Vue.createApp" or "ng.bootstrap"
  h) Page has <script type="application/json" id="__INITIAL_STATE__"> (common in financial apps)
```

---

## 3. Framework Detection Table

Identify rendering framework for better targeting:

| Framework | Detection Indicators | Common in KOR Finance | Data Format |
|-----------|---------------------|----------------------|------------|
| **React** | `React DevTools` extension | KRX Data Labs, Naver Finance | REST API, JSON |
| | `<div id="root"></div>` or `__react*` in window | Modern brokerages | Axios/Fetch |
| | `__REACT_DEVTOOLS_GLOBAL_HOOK__` in console | Financial dashboards | GraphQL (some) |
| **Vue.js** | `<div id="app"></div>` + Vue logo | FinanceHub, some HTS | REST API, JSON |
| | `__VUE_DEVTOOLS__` in window | Korean fintech apps | Fetch |
| | v-app, v-container tags | Secondary sources | Store pattern |
| **Angular** | `ng-app` or `data-ng-app` attributes | Legacy Korean systems | REST API, XML/JSON |
| | `ng-version` in HTML comment | Banking platforms | RxJS Observables |
| | `zone.js` in network tab | Government sites | CORS-restricted |
| **Next.js** | `_next/` folder in network tab | Modern KRX tools | ISR, SSG |
| | `__NEXT_DATA__` in page source | High-performance sites | API Routes (/api/*) |
| | Deployment on Vercel (or Korean CDN) | Latest financial apps | Optimized JSONs |

---

## 4. Workflow: Navigate → Wait → Verify → Snapshot → Extract

### Step 1: Navigate to Target

```typescript
// Pseudocode workflow
const TARGET_URL = "https://example-krx-site.com/stock/005930"; // Samsung Electronics

navigate(TARGET_URL, {
  waitUntil: "domcontentloaded",  // Initial DOM ready
  timeout: 15000
});
```

**For Korean sites:**
- Expect 2-10s load time (servers in Korea, optimized for domestic ISP)
- May redirect (302) due to location-based access control
- Check for "접속 제한" (access restricted) message

### Step 2: Wait for Content

See [Wait Strategies](#5-wait-strategies) section below.

### Step 3: Verify Content Appeared

```typescript
// Check if financial data is present
const hasStockData = await page.evaluate(() => {
  const priceElements = document.querySelectorAll('[data-testid="stock-price"]');
  return priceElements.length > 0 && parseFloat(priceElements[0].textContent) > 0;
});

if (!hasStockData) throw new Error("Stock data did not render");
```

### Step 4: Snapshot Page State

```typescript
// Take accessibility snapshot for reliable extraction
const snapshot = await page.snapshot();
// or full page screenshot for visual verification
const screenshot = await page.screenshot({ fullPage: true });
```

### Step 5: Extract Data

See [Output Format](#9-output-format-json-schema) for structured extraction.

---

## 5. Wait Strategies

Choose based on site behavior. Korean financial sites commonly use multiple patterns.

### Strategy A: Element Visibility (Most Reliable)

**Best for:** Simple cases where you know the final element ID/selector

```typescript
// Wait for primary price element
await page.waitForSelector('div[data-field="현재가"]', { timeout: 8000 });

// Or wait for multiple elements (portfolio view)
await Promise.all([
  page.waitForSelector('.stock-ticker', { timeout: 8000 }),
  page.waitForSelector('.price-change', { timeout: 8000 })
]);
```

**Korean financial site examples:**
```typescript
// KRX Data: 종목명 (stock name) appears when ready
await page.waitForSelector('[data-field="종목명"]', { timeout: 10000 });

// Real-time ticker: 실시간시세 (real-time price) becomes visible
await page.waitForSelector('.realtime-price-display', { timeout: 5000 });
```

### Strategy B: Network Idle (Most Thorough)

**Best for:** Complex dashboards with multiple API calls

```typescript
await page.waitForFunction(
  () => {
    // Check DevTools network status (varies by framework)
    return window.__networkState?.pending === 0;
  },
  { timeout: 12000 }
);
```

**Alternative: Monitor fetch/XHR directly**
```typescript
const networkIdlePromise = page.waitForFunction(
  () => {
    const networkData = performance.getEntriesByType('resource');
    const recentCalls = networkData.filter(
      entry => Date.now() - entry.responseEnd < 2000
    );
    return recentCalls.length === 0;
  },
  { timeout: 10000, polling: 500 }
);
```

### Strategy C: Custom Condition (Most Flexible)

**Best for:** Detecting specific financial data patterns

```typescript
// Korean Stock Data Example: Wait until OHLCV data is present
await page.waitForFunction(
  () => {
    const ohlcvElements = document.querySelectorAll('[data-ohlcv]');
    if (ohlcvElements.length === 0) return false;

    // Verify data is not placeholder/skeleton
    const closePrice = parseFloat(ohlcvElements[3]?.textContent || '0');
    return closePrice > 1000; // Korean stocks typically > ₩1000
  },
  { timeout: 8000, polling: 200 }
);
```

### Strategy D: MutationObserver (Real-Time/Streaming)

**Best for:** Live updating content (stock tickers, real-time feeds)

```typescript
await page.evaluate(() => {
  return new Promise((resolve) => {
    let updateCount = 0;
    const targetElement = document.querySelector('[data-field="현재가"]');

    const observer = new MutationObserver(() => {
      updateCount++;
      // Resolve after 3 updates or 5 seconds
      if (updateCount >= 3) {
        observer.disconnect();
        resolve(true);
      }
    });

    observer.observe(targetElement, {
      characterData: true,
      subtree: true,
      childList: true
    });

    setTimeout(() => {
      observer.disconnect();
      resolve(updateCount > 0);
    }, 5000);
  });
});
```

### Strategy Selection Matrix

| Site Type | Best Strategy | Fallback | Timeout |
|-----------|---------------|----------|---------|
| KRX real-time ticker | MutationObserver | Network Idle | 5-8s |
| Financial dashboard | Network Idle | Element Visibility | 8-12s |
| Search/filter results | Custom Condition | Element Visibility | 6-10s |
| Historical data table | Element Visibility | Network Idle | 10-15s |
| Derivatives/options | Custom Condition | MutationObserver | 12-20s |
| Chart/graph rendering | Custom Condition | Network Idle | 15-30s |

---

## 6. Common SPA Patterns with Code Examples

### Pattern 1: React-Based Financial Dashboard

**Characteristics:**
- Bundle ends in `.js` from `_next/` or similar
- `__NEXT_DATA__` or `__INITIAL_STATE__` in source
- API calls during mount phase

```typescript
// KRX Data Labs pattern
async function scrapeReactDashboard(symbol: string) {
  const page = await browser.newPage();

  // Navigate to stock detail
  await page.goto(`https://data.krx.co.kr/contents/MDC/MDI/mdiload/doc/sample_krx/STDT_01/STDT01005000.html?marketType=STK&stockCode=${symbol}`, {
    waitUntil: 'networkidle2',
    timeout: 15000
  });

  // Wait for React to hydrate and render
  await page.waitForFunction(
    () => document.querySelectorAll('[data-field]').length > 5,
    { timeout: 10000 }
  );

  // Extract rendered data
  const data = await page.evaluate(() => {
    const fields = {};
    document.querySelectorAll('[data-field]').forEach(el => {
      const field = el.getAttribute('data-field');
      const value = el.textContent.trim();
      fields[field] = value;
    });
    return fields;
  });

  return data;
}
```

### Pattern 2: Vue-Based Real-Time Ticker

**Characteristics:**
- `v-app` or `v-container` in HTML
- Vue Store for state management
- WebSocket connections for live data

```typescript
// Real-time stock ticker pattern
async function scrapeVueRealTimeTicker(symbols: string[]) {
  const page = await browser.newPage();

  await page.goto('https://example-finance.kr/realtime', {
    waitUntil: 'domcontentloaded'
  });

  // Wait for Vue to initialize and establish WebSocket
  await page.waitForFunction(
    () => window.__vue?.$store?.state?.connected === true,
    { timeout: 5000 }
  );

  // Wait for initial data to arrive
  await page.waitForFunction(
    () => {
      const store = window.__vue?.$store?.state;
      return store?.tickers && Object.keys(store.tickers).length > 0;
    },
    { timeout: 8000 }
  );

  // Extract live ticker data
  const tickers = await page.evaluate((requestedSymbols) => {
    const store = window.__vue?.$store?.state;
    const result = {};

    requestedSymbols.forEach(symbol => {
      if (store.tickers[symbol]) {
        result[symbol] = {
          price: store.tickers[symbol].price,
          change: store.tickers[symbol].change,
          changePercent: store.tickers[symbol].changePercent,
          timestamp: store.tickers[symbol].timestamp
        };
      }
    });

    return result;
  }, symbols);

  return tickers;
}
```

### Pattern 3: Next.js Data Pre-fetching

**Characteristics:**
- `_next/data/{buildId}/` API responses
- JSON files instead of HTML for hydration
- Optimized for performance

```typescript
// Next.js pattern with direct API interception
async function scrapeNextJsData(symbol: string) {
  const page = await browser.newPage();

  // Intercept API calls to see the JSON structure
  let capturedData = null;

  page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('_next/data/') && url.endsWith('.json')) {
      try {
        capturedData = await response.json();
      } catch (e) {
        // Response already consumed
      }
    }
  });

  // Navigate triggers API call
  await page.goto(`https://example-nextjs-krx.kr/stocks/${symbol}`, {
    waitUntil: 'networkidle2'
  });

  // If we captured the JSON, return it directly
  if (capturedData) {
    return capturedData.pageProps?.data;
  }

  // Fallback: extract from rendered DOM
  return await page.evaluate(() => {
    const state = window.__NEXT_DATA__?.props?.pageProps;
    return state;
  });
}
```

### Pattern 4: GraphQL-Based Derivatives

**Characteristics:**
- `graphql` endpoint
- Complex nested queries
- Real-time subscriptions

```typescript
// GraphQL pattern (common in modern Korean fintech)
async function scrapeGraphQLDerivatives(symbol: string) {
  const page = await browser.newPage();

  let graphqlResponses = [];

  page.on('response', async (response) => {
    if (response.url().includes('/graphql')) {
      const data = await response.json();
      graphqlResponses.push(data);
    }
  });

  await page.goto(`https://example-krx-fintech.kr/derivatives/${symbol}`, {
    waitUntil: 'networkidle2'
  });

  // Wait for GraphQL to return data
  await page.waitForFunction(
    () => graphqlResponses.some(r => r.data?.derivatives !== null),
    { timeout: 10000 }
  );

  // Extract and flatten GraphQL response
  const derivativesData = graphqlResponses
    .find(r => r.data?.derivatives)
    ?.data?.derivatives;

  return derivativesData;
}
```

---

## 7. Timeout Handling Table and Recovery

| Scenario | Timeout | Recovery Action | Status |
|----------|---------|------------------|--------|
| Initial page load hangs | 15s | Retry navigation with `waitUntil: 'domcontentloaded'` | WARN |
| Element never appears | 10s | Fall back to API discovery | ERROR |
| Network idle never reached | 12s | Use element visibility instead | WARN |
| Partial data (50% loaded) | 8s (soft) → 15s (hard) | Extract partial + retry | PARTIAL |
| WebSocket connection fails | 5s | Use REST API fallback | ERROR |
| Page redirects loop | 3 redirects | Abort and return error | ERROR |
| Content loads then disappears (skeleton) | 2s grace → retry | Verify stability for 2s | RETRY |

### Recovery Code Template

```typescript
async function scrapeWithRecovery(url: string, options = {}) {
  const MAX_RETRIES = 3;
  const TIMEOUT_MS = 15000;

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const page = await browser.newPage();

      await page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: TIMEOUT_MS
      });

      // Primary wait strategy
      try {
        await page.waitForSelector('[data-field]', { timeout: 8000 });
      } catch (e) {
        // Fallback wait strategy
        console.warn('Primary wait failed, trying fallback...');
        await page.waitForFunction(
          () => document.body.innerText.length > 100,
          { timeout: 8000 }
        );
      }

      // Verify data is present and stable
      await new Promise(r => setTimeout(r, 2000)); // Grace period

      const data = await extractData(page);
      await page.close();

      return { success: true, data, attempt };

    } catch (error) {
      console.error(`Attempt ${attempt} failed:`, error.message);

      if (attempt < MAX_RETRIES) {
        const backoffMs = Math.pow(2, attempt) * 1000; // Exponential backoff
        await new Promise(r => setTimeout(r, backoffMs));
      } else {
        return {
          success: false,
          error: error.message,
          attempt
        };
      }
    }
  }
}
```

---

## 8. Performance Tips

### Tip 1: Use Headless Mode for Speed

```typescript
const browser = await puppeteer.launch({
  headless: true,  // Chrome headless mode (30-40% faster)
  args: [
    '--disable-dev-shm-usage',  // For Linux systems
    '--disable-gpu',             // Disable GPU rendering
    '--disable-extensions',      // Skip extensions
    '--disable-plugins'          // Skip plugins
  ]
});
```

### Tip 2: Disable Unnecessary Resources

```typescript
await page.setRequestInterception(true);

page.on('request', (request) => {
  const resourceType = request.resourceType();

  // Block heavy resources
  if (['image', 'stylesheet', 'font', 'media'].includes(resourceType)) {
    request.abort();
  } else if (['script', 'xhr', 'fetch'].includes(resourceType)) {
    request.continue(); // Allow data loading
  } else {
    request.continue();
  }
});
```

### Tip 3: Parallel Processing with Connection Pooling

```typescript
// For Korean sites: 3-5 concurrent pages is usually safe
const pool = [];
const POOL_SIZE = 3;

async function scrapeMultipleStocks(symbols: string[]) {
  const results = await Promise.all(
    symbols.map(async (symbol, index) => {
      // Wait for pool slot to open
      while (pool.length >= POOL_SIZE) {
        await new Promise(r => setTimeout(r, 100));
      }

      pool.push(symbol);

      try {
        return await scrapeSingleStock(symbol);
      } finally {
        pool.splice(pool.indexOf(symbol), 1);
      }
    })
  );

  return results;
}
```

### Tip 4: Cache and Reuse Pages

```typescript
const pageCache = new Map();

async function getOrCreatePage() {
  // Reuse page for multiple requests within 1 minute
  const cached = Array.from(pageCache.values())
    .find(p => Date.now() - p.created < 60000);

  if (cached) {
    return cached.page;
  }

  const page = await browser.newPage();
  pageCache.set(Date.now(), { page, created: Date.now() });

  return page;
}
```

### Tip 5: Monitor Memory Usage

```typescript
async function scrapeWithMemoryLimit(symbols: string[], limitMB = 500) {
  const memUsage = () => Math.round(process.memoryUsage().heapUsed / 1024 / 1024);

  const results = [];

  for (const symbol of symbols) {
    if (memUsage() > limitMB) {
      console.warn('Memory limit reached, forcing GC...');
      global.gc?.(); // Requires --expose-gc flag
      await new Promise(r => setTimeout(r, 1000));
    }

    const data = await scrapeSingleStock(symbol);
    results.push(data);
  }

  return results;
}
```

---

## 9. Output Format JSON Schema

Standard format for all dynamic scraping outputs:

```json
{
  "timestamp": "2025-01-29T14:30:00Z",
  "source_url": "https://example-krx.co.kr/stock/005930",
  "symbol": "005930",
  "name_ko": "삼성전자",
  "name_en": "Samsung Electronics",
  "scraped_at": "2025-01-29T14:30:05Z",
  "wait_strategy_used": "element_visibility",
  "wait_time_ms": 3200,
  "content_ready": true,
  "framework_detected": "react",
  "data": {
    "current_price": {
      "value": 70500,
      "currency": "KRW",
      "unit": "원",
      "raw_html": "70,500원"
    },
    "change": {
      "absolute": 500,
      "percent": 0.71,
      "direction": "up",
      "raw_html": "+500 (+0.71%)"
    },
    "volume": {
      "value": 12345678,
      "unit": "주",
      "raw_html": "12,345,678"
    },
    "market_cap_trillion_won": 435.2,
    "ohlc": {
      "open": 70000,
      "high": 71000,
      "low": 69800,
      "close": 70500
    },
    "timestamp": "2025-01-29T14:30:00Z"
  },
  "metadata": {
    "page_title": "삼성전자 - KRX 시세",
    "elements_found": 45,
    "dynamic_elements_count": 23,
    "wait_attempts": 1
  },
  "quality_score": 0.95,
  "errors": []
}
```

**Validation Rules:**
- `content_ready: true` only if all primary fields populated
- `quality_score >= 0.8` acceptable for analysis
- `timestamp` must be within 5 seconds of `scraped_at`
- Financial values must be positive (stocks > ₩1000 typically)

---

## 10. Fallback to API Discovery Criteria

When dynamic scraping fails or times out, attempt API discovery:

### Step 1: Detect API Endpoints

```typescript
async function discoverAPIs(page: Page) {
  const apis = [];

  page.on('response', (response) => {
    const url = response.url();
    const resourceType = response.request().resourceType();

    if (['xhr', 'fetch'].includes(resourceType)) {
      apis.push({
        url: url,
        status: response.status(),
        contentType: response.headers()['content-type']
      });
    }
  });

  // Trigger page interactions
  await page.goto(targetUrl);
  await new Promise(r => setTimeout(r, 5000));

  return apis.filter(api =>
    [200, 304].includes(api.status) &&
    api.url.includes('/api/') || api.url.includes('/graphql')
  );
}
```

### Step 2: Identify Data Endpoints

```typescript
// Look for patterns in discovered APIs
const dataEndpoints = apis.filter(api => {
  return (
    api.url.includes('stock') ||
    api.url.includes('quote') ||
    api.url.includes('data') ||
    api.url.includes('chart') ||
    api.url.includes('ticker')
  );
});
```

### Step 3: Map Parameters

```typescript
// Extract parameters used in original request
const parameters = new URL(dataEndpoints[0].url).searchParams;

// Common Korean financial API patterns
const expectedParams = {
  symbol: 'stock_code',
  date: 'date',
  period: 'period',
  type: 'data_type'
};
```

### Step 4: Test and Verify

```typescript
async function testAPIEndpoint(endpoint: string, params: Record<string, any>) {
  try {
    const response = await fetch(endpoint, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0...' // Mimic browser
      }
    });

    const data = await response.json();

    // Verify it contains financial data
    return {
      valid: hasFinancialData(data),
      endpoint,
      responseSize: JSON.stringify(data).length,
      sample: Object.keys(data).slice(0, 5)
    };
  } catch (error) {
    return { valid: false, error: error.message };
  }
}
```

### Fallback Decision Tree

```
┌─ Dynamic Scraping Failed?
│
├─ YES → Attempt API Discovery
│  │
│  ├─ APIs found?
│  │  ├─ YES → Test data endpoints
│  │  │  ├─ Valid API? → USE DIRECT API
│  │  │  └─ Invalid? → Return ERROR (not scrapable)
│  │  │
│  │  └─ NO APIs? → Return ERROR (requires auth/blocked)
│  │
│  └─ Errors during discovery? → Use static fallback
│
└─ NO → Return scraped data
```

---

## Korean Financial Site Examples

### Example 1: KRX Official Data Lab (React-based)

**URL:** `https://data.krx.co.kr/`

**Detection:**
```
[DYNAMIC_CANDIDATE] ✓
- React DevTools present
- Data loads from /api/tradeVolume*
- __NEXT_DATA__ present
```

**Scraping Strategy:**
```typescript
// Wait for React table component to render
await page.waitForSelector('table[role="grid"]', { timeout: 10000 });

// Extract OHLCV data from table cells
const stocks = await page.evaluate(() => {
  const rows = Array.from(document.querySelectorAll('tbody tr'));
  return rows.map(row => ({
    code: row.querySelector('td:nth-child(1)')?.textContent?.trim(),
    name: row.querySelector('td:nth-child(2)')?.textContent?.trim(),
    price: parseFloat(row.querySelector('td:nth-child(3)')?.textContent?.replace(/,/g, '') || 0),
    change: parseFloat(row.querySelector('td:nth-child(4)')?.textContent?.replace(/[+-%]/g, '') || 0),
    volume: parseInt(row.querySelector('td:nth-child(5)')?.textContent?.replace(/,/g, '') || 0)
  }));
});
```

### Example 2: Modern Broker Real-Time Ticker

**Detection:**
```
[DYNAMIC_CANDIDATE] ✓
- Vue.js framework (v-app detected)
- WebSocket for real-time updates
- Live price feeds (updates every 1-3 seconds)
```

**Scraping Strategy:**
```typescript
// Use MutationObserver to track live updates
await page.evaluate(() => {
  return new Promise((resolve) => {
    const priceElement = document.querySelector('[data-field="현재가"]');
    let updateCount = 0;

    const observer = new MutationObserver(() => {
      updateCount++;
      if (updateCount >= 2) { // Wait for 2 updates to confirm live
        observer.disconnect();
        resolve(true);
      }
    });

    observer.observe(priceElement, {
      characterData: true,
      subtree: true
    });

    setTimeout(() => resolve(updateCount > 0), 8000);
  });
});
```

### Example 3: Financial Dashboard with Charts

**Detection:**
```
[DYNAMIC_CANDIDATE] ✓
- Chart library (Chart.js, ECharts) with SVG/Canvas
- Multiple API calls for data
- Custom wait condition: chart must be rendered
```

**Scraping Strategy:**
```typescript
// Wait for chart canvas to be populated
await page.waitForFunction(() => {
  const canvas = document.querySelector('canvas');
  return canvas?.width > 0 && canvas?.height > 0;
}, { timeout: 15000 });

// Extract chart data from underlying API response
const chartData = await page.evaluate(() => {
  return window.__chartDataCache ||
         window.chartInstance?.data ||
         window.__INITIAL_STATE__?.chart;
});
```

---

## Debugging Checklist

Before giving up on dynamic scraping:

- [ ] Check Network tab for API endpoints
- [ ] Verify React/Vue/Angular DevTools extension sees rendered state
- [ ] Try `page.evaluate(() => document.body.innerHTML)` to see final HTML
- [ ] Look for `__NEXT_DATA__`, `__INITIAL_STATE__`, or similar globals
- [ ] Check for CSP (Content Security Policy) blocking XHR inspection
- [ ] Test with `headless: false` to see what browser sees
- [ ] Monitor console for JavaScript errors: `page.on('console', msg => console.log(msg))`
- [ ] Check if page requires specific referer or cookie header
- [ ] Verify User-Agent isn't being blocked (try real browser UA)
- [ ] Look for Cloudflare/WAF challenges in response headers

---

## References

- [Puppeteer Documentation](https://pptr.dev/)
- [Browser DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [KRX Data Lab API](https://data.krx.co.kr/)
- [React Performance Monitoring](https://react.dev/reference/react/Profiler)
- [Vue DevTools Integration](https://devtools.vuejs.org/)
