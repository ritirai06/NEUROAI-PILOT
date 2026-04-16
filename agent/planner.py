"""
Planner v3 — converts natural language into explicit multi-step JSON plans.
YouTube: open_website → search_youtube → click_first_video (3 visible steps)
"""
import json, re, httpx
from agent.memory import Memory

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL      = "llama3.2:3b"

SYSTEM_PROMPT = """You are NeuroAI, a desktop automation assistant.
Convert the user command into a JSON execution plan with EXPLICIT steps.

SUPPORTED ACTIONS:
- open_app          params: {app}
- close_app         params: {app}
- open_website      params: {url}
- search_youtube    params: {query}
- click_first_video params: {}
- search_google     params: {query}
- search_duckduckgo params: {query}
- click             params: {target}
- type              params: {text}
- scroll            params: {direction, amount}
- take_screenshot   params: {filename}
- open_camera       params: {}
- click_photo       params: {}
- record_video      params: {duration}
- run_command       params: {cmd}
- get_weather       params: {city}
- get_news          params: {topic}
- get_country_info  params: {country}
- get_holidays      params: {country}
- get_ip_info       params: {ip}
- get_air_quality   params: {city}
- get_nasa_apod     params: {}
- get_random_dog    params: {}
- get_random_cat    params: {}
- get_moon_phase    params: {}
- uuid_generate     params: {}
- get_color_info    params: {hex_color}
- get_advice        params: {}
- get_trivia        params: {}
- open_twitter      params: {}
- open_reddit       params: {}
- open_linkedin     params: {}
- open_netflix      params: {}
- open_spotify_web  params: {}
- open_incognito    params: {url}
- open_task_manager params: {}
- clear_temp_files  params: {}
- empty_recycle_bin params: {}
- get_screen_resolution params: {}
- set_brightness    params: {level}
- get_startup_programs params: {}
- respond           params: {message}

RULES:
1. Output ONLY valid JSON — no explanation.
2. Format: {"steps": [{"action": "...", "params": {...}}], "summary": "..."}
3. For YouTube: ALWAYS use 3 steps: open_website(youtube.com) → search_youtube(query) → click_first_video()
4. Handle "and", "then", "after that" as step separators — NEVER skip steps.
5. Conversational input → respond action only.

EXAMPLE — "Open Chrome and play Arijit Singh":
{"steps":[
  {"action":"open_website","params":{"url":"https://www.youtube.com"}},
  {"action":"search_youtube","params":{"query":"Arijit Singh"}},
  {"action":"click_first_video","params":{}}
],"summary":"Play Arijit Singh on YouTube"}
"""

APP_ALIASES = {
    "chrome":"chrome","chome":"chrome","crome":"chrome","chromee":"chrome",
    "google chrome":"chrome","browser":"chrome",
    "firefox":"firefox","ff":"firefox",
    "vscode":"vscode","vs code":"vscode","visual studio code":"vscode","vsc":"vscode",
    "notepad":"notepad","note pad":"notepad",
    "calculator":"calculator","calc":"calculator","calcualtor":"calculator",
    "spotify":"spotify","spotfy":"spotify",
    "terminal":"terminal","cmd":"terminal","command prompt":"terminal","powershell":"terminal",
    "explorer":"explorer","file explorer":"explorer","files":"explorer",
    "paint":"paint","mspaint":"paint",
    "word":"word","excel":"excel","powerpoint":"powerpoint","ppt":"powerpoint",
    "outlook":"outlook","teams":"teams","discord":"discord",
    "telegram":"telegram","whatsapp":"whatsapp","zoom":"zoom",
    "vlc":"vlc","steam":"steam",
}

