#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except Exception as e:
    print(f"Playwright import failed: {e}", file=sys.stderr)
    sys.exit(2)

USAGE = "python3 render_html_to_png.py INPUT.html [OUTPUT.png]"

async def main(inp: Path, out: Path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 1280}, device_scale_factor=1.5)
        await page.goto(inp.resolve().as_uri(), wait_until="networkidle")
        await page.screenshot(path=str(out), full_page=True)
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    inp = Path(sys.argv[1]).expanduser()
    if not inp.exists():
        print(f"Input not found: {inp}", file=sys.stderr)
        sys.exit(1)
    out = Path(sys.argv[2]).expanduser() if len(sys.argv) == 3 else inp.with_suffix('.png')
    asyncio.run(main(inp, out))
    print(out)
