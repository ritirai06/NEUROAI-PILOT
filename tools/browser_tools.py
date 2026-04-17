"""
Browser automation — Playwright Chromium.
Compatible with uvicorn's asyncio event loop.
"""
import asyncio
import urllib.parse
import os
from playwright.async_api import async_playwright, Browser, Page

_browser: Browser | None = None
_page: Page | None = None
_pw = None


async def _get_page() -> Page:
    global _browser, _page, _pw

    if _page is not None:
        try:
            if not _page.is_closed():
                await _page.evaluate("1")
                return _page
        except Exception:
            pass
        _page = None

    if _browser is not None:
        try:
            ctx = await _browser.new_context(
                no_viewport=True,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            _page = await ctx.new_page()
            return _page
        except Exception:
            _browser = None
            _pw = None

    _pw = await async_playwright().start()
    _browser = await _pw.chromium.launch(
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--force-device-scale-factor=1",
        ]
    )
    ctx = await _browser.new_context(
        no_viewport=True,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    )
    _page = await ctx.new_page()
    await _page.bring_to_front()
    return _page


async def _goto(page: Page, url: str, timeout: int = 60000) -> None:
    last_err = None
    for wait in ("domcontentloaded", "commit", "load"):
        try:
            await page.goto(url, wait_until=wait, timeout=timeout)
            return
        except Exception as e:
            last_err = e
    raise last_err


# ── Navigation ────────────────────────────────────────────────────────────────

async def open_website(url: str) -> str:
    global _page
    if not url.startswith("http"):
        url = "https://" + url
    page = await _get_page()
    await page.bring_to_front()
    try:
        await _goto(page, url)
    except Exception as e:
        _page = None
        raise RuntimeError(f"Could not open {url}: {e}") from e
    try:
        title = await page.title()
    except Exception:
        title = ""
    return f"Opened: {url}" + (f" | {title}" if title else "")

async def go_back() -> str:
    page = await _get_page()
    await page.go_back()
    return f"Went back | Now: {page.url}"

async def go_forward() -> str:
    page = await _get_page()
    await page.go_forward()
    return f"Went forward | Now: {page.url}"

async def refresh_page() -> str:
    page = await _get_page()
    await page.reload(wait_until="domcontentloaded")
    return f"Page refreshed: {page.url}"

async def get_current_url() -> str:
    page = await _get_page()
    return f"Current URL: {page.url}"

async def get_page_title() -> str:
    page = await _get_page()
    title = await page.title()
    return f"Page title: {title}"

async def get_page_text() -> str:
    page = await _get_page()
    text = await page.inner_text("body")
    return text[:2000] if text else "No text found"

async def get_links() -> str:
    page = await _get_page()
    links = await page.query_selector_all("a[href]")
    hrefs = []
    for l in links[:15]:
        href = await l.get_attribute("href")
        text = (await l.inner_text()).strip()[:40]
        if href and href.startswith("http"):
            hrefs.append(f"{text} → {href}")
    return "\n".join(hrefs) if hrefs else "No links found"

async def zoom_page(level: int = 100) -> str:
    page = await _get_page()
    await page.evaluate(f"document.body.style.zoom = '{level}%'")
    return f"Page zoomed to {level}%"

async def take_browser_screenshot(filename: str = "browser_screenshot.png") -> str:
    page = await _get_page()
    path = os.path.join(os.getcwd(), filename)
    await page.screenshot(path=path, full_page=False)
    return f"Browser screenshot saved: {path}"

async def take_full_page_screenshot(filename: str = "fullpage.png") -> str:
    page = await _get_page()
    path = os.path.join(os.getcwd(), filename)
    await page.screenshot(path=path, full_page=True)
    return f"Full page screenshot saved: {path}"

# ── Search ────────────────────────────────────────────────────────────────────

