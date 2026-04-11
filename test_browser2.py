import asyncio, sys, traceback

async def test():
    # Import after event loop is running (same as uvicorn)
    from tools.browser_tools import open_website, search_youtube, click_first_video

    print("Testing open_website...", flush=True)
    try:
        r = await open_website("https://www.youtube.com")
        print("open_website OK:", r, flush=True)
    except Exception as e:
        print("open_website ERROR:", e, flush=True)
        traceback.print_exc()

    print("Testing search_youtube...", flush=True)
    try:
        r = await search_youtube("arijit singh")
        print("search_youtube OK:", r, flush=True)
    except Exception as e:
        print("search_youtube ERROR:", e, flush=True)
        traceback.print_exc()

    print("Testing click_first_video...", flush=True)
    try:
        r = await click_first_video()
        print("click_first_video OK:", r, flush=True)
    except Exception as e:
        print("click_first_video ERROR:", e, flush=True)
        traceback.print_exc()

asyncio.run(test())
