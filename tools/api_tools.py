import httpx, re, json

# ── Weather & News ────────────────────────────────────────────────────────────

async def get_weather(city: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://wttr.in/{city.replace(' ', '+')}?format=3")
            return r.text.strip()
    except Exception as e:
        return f"Weather failed: {e}"

async def get_weather_detailed(city: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://wttr.in/{city.replace(' ', '+')}?format=j1")
            d = r.json()
            cur = d["current_condition"][0]
            return (
                f"Weather in {city}:\n"
                f"Temp: {cur['temp_C']}C / {cur['temp_F']}F\n"
                f"Feels like: {cur['FeelsLikeC']}C\n"
                f"Condition: {cur['weatherDesc'][0]['value']}\n"
                f"Humidity: {cur['humidity']}% | Wind: {cur['windspeedKmph']} km/h\n"
                f"Visibility: {cur['visibility']} km"
            )
    except Exception as e:
        return f"Detailed weather failed: {e}"

async def get_news(topic: str = "technology") -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}")
            titles = re.findall(r'<title>(.*?)</title>', r.text)[1:6]
            return "\n".join(f"• {t}" for t in titles) if titles else "No news found"
    except Exception as e:
        return f"News failed: {e}"

# ── Finance ───────────────────────────────────────────────────────────────────

async def get_crypto_price(coin: str = "bitcoin") -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin.lower()}&vs_currencies=usd,inr")
            d = r.json()
            if coin.lower() not in d:
                return f"Coin '{coin}' not found"
            prices = d[coin.lower()]
            return f"{coin.title()}: ${prices.get('usd','?')} USD | ₹{prices.get('inr','?')} INR"
    except Exception as e:
        return f"Crypto price failed: {e}"

async def get_currency_rate(from_cur: str = "USD", to_cur: str = "INR") -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://open.er-api.com/v6/latest/{from_cur.upper()}")
            d = r.json()
            rate = d["rates"].get(to_cur.upper())
            if not rate:
                return f"Currency '{to_cur}' not found"
            return f"1 {from_cur.upper()} = {rate:.4f} {to_cur.upper()}"
    except Exception as e:
        return f"Currency rate failed: {e}"

async def get_stock_price(symbol: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}?interval=1d&range=1d",
                            headers={"User-Agent": "Mozilla/5.0"})
            d = r.json()
            meta = d["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", "N/A")
            prev  = meta.get("previousClose", "N/A")
            change = round(float(price) - float(prev), 2) if price != "N/A" else "N/A"
            return f"{symbol.upper()}: ${price} | Change: {change} | Prev close: ${prev}"
    except Exception as e:
        return f"Stock price failed: {e}"

# ── Dictionary & Language ─────────────────────────────────────────────────────

async def define_word(word: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}")
            d = r.json()
            if isinstance(d, list) and d:
                entry    = d[0]
                meanings = entry.get("meanings", [])
                result   = f"Word: {word}\n"
                for m in meanings[:2]:
                    pos  = m.get("partOfSpeech","")
                    defs = m.get("definitions",[])
                    if defs:
                        result += f"{pos}: {defs[0]['definition']}\n"
                        if defs[0].get("example"):
                            result += f'  Example: "{defs[0]["example"]}"\n'
                return result.strip()
            return f"No definition found for '{word}'"
    except Exception as e:
        return f"Dictionary failed: {e}"

async def translate_text(text: str, target_lang: str = "hi") -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={httpx.URL(text)}"
            r   = await c.get(f"https://translate.googleapis.com/translate_a/single",
                              params={"client":"gtx","sl":"auto","tl":target_lang,"dt":"t","q":text})
            d = r.json()
            translated = "".join(part[0] for part in d[0] if part[0])
            return f"Translated ({target_lang}): {translated}"
    except Exception as e:
        return f"Translation failed: {e}"

async def get_synonyms(word: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}")
            d = r.json()
            if isinstance(d, list) and d:
                syns = []
                for m in d[0].get("meanings", []):
                    for defn in m.get("definitions", []):
                        syns.extend(defn.get("synonyms", []))
                if syns:
                    return f"Synonyms for '{word}': {', '.join(syns[:10])}"
            return f"No synonyms found for '{word}'"
    except Exception as e:
        return f"Synonyms failed: {e}"

# ── Fun & Utility ─────────────────────────────────────────────────────────────

async def get_joke() -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get("https://official-joke-api.appspot.com/random_joke")
            d = r.json()
            return f"{d['setup']}\n... {d['punchline']}"
    except Exception as e:
        return f"Joke failed: {e}"

async def get_quote() -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get("https://zenquotes.io/api/random")
            d = r.json()
            return f'"{d[0]["q"]}"\n— {d[0]["a"]}'
    except Exception as e:
        return f"Quote failed: {e}"

async def get_fact() -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get("https://uselessfacts.jsph.pl/api/v2/facts/random?language=en")
            d = r.json()
            return f"Fact: {d['text']}"
    except Exception as e:
        return f"Fact failed: {e}"

async def get_time_in_city(city: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://worldtimeapi.org/api/timezone")
            zones = r.json()
            match = [z for z in zones if city.lower().replace(" ","_") in z.lower()]
            if not match:
                return f"Timezone not found for '{city}'"
            r2 = await c.get(f"https://worldtimeapi.org/api/timezone/{match[0]}")
            d  = r2.json()
            dt = d["datetime"][:19].replace("T"," ")
            return f"Time in {city}: {dt} ({match[0]})"
    except Exception as e:
        return f"Time lookup failed: {e}"

async def shorten_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://tinyurl.com/api-create.php?url={url}")
            return f"Short URL: {r.text.strip()}"
    except Exception as e:
        return f"URL shortener failed: {e}"

async def get_qr_code(text: str) -> str:
    try:
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={httpx.URL(text)}"
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://api.qrserver.com/v1/create-qr-code/",
                            params={"size":"300x300","data":text})
            path = "qrcode.png"
            with open(path, "wb") as f:
                f.write(r.content)
            return f"QR code saved: {path}"
    except Exception as e:
        return f"QR code failed: {e}"

