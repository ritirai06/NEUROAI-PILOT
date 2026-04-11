import asyncio, traceback

async def test():
    from tools.browser_tools import search_google
    print("Testing search_google...", flush=True)
    try:
        r = await search_google("python tutorials")
        print("OK:", r[:200], flush=True)
    except Exception as e:
        print("ERROR:", type(e).__name__, str(e)[:500], flush=True)
        traceback.print_exc()

asyncio.run(test())