async def search_youtube(query: str) -> str:
    global _page
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
    page = await _get_page()
    await page.bring_to_front()
    try:
        await _goto(page, url)
    except Exception as e:
        _page = None
        raise RuntimeError(f"Could not search YouTube: {e}") from e
    await page.wait_for_timeout(2000)
    return f"Searched YouTube for: {query}"

async def click_first_video() -> str:
    page = await _get_page()
    await page.wait_for_timeout(1500)
    for sel in [
        "ytd-video-renderer a#video-title",
        "ytd-rich-item-renderer a#video-title",
        "a#video-title",
        "ytd-video-renderer h3 a",
    ]:
        try:
            loc = page.locator(sel).first
            await loc.wait_for(state="visible", timeout=6000)
            title = (await loc.get_attribute("title") or await loc.inner_text() or "video").strip()[:60]
            await loc.scroll_into_view_if_needed()
            await loc.click()
            await page.wait_for_timeout(2000)
            return f"Playing: {title}"
        except Exception:
            continue
    try:
        links = await page.query_selector_all("a[href*='/watch?v=']")
        if links:
            await links[0].click()
            await page.wait_for_timeout(2000)
            return "Playing video"
    except Exception:
        pass
    return "Could not click video — please click manually"

async def search_google(query: str) -> str:
    global _page
    page = await _get_page()
    await page.bring_to_front()
    url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}&hl=en"
    try:
        await _goto(page, url)
    except Exception as e:
        _page = None
        raise RuntimeError(f"Could not search Google: {e}") from e
    try:
        btn = page.locator("button", has_text="Accept all").first
        if await btn.is_visible(timeout=2000):
            await btn.click()
            await page.wait_for_timeout(1000)
    except Exception:
        pass
    titles = []
    for sel in ["h3", ".LC20lb", ".DKV0Md"]:
        try:
            results = await page.query_selector_all(sel)
            for r in results[:5]:
                t = (await r.inner_text()).strip()
                if t and t not in titles:
                    titles.append(t)
            if titles:
                break
        except Exception:
            continue
    body = "\n".join(f"- {t}" for t in titles[:5]) if titles else "Search complete"
    return f"Google results for '{query}':\n{body}"

async def search_bing(query: str) -> str:
    global _page
    page = await _get_page()
    url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(query)}"
    try:
        await _goto(page, url)
    except Exception as e:
        _page = None
        raise RuntimeError(f"Could not search Bing: {e}") from e
    titles = []
    try:
        results = await page.query_selector_all("h2 a")
        for r in results[:5]:
            t = (await r.inner_text()).strip()
            if t:
                titles.append(t)
    except Exception:
        pass
    body = "\n".join(f"- {t}" for t in titles) if titles else "Search complete"
    return f"Bing results for '{query}':\n{body}"

async def search_amazon(query: str) -> str:
    global _page
    page = await _get_page()
    url = f"https://www.amazon.in/s?k={urllib.parse.quote_plus(query)}"
    try:
        await _goto(page, url)
    except Exception as e:
        _page = None
        raise RuntimeError(f"Could not search Amazon: {e}") from e
    await page.wait_for_timeout(2000)
    titles = []
    try:
        items = await page.query_selector_all("span.a-text-normal")
        for item in items[:5]:
            t = (await item.inner_text()).strip()
            if t:
                titles.append(t)
    except Exception:
        pass
    body = "\n".join(f"- {t}" for t in titles) if titles else "Search complete"
    return f"Amazon results for '{query}':\n{body}"

async def open_youtube() -> str:
    return await open_website("https://www.youtube.com")

async def open_gmail() -> str:
    return await open_website("https://mail.google.com")

async def open_github() -> str:
    return await open_website("https://github.com")

async def open_google_maps(location: str = "") -> str:
    url = f"https://www.google.com/maps/search/{urllib.parse.quote_plus(location)}" if location else "https://www.google.com/maps"
    return await open_website(url)