RE_OPEN    = re.compile(r'\b(open|launch|start|run|load)\b')
RE_CLOSE   = re.compile(r'\b(close|kill|quit|exit|stop|terminate)\b')
RE_SEARCH  = re.compile(r'\b(search|find|look up|google|lookup)\b')
RE_PLAY    = re.compile(r'\b(play|listen|watch|stream)\b')
RE_YOUTUBE = re.compile(r'\b(youtube|yt|you tube)\b')
RE_WEATHER = re.compile(r'\b(weather|temperature|forecast)\b')
RE_NEWS    = re.compile(r'\b(news|headlines|latest)\b')
RE_NEWS_CAT= re.compile(r'\b(law|legal|health|healthcare|medical|education|school|finance|economy|science|sports|cricket|politics|government|business|startup|entertainment|bollywood|world|india|breaking)\s+news\b')
RE_DIGEST  = re.compile(r'\b(daily digest|news digest|morning news|today news|all news)\b')
RE_BREAKING= re.compile(r'\b(breaking news|top news|latest news)\b')
RE_SHOT    = re.compile(r'\b(screenshot|screen shot|capture screen|snap)\b')
RE_CAMERA  = re.compile(r'\b(camera|webcam|photo|picture|selfie)\b')
RE_DUCK    = re.compile(r'\b(duckduckgo|ddg|duck duck go)\b')
RE_TWITTER = re.compile(r'\b(twitter|tweet|x\.com)\b')
RE_REDDIT  = re.compile(r'\b(reddit|subreddit)\b')
RE_LINKEDIN= re.compile(r'\b(linkedin)\b')
RE_NETFLIX = re.compile(r'\b(netflix)\b')
RE_SPOTIFY = re.compile(r'\b(spotify web|spotify browser|open spotify)\b')
RE_COUNTRY = re.compile(r'\b(country info|info about|tell me about)\b')
RE_HOLIDAY = re.compile(r'\b(holiday|holidays|public holiday)\b')
RE_TRIVIA  = re.compile(r'\b(trivia|quiz|fun fact)\b')
RE_ADVICE  = re.compile(r'\b(advice|give me advice|motivate)\b')
RE_DOG     = re.compile(r'\b(random dog|show.*dog|dog pic)\b')
RE_CAT     = re.compile(r'\b(random cat|show.*cat|cat pic)\b')
RE_NASA    = re.compile(r'\b(nasa|apod|astronomy picture)\b')
RE_UUID    = re.compile(r'\b(uuid|generate id|unique id)\b')
RE_MOON    = re.compile(r'\b(moon phase|moon|lunar)\b')
RE_IPINFO  = re.compile(r'\b(ip info|my ip|ip address info|lookup ip)\b')
RE_AIRQ    = re.compile(r'\b(air quality|aqi|pollution)\b')
RE_COLOR   = re.compile(r'\b(color info|colour info|hex color|color code)\b')
RE_RECYCLE = re.compile(r'\b(empty recycle|recycle bin|clear recycle)\b')
RE_TEMP    = re.compile(r'\b(clear temp|temp files|clean temp)\b')
RE_TASKMGR = re.compile(r'\b(task manager|taskmgr)\b')
RE_STARTUP = re.compile(r'\b(startup programs|startup apps)\b')
RE_BRIGHT  = re.compile(r'\b(brightness|screen brightness)\b')
RE_RESOLUTION = re.compile(r'\b(screen resolution|display resolution|resolution)\b')
RE_RECORD  = re.compile(r'\b(record video|record camera|video record)\b')
RE_CAMINFO = re.compile(r'\b(camera info|webcam info|camera details)\b')
RE_INCOG   = re.compile(r'\b(incognito|private.*tab|private.*window)\b')
RE_CALC    = re.compile(r'\b(calculate|compute|what is|solve|math)\b')
RE_DEFINE  = re.compile(r'\b(define|meaning of|what does.*mean|definition)\b')
RE_TRANS   = re.compile(r'\b(translate|translation)\b')
RE_JOKE    = re.compile(r'\b(joke|tell me a joke|make me laugh|funny)\b')
RE_QUOTE   = re.compile(r'\b(quote|inspire|motivational quote)\b')
RE_CRYPTO  = re.compile(r'\b(crypto|bitcoin|ethereum|btc|eth|coin price)\b')
RE_STOCK   = re.compile(r'\b(stock price|share price|stock of|nse|bse)\b')
RE_WIKI    = re.compile(r'\b(wikipedia|wiki|who is|what is.*wiki)\b')
RE_FOREX   = re.compile(r'\b(forex|exchange rate|currency rate|usd to|inr to)\b')
RE_QUAKE   = re.compile(r'\b(earthquake|seismic|tremor)\b')
RE_PASS    = re.compile(r'\b(generate password|random password|strong password|create password)\b')
RE_NUMFACT = re.compile(r'\b(number fact|fact about number|fun number)\b')
RE_DADJOKE = re.compile(r'\b(dad joke|pun)\b')
RE_CHUCK   = re.compile(r'\b(chuck norris)\b')
RE_SYSINFO = re.compile(r'\b(system info|system status|pc info|computer info)\b')
RE_BATTERY = re.compile(r'\b(battery|battery status|battery level)\b')
RE_WIFI    = re.compile(r'\b(wifi|wi-fi|network info|wifi info)\b')
RE_PING    = re.compile(r'\b(ping|ping test)\b')
RE_VOLUME  = re.compile(r'\b(volume|set volume|mute|unmute|volume up|volume down)\b')
RE_REMIND  = re.compile(r'\b(remind me|set reminder|reminder)\b')
RE_DATETIME= re.compile(r'\b(what time|current time|what date|today date|date and time)\b')
RE_NOTIFY  = re.compile(r'\b(notify|notification|show notification|alert me)\b')
RE_LOCK    = re.compile(r'\b(lock screen|lock pc|lock computer)\b')
RE_SLEEP   = re.compile(r'\b(sleep pc|sleep computer|hibernate)\b')
RE_SHUTDOWN= re.compile(r'\b(shutdown|shut down|power off)\b')
RE_RESTART = re.compile(r'\b(restart|reboot)\b')
RE_MAPS    = re.compile(r'\b(maps|google maps|directions|navigate to|location of)\b')
RE_WIKI_OPEN = re.compile(r'\b(open wikipedia|go to wikipedia|wikipedia page)\b')
RE_TRANSLATE_OPEN = re.compile(r'\b(open translate|google translate)\b')


