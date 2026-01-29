# API Discovery Strategy for Korean Financial Sites

## Overview
API discovery identifies backend data sources before committing to DOM scraping. This strategy guides systematic detection, documentation, and utilization of APIs on Korean financial sites (KRX, Naver Finance, DART, etc.).

---

## 1. When to Use API Discovery

### Use This Strategy When:
- **Data appears dynamically** on page load (not in initial HTML)
- **JavaScript initializes with JSON objects** (`window.__INITIAL_STATE__`, `window.config`)
- **Network tab shows XHR/Fetch requests** (especially in DevTools)
- **Same data appears in multiple formats** (HTML, CSV, JSON API)
- **Pagination or filtering happens without page reload** (SPA/single-page app)
- **Performance matters** (APIs are 10-100x faster than DOM parsing)
- **Rate limiting is a concern** (API quota tracking vs unlimited DOM access)

### Do NOT Use When:
- Site explicitly prohibits API access (ToS, robots.txt)
- Data is only in rendered HTML (truly client-side only)
- No XHR/Fetch requests detected after page load
- Static content (no real-time updates)

**Fallback to DOM scraping** if no APIs discovered after 2-3 minutes of network monitoring.

---

## 2. Detection Criteria

### [API_CANDIDATE] Rules

Flag as API candidate if ANY of these apply:

| Signal | Detection Method | Priority |
|--------|------------------|----------|
| **XHR/Fetch request** | Network tab shows `xhr` or `fetch` resource type | HIGH |
| **JSON response** | Response content-type is `application/json` | HIGH |
| **URL structure** | Matches pattern: `/api/`, `/v1/`, `/data/`, `/rest/` | HIGH |
| **Request params** | Query string contains: `pageNum`, `limit`, `sort`, `query` | MEDIUM |
| **Response headers** | `X-API-Version`, `X-RateLimit-*` headers present | MEDIUM |
| **CORS headers** | `Access-Control-Allow-*` headers indicate cross-origin API | MEDIUM |
| **GraphQL endpoint** | POST to `/graphql`, response has `data` + `errors` fields | HIGH |
| **Initial state object** | Page JS contains `window.__INITIAL_STATE__` or `window.__data__` | MEDIUM |
| **Timing pattern** | Request fires 100-500ms after navigation (data load pattern) | LOW |
| **Size pattern** | Response < 100KB but shows 1000+ items (paginated API) | LOW |

### Priority Scoring
- **HIGH (3 points):** Definite API usage
- **MEDIUM (2 points):** Likely API usage
- **LOW (1 point):** Possible API usage

**Trigger API Discovery if score ≥ 3**

---

## 3. Workflow

### Phase 1: Start Network Monitoring

```bash
# Open DevTools Network tab BEFORE navigation
# Filter: All → XHR → Fetch
# Settings: Preserve log (prevent clearing on navigation)
```

### Phase 2: Navigate and Capture

1. Navigate to target site
2. Observe initial page load (5-10 seconds)
3. Interact with page (click filters, paginate, search)
4. **Capture at least 3-5 different request types**
5. Note any authentication headers (`Authorization`, `X-Auth-Token`)

### Phase 3: Analyze Requests

For each captured request, document:

| Field | Example |
|-------|---------|
| **Method** | GET, POST, OPTIONS |
| **URL** | `https://api.krx.co.kr/api/ticker/quotes` |
| **Query params** | `?symbol=005930&period=1d` |
| **Headers** | `Authorization: Bearer ...`, `X-Requested-With: XMLHttpRequest` |
| **Request body** | JSON payload if POST |
| **Response type** | `application/json`, `application/xml` |
| **Status codes** | 200, 400, 429, 500 |
| **Response size** | KB, number of items returned |

### Phase 4: Get Full Details

For each API endpoint identified:

1. **Fetch via curl/fetch** to confirm API is callable
2. **Test pagination** (if applicable): increment `page`, `offset`, `limit`
3. **Test authentication** (if protected): vary `Authorization` header
4. **Check rate limits** (if present): observe `X-RateLimit-*` response headers
5. **Document required params** vs optional

### Phase 5: Document API

Create schema file (example below in Section 8)

---

## 4. Common API Patterns

### REST API Pattern

**Endpoint structure:**
```
GET /api/v1/{resource}/{id}
GET /api/v1/{resource}?page=1&limit=50&sort=name
POST /api/v1/{resource}
PUT /api/v1/{resource}/{id}
DELETE /api/v1/{resource}/{id}
```

**Response format:**
```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "Samsung", "price": 70000 },
    { "id": 2, "name": "SK Hynix", "price": 98000 }
  ],
  "pageInfo": {
    "total": 2000,
    "page": 1,
    "pageSize": 50,
    "totalPages": 40
  }
}
```

### GraphQL Pattern

**Endpoint:**
```
POST /graphql
```

**Request:**
```json
{
  "query": "query { stocks(first: 10) { edges { node { id name price } } } }"
}
```