async def open_google_translate(text: str = "", target: str = "hi") -> str:
    url = f"https://translate.google.com/?sl=auto&tl={target}&text={urllib.parse.quote_plus(text)}&op=translate"
    return await open_website(url)

async def open_wikipedia(query: str) -> str:
    url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote_plus(query.replace(' ','_'))}"
    return await open_website(url)

# ── Interaction ───────────────────────────────────────────────────────────────

async def click(target: str) -> str:
    page = await _get_page()
    try:
        loc = page.get_by_text(target, exact=False)
        if await loc.count() > 0:
            await loc.first.click(timeout=6000)
            return f"Clicked: '{target}'"
    except Exception:
        pass
    await page.click(target, timeout=6000)
    return f"Clicked: '{target}'"

async def click_button(text: str) -> str:
    page = await _get_page()
    btn = page.get_by_role("button", name=text)
    if await btn.count() > 0:
        await btn.first.click()
        return f"Clicked button: '{text}'"
    return f"Button '{text}' not found"

async def type(text: str) -> str:
    page = await _get_page()
    await page.keyboard.type(text, delay=40)
    return f"Typed: {text}"

async def clear_and_type(selector: str, text: str) -> str:
    page = await _get_page()
    await page.fill(selector, text)
    return f"Filled '{selector}' with: {text}"

async def press_enter() -> str:
    page = await _get_page()
    await page.keyboard.press("Enter")
    return "Pressed Enter"

async def press_escape() -> str:
    page = await _get_page()
    await page.keyboard.press("Escape")
    return "Pressed Escape"

async def scroll(direction: str = "down", amount: int = 3) -> str:
    page = await _get_page()
    delta = 300 * amount * (1 if direction == "down" else -1)
    await page.mouse.wheel(0, delta)
    return f"Scrolled {direction} {amount}x"

async def scroll_to_top() -> str:
    page = await _get_page()
    await page.keyboard.press("Control+Home")
    return "Scrolled to top"

async def scroll_to_bottom() -> str:
    page = await _get_page()
    await page.keyboard.press("Control+End")
    return "Scrolled to bottom"

async def wait_for_element(selector: str, timeout: int = 10000) -> str:
    page = await _get_page()
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return f"Element found: {selector}"
    except Exception:
        return f"Element not found: {selector}"

async def hover(selector: str) -> str:
    page = await _get_page()
    await page.hover(selector)
    return f"Hovered: {selector}"

async def select_option(selector: str, value: str) -> str:
    page = await _get_page()
    await page.select_option(selector, value)
    return f"Selected '{value}' in {selector}"

# ── Forms & Data ──────────────────────────────────────────────────────────────

async def fill_form(fields: dict) -> str:
    page = await _get_page()
    filled, failed = [], []
    for sel, val in fields.items():
        try:
            await page.fill(sel, str(val))
            filled.append(sel)
        except Exception:
            try:
                await page.get_by_label(sel).fill(str(val))
                filled.append(sel)
            except Exception:
                failed.append(sel)
    out = (f"Filled: {', '.join(filled)}" if filled else "") + \
          (f" Failed: {', '.join(failed)}" if failed else "")
    return out or "Nothing filled"

async def scrape(url: str, selector: str = "p") -> str:
    page = await _get_page()
    if not url.startswith("http"):
        url = "https://" + url
    await _goto(page, url)
    els = await page.query_selector_all(selector)
    texts = [t for el in els[:8] if (t := (await el.inner_text()).strip())]
    return "\n".join(texts) if texts else "No content found"

async def get_table_data() -> str:
    page = await _get_page()
    try:
        rows = await page.query_selector_all("table tr")
        result = []
        for row in rows[:10]:
            cells = await row.query_selector_all("td, th")
            row_text = " | ".join([(await c.inner_text()).strip() for c in cells])
            if row_text.strip():
                result.append(row_text)
        return "\n".join(result) if result else "No table found"
    except Exception as e:
        return f"Table error: {e}"