def _find_app(text: str) -> str | None:
    t = text.lower()
    for alias, canonical in APP_ALIASES.items():
        if alias in t:
            return canonical
    return None


def _clean_query(text: str) -> str:
    t = text.lower()
    for pat in [
        r'\b(search|google|find|look up|play|watch|listen to|stream)\b\s*(for\s+)?',
        r'\bon\s+(youtube|google|yt)\b',
        r'\bopen\s+\w+\s+and\s+', r'\bthen\s+', r'\bafter\s+that\s+',
    ]:
        t = re.sub(pat, '', t)
    for alias in APP_ALIASES:
        t = t.replace(alias, '')
    return t.strip(' .,?!')


def _extract_url(text: str) -> str | None:
    m = re.search(r'(https?://[^\s]+|[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)', text.lower())
    if m:
        u = m.group(1)
        return u if u.startswith('http') else 'https://' + u
    return None


def _extract_city(text: str) -> str:
    t = text.lower()
    m = re.search(r'weather\s+(?:in|for|at|of)?\s*([a-zA-Z][a-zA-Z\s]{1,25})(?:\?|$|,|\s)', t)
    if m:
        return m.group(1).strip()
    t = re.sub(r'\b(weather|temperature|forecast|what|is|the|in|for|at|whats)\b', '', t)
    return t.strip(" '?!,") or "London"


def _step(action: str, **params) -> dict:
    return {"action": action, "params": params}


def _plan(steps: list, summary: str) -> dict:
    return {"steps": steps, "summary": summary}


def _youtube_steps(query: str) -> list:
    """Always returns 3 explicit YouTube steps."""
    return [
        _step("open_website",      url="https://www.youtube.com"),
        _step("search_youtube",    query=query),
        _step("click_first_video"),
    ]


