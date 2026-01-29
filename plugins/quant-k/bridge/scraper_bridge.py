#!/usr/bin/env python3
"""
Browser Scraper Bridge - Playwright-based browser automation for web scraping

Usage:
    python scraper_bridge.py

Methods:
    - navigate(url) - Navigate to URL, return page title
    - snapshot() - Return page accessibility tree as simplified structure
    - evaluate(script) - Execute JavaScript and return result
    - extract_table(selector) - Extract table data as list of dicts
    - extract_list(selector, fields) - Extract list items with specified fields
    - close() - Close browser
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Browser, Page, Playwright
from base_bridge import BaseBridge, JsonRpcError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Error codes
BROWSER_ERROR = 1501
NAVIGATION_ERROR = 1502
EXTRACTION_ERROR = 1503
SCRIPT_ERROR = 1504


class ScraperBridge(BaseBridge):
    """Browser automation bridge using Playwright"""

    def __init__(self):
        super().__init__(19004)
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

        # Register scraper methods
        self.register_method("navigate", self.navigate)
        self.register_method("snapshot", self.snapshot)
        self.register_method("evaluate", self.evaluate)
        self.register_method("extract_table", self.extract_table)
        self.register_method("extract_list", self.extract_list)
        self.register_method("close", self.close_browser)

        logger.info("ScraperBridge initialized")

    async def _ensure_browser(self) -> None:
        """Lazy initialization of browser"""
        if self.browser is None:
            try:
                logger.info("Initializing Playwright browser...")
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                logger.info("Browser launched successfully")
            except Exception as e:
                logger.exception("Failed to launch browser")
                raise JsonRpcError(BROWSER_ERROR, f"Failed to launch browser: {str(e)}")

    async def _get_page(self) -> Page:
        """Get current page or create a new one"""
        await self._ensure_browser()

        if self.page is None:
            try:
                self.page = await self.browser.new_page()
                # Set reasonable timeout (30 seconds)
                self.page.set_default_timeout(30000)
                logger.info("New page created")
            except Exception as e:
                logger.exception("Failed to create page")
                raise JsonRpcError(BROWSER_ERROR, f"Failed to create page: {str(e)}")

        return self.page

    async def navigate(self, params: Dict) -> Dict:
        """
        Navigate to URL and return page title

        Args:
            params: {"url": "https://example.com", "wait_until": "load|domcontentloaded|networkidle"}

        Returns:
            {"title": "Page Title", "url": "https://example.com"}
        """
        url = params.get("url")
        if not url:
            raise JsonRpcError(-32602, "Invalid params: url required")

        wait_until = params.get("wait_until", "load")
        if wait_until not in ["load", "domcontentloaded", "networkidle"]:
            wait_until = "load"

        try:
            page = await self._get_page()
            logger.info(f"Navigating to {url}...")

            await page.goto(url, wait_until=wait_until)
            title = await page.title()
            current_url = page.url

            logger.info(f"Navigation successful: {title}")
            return {
                "title": title,
                "url": current_url
            }

        except Exception as e:
            logger.exception(f"Navigation failed for {url}")
            raise JsonRpcError(NAVIGATION_ERROR, f"Navigation failed: {str(e)}")

    async def snapshot(self, params: Dict) -> Dict:
        """
        Return page accessibility tree as simplified structure

        Args:
            params: {"max_depth": 3} (optional)

        Returns:
            {"snapshot": {...accessibility tree...}}
        """
        max_depth = params.get("max_depth", 3)

        try:
            page = await self._get_page()
            logger.info("Capturing page snapshot...")

            # Use JavaScript to get page structure instead of accessibility API
            script = """
            (maxDepth) => {
                function getNodeInfo(node, depth) {
                    if (depth >= maxDepth || !node) return null;

                    const info = {
                        tag: node.tagName?.toLowerCase() || 'text',
                        text: node.nodeType === 3 ? node.textContent?.trim() : null,
                    };

                    if (node.id) info.id = node.id;
                    if (node.className && typeof node.className === 'string') info.class = node.className;

                    if (node.children && node.children.length > 0) {
                        info.children = Array.from(node.children)
                            .map(child => getNodeInfo(child, depth + 1))
                            .filter(Boolean);
                    }

                    return info;
                }
                return getNodeInfo(document.body, 0);
            }
            """

            snapshot = await page.evaluate(script, max_depth)
            return {"snapshot": snapshot}

        except Exception as e:
            logger.exception("Failed to capture snapshot")
            raise JsonRpcError(EXTRACTION_ERROR, f"Snapshot failed: {str(e)}")

    def _simplify_tree(self, node: Optional[Dict], max_depth: int, current_depth: int = 0) -> Optional[Dict]:
        """Simplify accessibility tree to specified depth"""
        if node is None or current_depth >= max_depth:
            return None

        simplified = {
            "role": node.get("role"),
            "name": node.get("name"),
        }

        # Include value if present
        if "value" in node:
            simplified["value"] = node["value"]

        # Recursively process children
        children = node.get("children", [])
        if children and current_depth < max_depth - 1:
            simplified_children = []
            for child in children:
                simplified_child = self._simplify_tree(child, max_depth, current_depth + 1)
                if simplified_child:
                    simplified_children.append(simplified_child)
            if simplified_children:
                simplified["children"] = simplified_children

        return simplified

    async def evaluate(self, params: Dict) -> Dict:
        """
        Execute JavaScript in page context

        Args:
            params: {"script": "return document.title"}

        Returns:
            {"result": <script result>}
        """
        script = params.get("script")
        if not script:
            raise JsonRpcError(-32602, "Invalid params: script required")

        try:
            page = await self._get_page()
            logger.info("Evaluating script...")

            result = await page.evaluate(script)

            return {"result": result}

        except Exception as e:
            logger.exception("Script evaluation failed")
            raise JsonRpcError(SCRIPT_ERROR, f"Script evaluation failed: {str(e)}")

    async def extract_table(self, params: Dict) -> Dict:
        """
        Extract table data as list of dictionaries

        Args:
            params: {"selector": "table.data", "has_header": true}

        Returns:
            {"rows": [{"col1": "val1", "col2": "val2"}, ...]}
        """
        selector = params.get("selector", "table")
        has_header = params.get("has_header", True)

        try:
            page = await self._get_page()
            logger.info(f"Extracting table: {selector}")

            # Extract table data using JavaScript
            script = """
            (args) => {
                const [selector, hasHeader] = args;
                const table = document.querySelector(selector);
                if (!table) return null;

                const rows = Array.from(table.querySelectorAll('tr'));
                if (rows.length === 0) return [];

                let headers = [];
                let dataRows = rows;

                if (hasHeader && rows.length > 0) {
                    const headerRow = rows[0];
                    headers = Array.from(headerRow.querySelectorAll('th, td')).map(cell => cell.textContent.trim());
                    dataRows = rows.slice(1);
                }

                return dataRows.map(row => {
                    const cells = Array.from(row.querySelectorAll('td, th')).map(cell => cell.textContent.trim());

                    if (headers.length > 0) {
                        const obj = {};
                        cells.forEach((cell, idx) => {
                            const key = headers[idx] || `col_${idx}`;
                            obj[key] = cell;
                        });
                        return obj;
                    } else {
                        return cells;
                    }
                });
            }
            """

            result = await page.evaluate(script, [selector, has_header])

            if result is None:
                raise JsonRpcError(EXTRACTION_ERROR, f"Table not found: {selector}")

            logger.info(f"Extracted {len(result)} rows")
            return {"rows": result}

        except JsonRpcError:
            raise
        except Exception as e:
            logger.exception("Table extraction failed")
            raise JsonRpcError(EXTRACTION_ERROR, f"Table extraction failed: {str(e)}")

    async def extract_list(self, params: Dict) -> Dict:
        """
        Extract list items with specified fields

        Args:
            params: {
                "selector": "ul.items li",
                "fields": {
                    "title": ".title",
                    "price": ".price",
                    "link": "a@href"
                }
            }

        Returns:
            {"items": [{"title": "...", "price": "...", "link": "..."}, ...]}
        """
        selector = params.get("selector")
        fields = params.get("fields", {})

        if not selector:
            raise JsonRpcError(-32602, "Invalid params: selector required")

        try:
            page = await self._get_page()
            logger.info(f"Extracting list: {selector}")

            # Extract list data using JavaScript
            script = """
            (args) => {
                const [selector, fields] = args;
                const items = Array.from(document.querySelectorAll(selector));

                return items.map(item => {
                    const result = {};

                    for (const [key, fieldSelector] of Object.entries(fields)) {
                        // Handle attribute selectors like "a@href"
                        const match = fieldSelector.match(/^(.+?)@(.+)$/);

                        if (match) {
                            const [, elemSel, attr] = match;
                            const elem = elemSel ? item.querySelector(elemSel) : item;
                            result[key] = elem ? elem.getAttribute(attr) : null;
                        } else {
                            const elem = fieldSelector ? item.querySelector(fieldSelector) : item;
                            result[key] = elem ? elem.textContent.trim() : null;
                        }
                    }

                    return result;
                });
            }
            """

            result = await page.evaluate(script, [selector, fields])

            logger.info(f"Extracted {len(result)} items")
            return {"items": result}

        except Exception as e:
            logger.exception("List extraction failed")
            raise JsonRpcError(EXTRACTION_ERROR, f"List extraction failed: {str(e)}")

    async def close_browser(self, params: Dict) -> Dict:
        """
        Close browser and cleanup resources

        Returns:
            {"closed": true}
        """
        try:
            logger.info("Closing browser...")

            if self.page:
                await self.page.close()
                self.page = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            logger.info("Browser closed successfully")
            return {"closed": True}

        except Exception as e:
            logger.exception("Failed to close browser")
            raise JsonRpcError(BROWSER_ERROR, f"Failed to close browser: {str(e)}")


if __name__ == "__main__":
    bridge = ScraperBridge()
    bridge.run()