async def send_email(to: str, subject: str = "Hello", body: str = "") -> str:
    url = (
        f"https://mail.google.com/mail/?view=cm&fs=1"
        f"&to={urllib.parse.quote(to)}"
        f"&su={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body)}"
    )
    page = await _get_page()
    await _goto(page, url)
    return f"Gmail compose opened for: {to}"

async def download_file(url: str, filename: str = None) -> str:
    import httpx as _httpx
    try:
        if not filename:
            filename = url.split("/")[-1].split("?")[0] or "download"
        path = os.path.join(os.getcwd(), filename)
        async with _httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
            r = await c.get(url)
            with open(path, "wb") as f:
                f.write(r.content)
        size = os.path.getsize(path) // 1024
        return f"Downloaded: {path} ({size}KB)"
    except Exception as e:
        return f"Download failed: {e}"

# ── Browser management ────────────────────────────────────────────────────────

async def open_new_tab(url: str = "about:blank") -> str:
    global _page
    if _browser is None:
        await _get_page()
    ctx = _page.context if _page else await _browser.new_context()
    _page = await ctx.new_page()
    if url != "about:blank":
        await _goto(_page, url)
    return f"New tab opened: {url}"

async def close_browser() -> str:
    global _browser, _page, _pw
    try:
        if _browser:
            await _browser.close()
    except Exception:
        pass
    try:
        if _pw:
            await _pw.stop()
    except Exception:
        pass
    _browser = None
    _page = None
    _pw = None
    return "Browser closed"

# ── New browser tools ────────────────────────────────────────────────────────────────

async def search_duckduckgo(query: str) -> str:
    page = await _get_page()
    url = f"https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}"
    await _goto(page, url)
    titles = []
    try:
        results = await page.query_selector_all("h2 a")
        for r in results[:5]:
            t = (await r.inner_text()).strip()
            if t:
                titles.append(t)
    except Exception:
        pass
    body = "\n".join(f"- {t}" for t in titles) if titles else "Search complete"
    return f"DuckDuckGo results for '{query}':\n{body}"

async def open_twitter() -> str:
    return await open_website("https://twitter.com")

async def open_reddit() -> str:
    return await open_website("https://www.reddit.com")

async def open_linkedin() -> str:
    return await open_website("https://www.linkedin.com")

async def open_stackoverflow() -> str:
    return await open_website("https://stackoverflow.com")

async def open_netflix() -> str:
    return await open_website("https://www.netflix.com")

async def open_spotify_web() -> str:
    return await open_website("https://open.spotify.com")

async def get_page_screenshot_base64() -> str:
    import base64
    page = await _get_page()
    data = await page.screenshot(type="png")
    b64 = base64.b64encode(data).decode()
    return f"data:image/png;base64,{b64[:100]}... ({len(b64)} chars)"

async def highlight_element(selector: str) -> str:
    page = await _get_page()
    try:
        await page.evaluate(
            f"""document.querySelector('{selector}').style.outline='3px solid red'"""
        )
        return f"Highlighted: {selector}"
    except Exception as e:
        return f"Highlight error: {e}"

async def count_elements(selector: str) -> str:
    page = await _get_page()
    els = await page.query_selector_all(selector)
    return f"Found {len(els)} elements matching '{selector}'"

async def get_element_text(selector: str) -> str:
    page = await _get_page()
    try:
        el = await page.query_selector(selector)
        if el:
            return (await el.inner_text()).strip()
        return f"Element not found: {selector}"
    except Exception as e:
        return f"Get element text error: {e}"

async def open_incognito(url: str = "about:blank") -> str:
    global _page
    if _browser is None:
        await _get_page()
    ctx = await _browser.new_context(
        no_viewport=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    _page = await ctx.new_page()
    if url != "about:blank":
        if not url.startswith("http"):
            url = "https://" + url
        await _goto(_page, url)
    return f"Incognito tab opened: {url}"