**Response:**
```json
{
  "data": {
    "stocks": {
      "edges": [
        { "node": { "id": "1", "name": "Samsung", "price": 70000 } }
      ]
    }
  }
}
```

### Pagination Patterns

| Pattern | Query Param | Example |
|---------|-------------|---------|
| Offset-based | `offset`, `limit` | `/api/stocks?offset=100&limit=50` |
| Page-based | `page`, `pageSize` | `/api/stocks?page=3&pageSize=50` |
| Cursor-based | `cursor`, `first` | `/api/stocks?cursor=abc123&first=50` |
| Keyset pagination | `after`, `limit` | `/api/stocks?after=1000&limit=50` |

**Korean sites favor:** Page-based and offset-based patterns

---

## 5. Authentication Handling

### Cookie-Based Auth (Most Korean Sites)

```javascript
// Auto-handled by browser
fetch('https://api.site.kr/data', {
  credentials: 'include'  // Send cookies
})
```

**Common Korean financial sites use:**
- `JSESSIONID` (Java sessions - DART, KRX)
- `_session_id` (Rails-based)
- `session_token` (custom)

**Detection:**
- Network tab → Find first API request → Response headers → Check `Set-Cookie`
- Store cookie, send in subsequent requests with `credentials: 'include'`

### Token-Based Auth (Bearer Token)

```javascript
fetch('https://api.site.kr/data', {
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...'
  }
})
```

**Korean API patterns:**
- KRX OpenAPI: Uses API key in header or query param
- Naver Finance: Bearer token from login
- DART: API key + secret

**Detection:**
- Look for `Authorization: Bearer` header
- Check for X-API-KEY header
- Inspect localStorage/sessionStorage for tokens

### CORS Preflight (OPTIONS)

Many Korean financial APIs require CORS preflight:

```
OPTIONS /api/ticker/quotes
Access-Control-Request-Method: GET
Access-Control-Request-Headers: authorization
```

Response should include:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: authorization
```

**If CORS is missing:** Must proxy through server-side to avoid browser blocking

---

## 6. Rate Limiting Detection

### Headers to Monitor

| Header | Indicates |
|--------|-----------|
| `X-RateLimit-Limit` | Max requests per period |
| `X-RateLimit-Remaining` | Requests left in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |
| `Retry-After` | Seconds to wait before retrying (on 429) |

### Common Korean API Limits

| API | Limit | Window |
|-----|-------|--------|
| KRX OpenAPI | 100 | per minute |
| Naver Finance | 1000 | per hour |
| DART OpenAPI | 50 | per second |
| KOSPI data | Varies | per day |

### Detection Strategy

1. Make 10 rapid requests
2. Track `X-RateLimit-Remaining` header decay
3. Calculate rate window from `X-RateLimit-Reset`
4. Extract limit from `X-RateLimit-Limit`

**Formula:** `Requests per period = Limit / (Reset - Current) * 1000`

---

## 7. GraphQL Introspection

### When to Use

If you detect GraphQL endpoint, run introspection to discover schema:

### Standard Introspection Query

```graphql
query IntrospectionQuery {
  __schema {
    types {
      name
      kind
      description
      fields {
        name
        type {
          name
          kind
        }
        args {
          name
          type { name }
          defaultValue
        }
      }
    }
    queryType { name }
    mutationType { name }
  }
}
```

### Request Format

```bash
curl -X POST https://api.site.kr/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"query":"<introspection_query_above>"}'
```

### Parse Response

Look for:
- Available types (e.g., `Stock`, `User`, `Quote`)
- Query entry points (e.g., `stocks`, `quotes`, `search`)
- Field arguments and their types
- Mutations available

---

## 8. Output Formats

### Discovery Mode (What APIs Exist)

**File:** `{site}-apis-discovered.md`

```markdown
# APIs Discovered on {Site}

## Summary
- Total endpoints: 5
- Auth type: Bearer token
- Rate limit: 1000 req/hour
- GraphQL: No

## Endpoints

### 1. Stock Quotes
- **URL:** `https://api.krx.co.kr/v1/ticker/quotes`
- **Method:** GET
- **Params:** `symbol` (required), `period` (optional: 1d, 1w, 1m)
- **Response:** JSON array of quote objects
- **Rate limit:** 100 req/min
- **Auth:** API key in `X-API-Key` header
- **Example:**
  ```bash
  curl 'https://api.krx.co.kr/v1/ticker/quotes?symbol=005930&period=1d' \
    -H 'X-API-Key: YOUR_KEY'
  ```

### 2. Company Info
- **URL:** `https://api.krx.co.kr/v1/company/{symbol}`
- **Method:** GET
- **Response:** Single company object
- **Auth:** API key