class Planner:
    def __init__(self, memory: Memory):
        self.memory = memory

    async def plan(self, user_input: str) -> dict:
        result = self._rules(user_input)
        if result:
            return result
        try:
            return await self._llm(user_input)
        except Exception:
            return self._unknown(user_input)

    def _rules(self, raw: str) -> dict | None:
        t = raw.lower().strip()

        # SCREENSHOT
        if RE_SHOT.search(t):
            return _plan([_step("take_screenshot", filename="screenshot.png")], "Take screenshot")

        # CAMERA
        if RE_CAMERA.search(t):
            if RE_RECORD.search(t):
                m = re.search(r'(\d+)\s*(?:sec|second)', t)
                dur = int(m.group(1)) if m else 5
                return _plan([_step("record_video", duration=dur)], f"Record video ({dur}s)")
            if RE_CAMINFO.search(t):
                return _plan([_step("get_camera_info")], "Get camera info")
            steps = [_step("open_camera")]
            if re.search(r'\b(click|take|capture|snap)\b', t):
                steps.append(_step("click_photo"))
            return _plan(steps, "Open camera" + (" and take photo" if len(steps) > 1 else ""))

        # WEATHER
        if RE_WEATHER.search(t):
            city = _extract_city(t)
            return _plan([_step("get_weather", city=city)], f"Weather in {city}")

        # AIR QUALITY
        if RE_AIRQ.search(t):
            m = re.search(r'(?:air quality|aqi|pollution)\s+(?:in|for|at)?\s*([a-zA-Z][a-zA-Z\s]{1,25}?)(?:\?|$|,)', t)
            city = m.group(1).strip() if m else "Delhi"
            return _plan([_step("get_air_quality", city=city)], f"Air quality in {city}")

        # EARTHQUAKE
        if RE_QUAKE.search(t):
            return _plan([_step("get_earthquake_data")], "Recent earthquakes")

        # BREAKING NEWS
        if RE_BREAKING.search(t):
            return _plan([_step("get_breaking_news")], "Breaking news")

        # DAILY DIGEST
        if RE_DIGEST.search(t):
            return _plan([_step("get_daily_digest")], "Daily news digest")

        # NEWS BY CATEGORY (law, health, education, etc.)
        if RE_NEWS_CAT.search(t):
            m = re.search(r'\b(law|legal|health|healthcare|medical|education|school|finance|economy|science|sports|cricket|politics|government|business|startup|entertainment|bollywood|world|india|breaking)\b', t)
            cat_map = {
                "legal": "law", "healthcare": "health", "medical": "health",
                "school": "education", "economy": "finance",
                "cricket": "sports", "government": "politics",
                "startup": "business", "bollywood": "entertainment",
            }
            raw_cat = m.group(1) if m else "technology"
            category = cat_map.get(raw_cat, raw_cat)
            return _plan([_step("get_news_by_category", category=category)], f"{category.title()} news")

        # NEWS (general)
        if RE_NEWS.search(t):
            m = re.search(r'(?:news|headlines)\s+(?:about|on|for)?\s*([a-zA-Z\s]{2,30}?)(?:\?|$)', t)
            topic = m.group(1).strip() if m else "technology"
            return _plan([_step("get_news", topic=topic)], f"News: {topic}")

        # TRIVIA
        if RE_TRIVIA.search(t):
            return _plan([_step("get_trivia")], "Get trivia")

        # ADVICE
        if RE_ADVICE.search(t):
            return _plan([_step("get_advice")], "Get advice")

        # RANDOM DOG / CAT
        if RE_DOG.search(t):
            return _plan([_step("get_random_dog")], "Random dog image")
        if RE_CAT.search(t):
            return _plan([_step("get_random_cat")], "Random cat image")

        # NASA APOD
        if RE_NASA.search(t):
            return _plan([_step("get_nasa_apod")], "NASA Astronomy Picture of the Day")

        # UUID
        if RE_UUID.search(t):
            return _plan([_step("uuid_generate")], "Generate UUID")

        # MOON PHASE
        if RE_MOON.search(t):
            return _plan([_step("get_moon_phase")], "Moon phase")

        # IP INFO
        if RE_IPINFO.search(t):
            m = re.search(r'(?:lookup ip|ip info)\s+([\d.]+)', t)
            ip = m.group(1) if m else ""
            return _plan([_step("get_ip_info", ip=ip)], "IP info")

        # COLOR INFO
        if RE_COLOR.search(t):
            m = re.search(r'#?([0-9a-fA-F]{6})', t)
            hex_color = m.group(1) if m else "ff5733"
            return _plan([_step("get_color_info", hex_color=hex_color)], f"Color info: #{hex_color}")

        # HOLIDAYS
        if RE_HOLIDAY.search(t):
            m = re.search(r'holidays?\s+(?:in|for)?\s*([a-zA-Z]{2,3})', t)
            country = m.group(1).upper() if m else "US"
            return _plan([_step("get_holidays", country=country)], f"Holidays in {country}")

        # COUNTRY INFO
        if RE_COUNTRY.search(t):
            m = re.search(r'(?:info about|tell me about|country info)\s+([a-zA-Z\s]{2,30}?)(?:\?|$)', t)
            country = m.group(1).strip() if m else "India"
            return _plan([_step("get_country_info", country=country)], f"Country info: {country}")

        # SYSTEM TOOLS
        if RE_RECYCLE.search(t):
            return _plan([_step("empty_recycle_bin")], "Empty recycle bin")
        if RE_TEMP.search(t):
            return _plan([_step("clear_temp_files")], "Clear temp files")
        if RE_TASKMGR.search(t):
            return _plan([_step("open_task_manager")], "Open Task Manager")
        if RE_STARTUP.search(t):
            return _plan([_step("get_startup_programs")], "Get startup programs")
        if RE_RESOLUTION.search(t):
            return _plan([_step("get_screen_resolution")], "Get screen resolution")
        if RE_BRIGHT.search(t):
            m = re.search(r'(\d+)', t)
            level = int(m.group(1)) if m else 70
            return _plan([_step("set_brightness", level=level)], f"Set brightness to {level}%")

        # RUN COMMAND
        m = re.search(r'(?:run|execute)\s+(?:command\s*[:\-]?\s*)(.+)', t)
        if m:
            cmd = m.group(1).strip()
            return _plan([_step("run_command", cmd=cmd)], f"Run: {cmd}")

        # CLOSE APP
        if RE_CLOSE.search(t):
            app = _find_app(t)
            if app:
                return _plan([_step("close_app", app=app)], f"Close {app}")

        # INCOGNITO
        if RE_INCOG.search(t):
            url = _extract_url(t) or "about:blank"
            return _plan([_step("open_incognito", url=url)], f"Open incognito: {url}")

        # DUCKDUCKGO
        if RE_DUCK.search(t):
            q = _clean_query(t)
            return _plan([_step("search_duckduckgo", query=q or "search")], f"DuckDuckGo: {q}")

        # SOCIAL / STREAMING SITES
        if RE_TWITTER.search(t) and RE_OPEN.search(t):
            return _plan([_step("open_twitter")], "Open Twitter")
        if RE_REDDIT.search(t) and RE_OPEN.search(t):
            return _plan([_step("open_reddit")], "Open Reddit")
        if RE_LINKEDIN.search(t) and RE_OPEN.search(t):
            return _plan([_step("open_linkedin")], "Open LinkedIn")
        if RE_NETFLIX.search(t) and RE_OPEN.search(t):
            return _plan([_step("open_netflix")], "Open Netflix")
        if RE_SPOTIFY.search(t):
            return _plan([_step("open_spotify_web")], "Open Spotify Web")

        # YOUTUBE / PLAY — always 3 explicit steps
        if RE_YOUTUBE.search(t) or RE_PLAY.search(t):
            query = _clean_query(t)
            if not query or len(query) < 2:
                query = "music"
            return _plan(_youtube_steps(query), f"Play on YouTube: {query}")

        # OPEN APP + optional chained action
        if RE_OPEN.search(t):
            app = _find_app(t)
            url = _extract_url(t)

            # Browser app — use Playwright directly, never open_app for chrome
            if app in ("chrome", "firefox"):
                if RE_YOUTUBE.search(t) or RE_PLAY.search(t):
                    q = _clean_query(t)
                    return _plan(_youtube_steps(q or "music"), f"YouTube: {q}")
                if RE_SEARCH.search(t):
                    q = _clean_query(t)
                    return _plan([_step("search_google", query=q)], f"Search: {q}")
                if url:
                    return _plan([_step("open_website", url=url)], f"Open {url}")
                return _plan([_step("open_website", url="https://www.google.com")], "Open browser")

            if app:
                steps = [_step("open_app", app=app)]
                if RE_YOUTUBE.search(t) or RE_PLAY.search(t):
                    q = _clean_query(t)
                    steps += _youtube_steps(q or "music")
                    return _plan(steps, f"Open {app} → YouTube: {q}")
                if RE_SEARCH.search(t):
                    q = _clean_query(t)
                    if q:
                        steps.append(_step("search_google", query=q))
                        return _plan(steps, f"Open {app} → search {q}")
                if url:
                    steps.append(_step("open_website", url=url))
                    return _plan(steps, f"Open {app} → {url}")
                return _plan(steps, f"Open {app}")

            if url:
                return _plan([_step("open_website", url=url)], f"Open {url}")

        # GOOGLE SEARCH
        if RE_SEARCH.search(t) and not RE_YOUTUBE.search(t):
            q = _clean_query(t)
            if q and len(q) > 1:
                return _plan([_step("search_google", query=q)], f"Search: {q}")

        # BARE URL
        url = _extract_url(t)
        if url and re.search(r'\b(go to|visit|navigate|open)\b', t):
            return _plan([_step("open_website", url=url)], f"Open {url}")

        # EMAIL
        m = re.search(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', t)
        if m and re.search(r'\b(email|mail|send|compose)\b', t):
            to = m.group(1)
            subj = re.search(r'subject[:\s]+([^,]+)', t)
            return _plan([_step("open_website",
                url=f"https://mail.google.com/mail/?view=cm&fs=1&to={to}&su={subj.group(1).strip() if subj else 'Hello'}")],
                f"Compose email to {to}")

        # CALCULATE
        if RE_CALC.search(t):
            expr = re.sub(r'\b(calculate|compute|what is|solve|math)\b', '', t).strip(' ?')
            if expr:
                return _plan([_step("calculate", expression=expr)], f"Calculate: {expr}")

        # DEFINE WORD
        if RE_DEFINE.search(t):
            m = re.search(r'(?:define|meaning of|definition of|what does)\s+([a-zA-Z]+)', t)
            word = m.group(1) if m else t.split()[-1]
            return _plan([_step("define_word", word=word)], f"Define: {word}")

        # TRANSLATE
        if RE_TRANS.search(t):
            m = re.search(r'translate\s+(.+?)\s+(?:to|in)\s+([a-zA-Z]+)', t)
            if m:
                return _plan([_step("translate_text", text=m.group(1), target_lang=m.group(2)[:2])], f"Translate: {m.group(1)}")
            return _plan([_step("open_google_translate")], "Open Google Translate")

        # JOKE
        if RE_JOKE.search(t):
            if RE_DADJOKE.search(t):
                return _plan([_step("get_dad_joke")], "Dad joke")
            if RE_CHUCK.search(t):
                return _plan([_step("get_chuck_norris_joke")], "Chuck Norris joke")
            return _plan([_step("get_joke")], "Tell a joke")

        # QUOTE
        if RE_QUOTE.search(t):
            return _plan([_step("get_quote")], "Inspirational quote")

        # CRYPTO
        if RE_CRYPTO.search(t):
            m = re.search(r'\b(bitcoin|ethereum|btc|eth|dogecoin|doge|solana|sol|bnb|xrp)\b', t)
            coin = {"btc":"bitcoin","eth":"ethereum","doge":"dogecoin","sol":"solana"}.get(m.group(1), m.group(1)) if m else "bitcoin"
            return _plan([_step("get_crypto_price", coin=coin)], f"Crypto price: {coin}")

        # STOCK
        if RE_STOCK.search(t):
            m = re.search(r'(?:stock|share)\s+(?:of|price)?\s*([A-Z]{1,5})', raw)
            symbol = m.group(1) if m else "AAPL"
            return _plan([_step("get_stock_price", symbol=symbol)], f"Stock: {symbol}")

        # WIKIPEDIA
        if RE_WIKI.search(t) and not RE_WIKI_OPEN.search(t):
            q = re.sub(r'\b(wikipedia|wiki|who is|what is)\b', '', t).strip(' ?')
            if q:
                return _plan([_step("search_wikipedia", query=q)], f"Wikipedia: {q}")

        # FOREX
        if RE_FOREX.search(t):
            m = re.search(r'([A-Z]{3})\s+to\s+([A-Z]{3})', raw)
            if m:
                return _plan([_step("get_currency_rate", from_cur=m.group(1), to_cur=m.group(2))], f"Forex: {m.group(1)} to {m.group(2)}")
            return _plan([_step("get_forex_rates", base="USD")], "Forex rates")

        # PASSWORD
        if RE_PASS.search(t):
            m = re.search(r'(\d+)', t)
            length = int(m.group(1)) if m else 16
            return _plan([_step("generate_password", length=length)], f"Generate {length}-char password")

        # NUMBER FACT
        if RE_NUMFACT.search(t):
            m = re.search(r'(\d+)', t)
            n = int(m.group(1)) if m else None
            return _plan([_step("get_number_fact", number=n)], "Number fact")

        # SYSTEM INFO
        if RE_SYSINFO.search(t):
            return _plan([_step("get_system_info")], "System info")

        # BATTERY
        if RE_BATTERY.search(t):
            return _plan([_step("get_battery")], "Battery status")

        # WIFI
        if RE_WIFI.search(t):
            return _plan([_step("get_wifi_info")], "WiFi info")

        # PING
        if RE_PING.search(t):
            m = re.search(r'ping\s+([a-zA-Z0-9.\-]+)', t)
            host = m.group(1) if m else "google.com"
            return _plan([_step("ping", host=host)], f"Ping {host}")

        # VOLUME
        if RE_VOLUME.search(t):
            if re.search(r'\bmute\b', t):
                return _plan([_step("mute_volume")], "Mute volume")
            if re.search(r'\b(volume up|increase volume|louder)\b', t):
                return _plan([_step("volume_up")], "Volume up")
            if re.search(r'\b(volume down|decrease volume|quieter)\b', t):
                return _plan([_step("volume_down")], "Volume down")
            m = re.search(r'(\d+)', t)
            if m:
                return _plan([_step("set_volume", level=int(m.group(1)))], f"Set volume to {m.group(1)}%")

        # REMINDER
        if RE_REMIND.search(t):
            m_msg = re.search(r'remind me\s+(?:to\s+)?(.+?)\s+(?:in|after)\s+(\d+)', t)
            if m_msg:
                return _plan([_step("set_reminder", message=m_msg.group(1), seconds=int(m_msg.group(2)))], f"Reminder: {m_msg.group(1)}")

        # DATE/TIME
        if RE_DATETIME.search(t):
            return _plan([_step("get_datetime")], "Current date and time")

        # NOTIFICATION
        if RE_NOTIFY.search(t):
            m = re.search(r'(?:notify|alert|notification)\s+(?:me\s+)?(?:that\s+)?(.+)', t)
            msg = m.group(1).strip() if m else "NeuroAI notification"
            return _plan([_step("show_notification", title="NeuroAI", message=msg)], f"Notify: {msg}")

        # LOCK / SLEEP / SHUTDOWN / RESTART
        if RE_LOCK.search(t):
            return _plan([_step("lock_screen")], "Lock screen")
        if RE_SLEEP.search(t):
            return _plan([_step("sleep_pc")], "Sleep PC")
        if RE_SHUTDOWN.search(t):
            return _plan([_step("shutdown", delay=0)], "Shutdown PC")
        if RE_RESTART.search(t):
            return _plan([_step("restart", delay=0)], "Restart PC")

        # MAPS
        if RE_MAPS.search(t):
            m = re.search(r'(?:maps|directions|navigate to|location of)\s+(.+)', t)
            loc = m.group(1).strip() if m else ""
            return _plan([_step("open_google_maps", location=loc)], f"Maps: {loc}")

        # OPEN TRANSLATE
        if RE_TRANSLATE_OPEN.search(t):
            return _plan([_step("open_google_translate")], "Open Google Translate")

        return None

    async def _llm(self, user_input: str) -> dict:
        history = self.memory.get_recent(2)
        ctx = ("Recent:\n" + "\n".join(f"- {h['input']}" for h in history) + "\n\n") if history else ""
        payload = {
            "model": MODEL,
            "prompt": f"{SYSTEM_PROMPT}\n\n{ctx}User: {user_input}",
            "stream": False, "format": "json",
            "options": {"temperature": 0.1, "num_predict": 400, "num_ctx": 1024},
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            data = resp.json()
            if "error" in data:
                return self._unknown(user_input)
            return self._parse_llm(data.get("response", "{}"))

    def _parse_llm(self, raw: str) -> dict:
        try:
            data = json.loads(raw)
            if "steps" in data:
                steps = []
                for s in data["steps"]:
                    if "action" in s:
                        steps.append(s)
                    elif "tool" in s:
                        params = {k: v for k, v in s.items() if k != "tool"}
                        steps.append({"action": s["tool"], "params": params})
                return {"steps": steps, "summary": data.get("summary", raw[:60])}
        except Exception:
            pass
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            try:
                return self._parse_llm(m.group())
            except Exception:
                pass
        return _plan([_step("respond", message=raw[:300])], raw[:60])

    def _unknown(self, text: str) -> dict:
        r = self._rules(text)
        if r:
            return r
        return _plan([_step("respond", message=(
            "I couldn't understand that. Try:\n"
            "• 'Open Chrome and play Arijit Singh'\n"
            "• 'Open camera and take photo'\n"
            "• 'Search Python tutorials'\n"
            "• 'Weather in London'\n"
            "• 'Open VS Code'"
        ))], "Unknown command")
