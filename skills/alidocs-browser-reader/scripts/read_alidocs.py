#!/usr/bin/env python3
import argparse
import json
import re
import sys


def fail(message: str, code: int = 1) -> None:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    raise SystemExit(code)


def load_modules():
    try:
        import browser_cookie3  # type: ignore
    except ImportError:
        fail("missing dependency: browser-cookie3")

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        fail("missing dependency: playwright")

    return browser_cookie3, sync_playwright


def build_cookies(browser_cookie3):
    cookies = []
    jar = browser_cookie3.chrome(domain_name="dingtalk.com")
    for c in jar:
        if "dingtalk.com" not in c.domain:
            continue
        cookie = {
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path or "/",
            "httpOnly": False,
            "secure": bool(c.secure),
        }
        if c.expires:
            cookie["expires"] = float(c.expires)
        cookies.append(cookie)
    if not cookies:
        fail("no DingTalk cookies found in local Chrome profile")
    return cookies


def extract(url: str, max_chars: int):
    browser_cookie3, sync_playwright = load_modules()
    cookies = build_cookies(browser_cookie3)

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=chrome_path)
        context = browser.new_context(viewport={"width": 1440, "height": 2400})
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(12000)

        if len(page.frames) < 2:
            browser.close()
            fail("document preview frame not found; browser session may be stale")

        frame = page.frames[-1]
        selectors = [
            "article",
            "[class*=editor]",
            "[class*=content]",
            "body",
        ]
        text = ""
        for selector in selectors:
            locator = frame.locator(selector)
            if locator.count() == 0:
                continue
            try:
                candidate = locator.first.inner_text(timeout=15000).strip()
            except Exception:
                continue
            if len(candidate) > len(text):
                text = candidate
        if not text:
            browser.close()
            fail("preview frame loaded but article content was not found")

        title = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff\u2060-\u206f]", "", page.title()).strip()
        browser.close()

    if not text:
        fail("article content is empty")

    return {
        "ok": True,
        "title": title,
        "frame_url": frame.url,
        "text": text[:max_chars],
        "truncated": len(text) > max_chars,
    }


def main():
    parser = argparse.ArgumentParser(description="Read AliDocs content using local Chrome DingTalk cookies.")
    parser.add_argument("url", help="AliDocs or DingTalk docs URL")
    parser.add_argument("--max-chars", type=int, default=12000, help="Maximum number of text characters to return")
    args = parser.parse_args()

    result = extract(args.url, max(1000, args.max_chars))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
