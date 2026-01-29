#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { PythonBridge } from "./lib/python-bridge.js";
import * as path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Bridge instances
let krxBridge: PythonBridge | null = null;
let factorBridge: PythonBridge | null = null;
let screenerBridge: PythonBridge | null = null;
let scraperBridge: PythonBridge | null = null;

async function initBridges() {
  const bridgeDir = path.join(__dirname, "..", "bridge");

  krxBridge = new PythonBridge({
    port: 19001,
    bridgeScript: path.join(bridgeDir, "krx_bridge.py"),
  });

  factorBridge = new PythonBridge({
    port: 19002,
    bridgeScript: path.join(bridgeDir, "factor_bridge.py"),
  });

  screenerBridge = new PythonBridge({
    port: 19003,
    bridgeScript: path.join(bridgeDir, "screener_bridge.py"),
  });

  scraperBridge = new PythonBridge({
    port: 19004,
    bridgeScript: path.join(bridgeDir, "scraper_bridge.py"),
  });

  await Promise.all([
    krxBridge.start(),
    factorBridge.start(),
    screenerBridge.start(),
    scraperBridge.start(),
  ]);
}

const server = new Server(
  {
    name: "quant-k",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "krx_collect",
      description: "KRX 주식 데이터 수집 (종목 목록, OHLCV, 재무 지표)",
      inputSchema: {
        type: "object",
        properties: {
          market: {
            type: "string",
            enum: ["KOSPI", "KOSDAQ"],
            description: "시장 구분",
          },
          ticker: {
            type: "string",
            pattern: "^\\d{6}$",
            description: "종목 코드 (6자리)",
          },
          startDate: {
            type: "string",
            pattern: "^\\d{8}$",
            description: "시작일 (YYYYMMDD)",
          },
          endDate: {
            type: "string",
            pattern: "^\\d{8}$",
            description: "종료일 (YYYYMMDD)",
          },
          dataType: {
            type: "string",
            enum: ["tickers", "ohlcv", "fundamental", "marketcap"],
            description: "조회할 데이터 종류",
          },
          refresh: {
            type: "boolean",
            description: "캐시 무시 여부",
          },
        },
        required: ["dataType"],
      },
    },
    {
      name: "factor_analyze",
      description: "팩터 분석 및 종목 순위 계산",
      inputSchema: {
        type: "object",
        properties: {
          factors: {
            type: "array",
            items: {
              type: "string",
              enum: [
                "PER", "PBR", "PSR", "PCR", "EV_EBITDA",
                "MOM_1M", "MOM_3M", "MOM_6M", "MOM_12M",
                "ROE", "ROA", "GP_MARGIN", "OP_MARGIN",
                "SIZE", "SIZE_INV", "VOL_20D",
              ],
            },
            description: "분석할 팩터 목록",
          },
          market: {
            type: "string",
            enum: ["KOSPI", "KOSDAQ"],
          },
          date: {
            type: "string",
            pattern: "^\\d{8}$",
          },
          topN: {
            type: "number",
            minimum: 1,
            maximum: 100,
          },
          ticker: {
            type: "string",
            pattern: "^\\d{6}$",
            description: "특정 종목 팩터 노출도 조회",
          },
          weights: {
            type: "object",
            additionalProperties: { type: "number" },
            description: "복합 팩터 가중치",
          },
        },
        required: ["factors"],
      },
    },
    {
      name: "stock_screen",
      description: "조건 기반 종목 스크리닝",
      inputSchema: {
        type: "object",
        properties: {
          conditions: {
            type: "array",
            items: { type: "string" },
            description: "스크리닝 조건 (예: PER<10, ROE>15)",
          },
          market: {
            type: "string",
            enum: ["KOSPI", "KOSDAQ", "ALL"],
          },
          date: {
            type: "string",
            pattern: "^\\d{8}$",
          },
          sortBy: {
            type: "string",
          },
          sortOrder: {
            type: "string",
            enum: ["asc", "desc"],
          },
          limit: {
            type: "number",
            minimum: 1,
            maximum: 500,
          },
          save: {
            type: "string",
            description: "조건 저장 이름",
          },
          load: {
            type: "string",
            description: "저장된 조건 이름",
          },
        },
        required: ["conditions"],
      },
    },
    {
      name: "browser_scrape",
      description: "브라우저 자동화로 웹 데이터 수집 (네이버 금융, DART, KRX)",
      inputSchema: {
        type: "object",
        properties: {
          url: { type: "string", description: "수집할 URL" },
          action: {
            type: "string",
            enum: ["navigate", "snapshot", "extract_table", "extract_list", "evaluate", "close"],
            description: "실행할 작업"
          },
          selector: { type: "string", description: "CSS 셀렉터 (extract_table/extract_list용)" },
          fields: {
            type: "object",
            additionalProperties: { type: "string" },
            description: "필드 매핑 (extract_list용, 예: {name: '.title', link: 'a@href'})"
          },
          script: { type: "string", description: "JavaScript 코드 (evaluate용)" },
          hasHeader: { type: "boolean", description: "테이블 헤더 여부", default: true }
        },
        required: ["action"]
      }
    },
  ],
}));

