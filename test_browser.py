import asyncio, sys, traceback
from playwright.async_api import async_playwright

async def test():
    print("starting pw", flush=True)
    pw = await async_playwright().start()
    print("launching browser", flush=True)
    try:
        browser = await pw.chromium.launch(
            headless=False, slow_mo=50,
            args=["--no-sandbox","--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled",
                  "--start-maximized","--disable-extensions","--disable-popup-blocking"]
        )
        print("browser launched", flush=True)
        ctx = await browser.new_context(
            viewport={"width":1280,"height":800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()
        print("page created, going to youtube...", flush=True)
        await page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=60000)
        print("title:", await page.title(), flush=True)
        await browser.close()
    except Exception as e:
        print("ERROR:", type(e).__name__, flush=True)
        traceback.print_exc()
    finally:
        await pw.stop()

asyncio.run(test())
print("DONE", flush=True)