async def search_wikipedia(query: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get("https://en.wikipedia.org/api/rest_v1/page/summary/" +
                            query.replace(" ","_"),
                            headers={"User-Agent":"NeuroAI/3.0"})
            d = r.json()
            if d.get("type") == "disambiguation":
                return f"'{query}' is ambiguous. Try a more specific term."
            extract = d.get("extract","")[:500]
            return f"Wikipedia: {d.get('title','')}\n{extract}"
    except Exception as e:
        return f"Wikipedia failed: {e}"

async def get_github_user(username: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://api.github.com/users/{username}",
                            headers={"User-Agent":"NeuroAI/3.0"})
            d = r.json()
            if "message" in d:
                return f"GitHub user '{username}' not found"
            return (f"GitHub: {d['login']}\n"
                    f"Name: {d.get('name','N/A')} | Bio: {d.get('bio','N/A')}\n"
                    f"Repos: {d['public_repos']} | Followers: {d['followers']} | Following: {d['following']}\n"
                    f"URL: {d['html_url']}")
    except Exception as e:
        return f"GitHub lookup failed: {e}"

async def api_get(url: str, headers: dict = None) -> str:
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(url, headers=headers or {})
            return r.text[:2000]
    except Exception as e:
        return f"GET failed: {e}"

async def api_post(url: str, data: dict = None) -> str:
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(url, json=data or {})
            return r.text[:2000]
    except Exception as e:
        return f"POST failed: {e}"

async def check_website_status(url: str) -> str:
    try:
        if not url.startswith("http"):
            url = "https://" + url
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(url)
            return f"{url} is UP | Status: {r.status_code} | Response: {r.elapsed.total_seconds():.2f}s"
    except Exception as e:
        return f"{url} is DOWN | Error: {e}"

# ── New API tools ───────────────────────────────────────────────────────────────────

async def get_ip_info(ip: str = "") -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://ipinfo.io/{ip}/json")
            d = r.json()
            return (f"IP: {d.get('ip')} | City: {d.get('city')} | Region: {d.get('region')}\n"
                    f"Country: {d.get('country')} | Org: {d.get('org')} | Timezone: {d.get('timezone')}")
    except Exception as e:
        return f"IP info failed: {e}"

async def get_moon_phase() -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get("https://wttr.in/Moon?format=%m+%D")
            return f"Moon phase: {r.text.strip()}"
    except Exception as e:
        return f"Moon phase failed: {e}"

async def get_nasa_apod() -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY")
            d = r.json()
            return f"NASA APOD: {d.get('title')}\n{d.get('explanation','')[:300]}\nURL: {d.get('url','')}"
    except Exception as e:
        return f"NASA APOD failed: {e}"

async def get_random_dog() -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get("https://dog.ceo/api/breeds/image/random")
            return f"Random dog: {r.json().get('message','')}"
    except Exception as e:
        return f"Random dog failed: {e}"

async def get_random_cat() -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get("https://api.thecatapi.com/v1/images/search")
            d = r.json()
            return f"Random cat: {d[0].get('url','') if d else 'Not found'}"
    except Exception as e:
        return f"Random cat failed: {e}"

async def get_country_info(country: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://restcountries.com/v3.1/name/{country}")
            d = r.json()[0]
            cap = d.get("capital", [""])[0]
            pop = d.get("population", 0)
            return (f"Country: {d['name']['common']} | Capital: {cap}\n"
                    f"Population: {pop:,} | Region: {d.get('region')} | Currency: "
                    + ", ".join(v.get('name','') for v in d.get('currencies',{}).values()))
    except Exception as e:
        return f"Country info failed: {e}"

async def get_holidays(country: str = "US", year: int = 2025) -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country.upper()}")
            holidays = r.json()[:10]
            return "\n".join(f"{h['date']}: {h['name']}" for h in holidays)
    except Exception as e:
        return f"Holidays failed: {e}"

async def get_air_quality(city: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://wttr.in/{city.replace(' ','+')}?format=j1")
            d = r.json()
            # wttr doesn't have AQI; use nearest_area as fallback info
            area = d.get("nearest_area", [{}])[0]
            name = area.get("areaName", [{}])[0].get("value", city)
            return f"Air quality data for {name}: Use dedicated AQI API for precise readings. Weather: {d['current_condition'][0]['weatherDesc'][0]['value']}"
    except Exception as e:
        return f"Air quality failed: {e}"

async def uuid_generate() -> str:
    import uuid
    return f"UUID: {uuid.uuid4()}"

async def get_color_info(hex_color: str) -> str:
    try:
        hex_color = hex_color.lstrip("#")
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"https://www.thecolorapi.com/id?hex={hex_color}")
            d = r.json()
            return (f"Color: {d['name']['value']} | Hex: #{hex_color}\n"
                    f"RGB: {d['rgb']['value']} | HSL: {d['hsl']['value']}")
    except Exception as e:
        return f"Color info failed: {e}"

async def get_advice() -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get("https://api.adviceslip.com/advice")
            return f"Advice: {r.json()['slip']['advice']}"
    except Exception as e:
        return f"Advice failed: {e}"

async def get_trivia(category: str = "general") -> str:
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get("https://opentdb.com/api.php?amount=1&type=multiple")
            d = r.json()
            q = d["results"][0]
            return f"Trivia ({q['category']}):\nQ: {q['question']}\nA: {q['correct_answer']}"
    except Exception as e:
        return f"Trivia failed: {e}"