...
```

### Extraction Mode (Ready to Use)

**File:** `{site}-api-schema.json`

```json
{
  "site": "krx.co.kr",
  "discoveryDate": "2025-01-29",
  "apiVersion": "1.0",
  "authentication": {
    "type": "api-key",
    "header": "X-API-Key",
    "location": "header"
  },
  "baseUrl": "https://api.krx.co.kr/v1",
  "rateLimit": {
    "requestsPerMinute": 100,
    "requestsPerHour": 5000
  },
  "endpoints": [
    {
      "name": "quoteTickers",
      "path": "/ticker/quotes",
      "method": "GET",
      "description": "Get stock quotes",
      "parameters": [
        {
          "name": "symbol",
          "type": "string",
          "required": true,
          "example": "005930"
        },
        {
          "name": "period",
          "type": "string",
          "required": false,
          "enum": ["1d", "1w", "1m"],
          "default": "1d"
        }
      ],
      "response": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "symbol": { "type": "string" },
            "name": { "type": "string" },
            "price": { "type": "number" },
            "change": { "type": "number" },
            "changePercent": { "type": "number" },
            "volume": { "type": "number" },
            "timestamp": { "type": "string", "format": "iso8601" }
          }
        }
      },
      "example": "GET /ticker/quotes?symbol=005930&period=1d"
    }
  ]
}
```

---

## 9. Security Considerations

### DO

- [ ] Check robots.txt / API ToS before scraping
- [ ] Respect rate limits (use exponential backoff on 429)
- [ ] Cache responses locally (reduces API calls)
- [ ] Use server-side proxies for sensitive tokens
- [ ] Log API usage for debugging
- [ ] Implement circuit breakers (stop on repeated 5xx)

### DO NOT

- [ ] Store API keys in client-side code or git
- [ ] Make cross-origin API requests from browser (use CORS proxy)
- [ ] Ignore `Retry-After` headers
- [ ] Hammer API endpoints (respect rate limits)
- [ ] Expose authentication headers in client logs
- [ ] Share API credentials across team members

### Credential Management

```bash
# Use environment variables
export KRX_API_KEY="your_key_here"

# Or .env file (NOT in git)
# .env (in .gitignore)
KRX_API_KEY=your_key_here
NAVER_AUTH_TOKEN=your_token_here

# Load in code
const apiKey = process.env.KRX_API_KEY;
```

---

## 10. Fallback Criteria

### Switch to DOM Scraping When:

| Condition | Action |
|-----------|--------|
| **No XHR detected after 30 seconds** | Switch to DOM scraping |
| **All requests return 401/403** | API requires authentication not available |
| **Rate limit hit (429)** | Fall back to DOM + cache strategy |
| **API endpoint 404** | Endpoint may have changed, inspect DOM |
| **CORS blocks all requests** | Use server-side proxy or DOM scraping |
| **API requires JavaScript execution** | May need headless browser (Playwright) |
| **Anti-scraping active** | Switch to rotating proxies or API |

### Hybrid Approach

**Combine when appropriate:**
- Use API for real-time updates (prices, quotes)
- Use DOM scraping for one-time static data (company info, fundamentals)
- Cache API responses to reduce request volume

---

## Korean Financial API Examples

### KRX Open API

**Discovery URL:** https://data.krx.co.kr/contents/MDC/MDI/mdiLoader

**Pattern:**
```
GET /api/MDC_VOLATILITY/data
?bas_dd=20250129
&adj_tp_cd=1
&rn=100
```

**Response:** XML or JSON (specify in params)

**Rate limit:** 100 calls/minute per IP

**Auth:** API key registration required (https://data.krx.co.kr)

### Naver Finance API

**Discovery URL:** https://finance.naver.com/

**Common endpoints:**
- `/api/quote/stockInfo?symbol=005930` (Quote data)
- `/api/chart/getPriceChart?symbol=005930` (Historical prices)

**Pattern:** JSON response with `resultCode`, `data` fields

**Auth:** Session-based (Set-Cookie header)

### DART OpenAPI

**Discovery URL:** https://opendart.fss.or.kr/

**Pattern:**
```
GET /api/fnlttInstnot.json
?crtfc_key=YOUR_KEY
&corp_code=0000120271
&bsns_year=2024
```

**Response:** JSON with embedded result arrays

**Rate limit:** 50 calls/second (strict)

**Auth:** API key (get from FSS registration)

---

## Checklist

- [ ] Opened Network tab before navigation
- [ ] Captured at least 5 different API calls
- [ ] Identified authentication method
- [ ] Tested pagination (if applicable)
- [ ] Checked rate limit headers
- [ ] Documented all required headers
- [ ] Created discovery markdown file
- [ ] Created schema JSON file
- [ ] Tested API via curl/postman
- [ ] Verified response structure matches expectation
- [ ] Confirmed no CORS issues (or noted proxy requirement)
- [ ] Checked ToS for API usage restrictions
- [ ] Implemented rate limit handling
- [ ] Added fallback to DOM scraping

---

## References

- MDN: Network Tab Guide - https://developer.mozilla.org/en-US/docs/Tools/Network_Monitor
- GraphQL Introspection - https://graphql.org/learn/introspection/
- HTTP Status Codes - https://httpwg.org/specs/rfc7231.html#status.codes
- CORS - https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- REST API Best Practices - https://restfulapi.net/

---

**Version:** 1.0
**Last Updated:** 2025-01-29
**Maintained by:** quant-k browser-scraper strategy