// Helper function to wait for bridge connection with retry
async function waitForBridge(
  bridge: PythonBridge | null,
  bridgeName: string,
  maxWaitMs = 5000
): Promise<PythonBridge> {
  if (!bridge) {
    throw new Error(`${bridgeName} not initialized`);
  }

  if (bridge.isConnected()) {
    return bridge;
  }

  // Wait for connection with polling
  const startTime = Date.now();
  const pollInterval = 100;

  while (Date.now() - startTime < maxWaitMs) {
    if (bridge.isConnected()) {
      return bridge;
    }
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }

  throw new Error(`${bridgeName} connection timeout after ${maxWaitMs}ms`);
}

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "krx_collect": {
        const bridge = await waitForBridge(krxBridge, "KRX Bridge");

        const dataType = args?.dataType as string;
        let result: unknown;

        switch (dataType) {
          case "tickers":
            result = await bridge.call("get_ticker_list", {
              market: args?.market || "KOSPI",
            });
            break;
          case "ohlcv":
            result = await bridge.call("get_ohlcv", {
              ticker: args?.ticker,
              start: args?.startDate,
              end: args?.endDate,
            });
            break;
          case "fundamental":
            result = await bridge.call("get_fundamental", {
              ticker: args?.ticker,
              date: args?.date,
            });
            break;
          case "marketcap":
            result = await bridge.call("get_market_cap", {
              market: args?.market || "KOSPI",
              date: args?.date,
            });
            break;
          default:
            throw new Error(`Unknown data type: ${dataType}`);
        }

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "factor_analyze": {
        const bridge = await waitForBridge(factorBridge, "Factor Bridge");

        let result: unknown;

        if (args?.ticker) {
          // 특정 종목 팩터 노출도
          result = await bridge.call("get_factor_exposure", {
            ticker: args.ticker,
            factors: args?.factors,
            date: args?.date,
          });
        } else if (args?.weights && Object.keys(args.weights as object).length > 0) {
          // 복합 팩터 계산
          result = await bridge.call("calculate_composite", {
            factors: args?.factors,
            weights: args?.weights,
            market: args?.market || "KOSPI",
            date: args?.date,
          });
        } else {
          // 단일 팩터 순위
          const factors = args?.factors as string[];
          if (factors.length === 1) {
            result = await bridge.call("rank_by_factor", {
              factor: factors[0],
              market: args?.market || "KOSPI",
              date: args?.date,
              top_n: args?.topN || 20,
            });
          } else {
            // 여러 팩터 계산
            result = await bridge.call("calculate_composite", {
              factors: factors,
              market: args?.market || "KOSPI",
              date: args?.date,
            });
          }
        }

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "stock_screen": {
        const bridge = await waitForBridge(screenerBridge, "Screener Bridge");

        const result = await bridge.call("screen", {
          conditions: args?.conditions,
          market: args?.market || "KOSPI",
          date: args?.date,
          sort_by: args?.sortBy,
          sort_order: args?.sortOrder || "desc",
          limit: args?.limit || 100,
          save: args?.save,
          load: args?.load,
        });

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "browser_scrape": {
        const bridge = await waitForBridge(scraperBridge, "Scraper Bridge");

        const action = args?.action as string;
        let result: unknown;

        switch (action) {
          case "navigate":
            result = await bridge.call("navigate", { url: args?.url });
            break;
          case "snapshot":
            result = await bridge.call("snapshot", {});
            break;
          case "extract_table":
            result = await bridge.call("extract_table", {
              selector: args?.selector,
              has_header: args?.hasHeader ?? true
            });
            break;
          case "extract_list":
            result = await bridge.call("extract_list", {
              selector: args?.selector,
              fields: args?.fields
            });
            break;
          case "evaluate":
            result = await bridge.call("evaluate", { script: args?.script });
            break;
          case "close":
            result = await bridge.call("close", {});
            break;
          default:
            throw new Error(`Unknown action: ${action}`);
        }

        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ error: message }),
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  try {
    await initBridges();
    console.error("KRX Quant MCP Server started");

    const transport = new StdioServerTransport();
    await server.connect(transport);
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
}

main();
