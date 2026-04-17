"""
Temporal Activities — all tools wrapped as Temporal activities.
"""
import asyncio
from temporalio import activity
from tools.browser_tools import (
    open_website, search_youtube, click_first_video,
    search_google, search_bing, search_amazon,
    click, click_button, type, clear_and_type,
    press_enter, press_escape,
    scroll, scroll_to_top, scroll_to_bottom,
    fill_form, scrape, get_table_data, send_email,
    go_back, go_forward, refresh_page,
    get_current_url, get_page_title, get_page_text, get_links,
    zoom_page, take_browser_screenshot, take_full_page_screenshot,
    wait_for_element, hover, select_option,
    open_youtube, open_gmail, open_github,
    open_google_maps, open_google_translate, open_wikipedia,
    open_new_tab, close_browser, download_file,
    search_duckduckgo, open_twitter, open_reddit, open_linkedin,
    open_stackoverflow, open_netflix, open_spotify_web,
    get_page_screenshot_base64, highlight_element, count_elements,
    get_element_text, open_incognito,
)
from tools.desktop_tools import (
    open_website_visible, search_youtube_visible, search_google_visible, click_first_video_visible
)
from tools.system_tools import (
    open_app, close_app, run_command, take_screenshot, wait, respond,
    copy_to_clipboard, get_clipboard,
    set_volume, mute_volume, volume_up, volume_down,
    get_system_info, get_battery, get_cpu_usage, get_ram_usage,
    get_disk_usage, get_running_processes, kill_process,
    create_file, read_file, delete_file, list_files,
    move_file, copy_file, zip_files, unzip_file, find_files, get_file_info,
    get_ip_address, ping, get_wifi_info, get_network_speed,
    lock_screen, shutdown, restart, sleep_pc,
    show_notification, set_wallpaper, press_key, type_text,
    get_datetime, set_reminder, calculate, search_in_file, word_count,
    get_screen_resolution, empty_recycle_bin, get_env_var, set_brightness,
    get_installed_apps, open_task_manager, clear_temp_files, get_startup_programs,
    rename_file, append_to_file, get_mouse_position, move_mouse,
    mouse_click, mouse_double_click, right_click, scroll_mouse,
)
from tools.camera_tools import open_camera, click_photo, close_camera, record_video, get_camera_info
from tools.api_tools import (
    get_weather, get_weather_detailed, get_news,
    get_crypto_price, get_currency_rate, get_stock_price,
    define_word, translate_text, get_synonyms,
    get_joke, get_quote, get_fact,
    get_time_in_city, shorten_url, get_qr_code,
    search_wikipedia, get_github_user,
    api_get, api_post, check_website_status,
    get_ip_info, get_moon_phase, get_nasa_apod, get_random_dog, get_random_cat,
    get_country_info, get_holidays, get_air_quality, uuid_generate,
    get_color_info, get_advice, get_trivia,
)

def _sync(fn):
    """Wrap a sync function for use in async activity."""
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)
    return wrapper

# ── Browser activities ────────────────────────────────────────────────────────
@activity.defn(name="open_website")
async def act_open_website(url: str) -> str: return await asyncio.to_thread(open_website_visible, url)

@activity.defn(name="search_youtube")
async def act_search_youtube(query: str) -> str: return await asyncio.to_thread(search_youtube_visible, query)

@activity.defn(name="click_first_video")
async def act_click_first_video() -> str: return await asyncio.to_thread(click_first_video_visible)

@activity.defn(name="search_google")
async def act_search_google(query: str) -> str: return await asyncio.to_thread(search_google_visible, query)

@activity.defn(name="search_bing")
async def act_search_bing(query: str) -> str: return await search_bing(query)

@activity.defn(name="search_amazon")
async def act_search_amazon(query: str) -> str: return await search_amazon(query)

@activity.defn(name="click")
async def act_click(target: str) -> str: return await click(target)

@activity.defn(name="click_button")
async def act_click_button(text: str) -> str: return await click_button(text)

@activity.defn(name="type")
async def act_type(text: str) -> str: return await type(text)

@activity.defn(name="clear_and_type")
async def act_clear_and_type(selector: str, text: str) -> str: return await clear_and_type(selector, text)

@activity.defn(name="press_enter")
async def act_press_enter() -> str: return await press_enter()

@activity.defn(name="press_escape")
async def act_press_escape() -> str: return await press_escape()

@activity.defn(name="scroll")
async def act_scroll(direction: str = "down", amount: int = 3) -> str: return await scroll(direction, amount)

@activity.defn(name="scroll_to_top")
async def act_scroll_to_top() -> str: return await scroll_to_top()

@activity.defn(name="scroll_to_bottom")
async def act_scroll_to_bottom() -> str: return await scroll_to_bottom()

@activity.defn(name="fill_form")
async def act_fill_form(fields: dict) -> str: return await fill_form(fields)

@activity.defn(name="scrape")
async def act_scrape(url: str, selector: str = "p") -> str: return await scrape(url, selector)

@activity.defn(name="get_table_data")
async def act_get_table_data() -> str: return await get_table_data()

@activity.defn(name="send_email")
async def act_send_email(to: str, subject: str = "Hello", body: str = "") -> str: return await send_email(to, subject, body)

@activity.defn(name="go_back")
async def act_go_back() -> str: return await go_back()

@activity.defn(name="go_forward")
async def act_go_forward() -> str: return await go_forward()

@activity.defn(name="refresh_page")
async def act_refresh_page() -> str: return await refresh_page()

@activity.defn(name="get_current_url")
async def act_get_current_url() -> str: return await get_current_url()

@activity.defn(name="get_page_title")
async def act_get_page_title() -> str: return await get_page_title()

@activity.defn(name="get_page_text")
async def act_get_page_text() -> str: return await get_page_text()

@activity.defn(name="get_links")
async def act_get_links() -> str: return await get_links()

@activity.defn(name="zoom_page")
async def act_zoom_page(level: int = 100) -> str: return await zoom_page(level)

@activity.defn(name="take_browser_screenshot")
async def act_take_browser_screenshot(filename: str = "browser_screenshot.png") -> str: return await take_browser_screenshot(filename)

@activity.defn(name="take_full_page_screenshot")
async def act_take_full_page_screenshot(filename: str = "fullpage.png") -> str: return await take_full_page_screenshot(filename)

@activity.defn(name="wait_for_element")
async def act_wait_for_element(selector: str, timeout: int = 10000) -> str: return await wait_for_element(selector, timeout)

@activity.defn(name="hover")
async def act_hover(selector: str) -> str: return await hover(selector)

@activity.defn(name="select_option")
async def act_select_option(selector: str, value: str) -> str: return await select_option(selector, value)

@activity.defn(name="open_youtube")
async def act_open_youtube() -> str: return await open_youtube()

@activity.defn(name="open_gmail")
async def act_open_gmail() -> str: return await open_gmail()

@activity.defn(name="open_github")
async def act_open_github() -> str: return await open_github()

@activity.defn(name="open_google_maps")
async def act_open_google_maps(location: str = "") -> str: return await open_google_maps(location)

@activity.defn(name="open_google_translate")
async def act_open_google_translate(text: str = "", target: str = "hi") -> str: return await open_google_translate(text, target)

@activity.defn(name="open_wikipedia")
async def act_open_wikipedia(query: str) -> str: return await open_wikipedia(query)

@activity.defn(name="open_new_tab")
async def act_open_new_tab(url: str = "about:blank") -> str: return await open_new_tab(url)

@activity.defn(name="close_browser")
async def act_close_browser() -> str: return await close_browser()

@activity.defn(name="download_file")
async def act_download_file(url: str, filename: str = None) -> str: return await download_file(url, filename)

# ── System activities ─────────────────────────────────────────────────────────
@activity.defn(name="open_app")
async def act_open_app(app: str) -> str: return await asyncio.to_thread(open_app, app)

@activity.defn(name="close_app")
async def act_close_app(app: str) -> str: return await asyncio.to_thread(close_app, app)

@activity.defn(name="run_command")
async def act_run_command(cmd: str) -> str: return await asyncio.to_thread(run_command, cmd)

@activity.defn(name="take_screenshot")
async def act_take_screenshot(filename: str = "screenshot.png") -> str: return await asyncio.to_thread(take_screenshot, filename)

@activity.defn(name="wait")
async def act_wait(seconds: float = 1.0) -> str:
    await asyncio.sleep(float(seconds))
    return f"Waited {seconds}s"

@activity.defn(name="respond")
async def act_respond(message: str) -> str: return respond(message)

@activity.defn(name="get_system_info")
async def act_get_system_info() -> str: return await asyncio.to_thread(get_system_info)

@activity.defn(name="get_battery")
async def act_get_battery() -> str: return await asyncio.to_thread(get_battery)

@activity.defn(name="get_cpu_usage")
async def act_get_cpu_usage() -> str: return await asyncio.to_thread(get_cpu_usage)

@activity.defn(name="get_ram_usage")
async def act_get_ram_usage() -> str: return await asyncio.to_thread(get_ram_usage)

@activity.defn(name="get_disk_usage")
async def act_get_disk_usage(path: str = "/") -> str: return await asyncio.to_thread(get_disk_usage, path)

@activity.defn(name="get_running_processes")
async def act_get_running_processes(limit: int = 10) -> str: return await asyncio.to_thread(get_running_processes, limit)

@activity.defn(name="kill_process")
async def act_kill_process(name: str) -> str: return await asyncio.to_thread(kill_process, name)

@activity.defn(name="copy_to_clipboard")
async def act_copy_to_clipboard(text: str) -> str: return await asyncio.to_thread(copy_to_clipboard, text)

@activity.defn(name="get_clipboard")
async def act_get_clipboard() -> str: return await asyncio.to_thread(get_clipboard)

@activity.defn(name="set_volume")
async def act_set_volume(level: int) -> str: return await asyncio.to_thread(set_volume, level)

@activity.defn(name="mute_volume")
async def act_mute_volume() -> str: return await asyncio.to_thread(mute_volume)

@activity.defn(name="volume_up")
async def act_volume_up(amount: int = 10) -> str: return await asyncio.to_thread(volume_up, amount)

@activity.defn(name="volume_down")
async def act_volume_down(amount: int = 10) -> str: return await asyncio.to_thread(volume_down, amount)

@activity.defn(name="create_file")
async def act_create_file(path: str, content: str = "") -> str: return await asyncio.to_thread(create_file, path, content)

@activity.defn(name="read_file")
async def act_read_file(path: str) -> str: return await asyncio.to_thread(read_file, path)

@activity.defn(name="delete_file")
async def act_delete_file(path: str) -> str: return await asyncio.to_thread(delete_file, path)

@activity.defn(name="list_files")
async def act_list_files(path: str = ".") -> str: return await asyncio.to_thread(list_files, path)

@activity.defn(name="move_file")
async def act_move_file(src: str, dst: str) -> str: return await asyncio.to_thread(move_file, src, dst)

@activity.defn(name="copy_file")
async def act_copy_file(src: str, dst: str) -> str: return await asyncio.to_thread(copy_file, src, dst)

@activity.defn(name="zip_files")
async def act_zip_files(source: str, output: str = None) -> str: return await asyncio.to_thread(zip_files, source, output)

@activity.defn(name="unzip_file")
async def act_unzip_file(path: str, dest: str = ".") -> str: return await asyncio.to_thread(unzip_file, path, dest)

@activity.defn(name="find_files")
async def act_find_files(folder: str, pattern: str) -> str: return await asyncio.to_thread(find_files, folder, pattern)

@activity.defn(name="get_file_info")
async def act_get_file_info(path: str) -> str: return await asyncio.to_thread(get_file_info, path)

@activity.defn(name="search_in_file")
async def act_search_in_file(path: str, keyword: str) -> str: return await asyncio.to_thread(search_in_file, path, keyword)

@activity.defn(name="word_count")
async def act_word_count(path: str) -> str: return await asyncio.to_thread(word_count, path)

@activity.defn(name="get_ip_address")
async def act_get_ip_address() -> str: return await asyncio.to_thread(get_ip_address)

@activity.defn(name="ping")
async def act_ping(host: str) -> str: return await asyncio.to_thread(ping, host)

@activity.defn(name="get_wifi_info")
async def act_get_wifi_info() -> str: return await asyncio.to_thread(get_wifi_info)

@activity.defn(name="get_network_speed")
async def act_get_network_speed() -> str: return await asyncio.to_thread(get_network_speed)

@activity.defn(name="lock_screen")
async def act_lock_screen() -> str: return await asyncio.to_thread(lock_screen)

@activity.defn(name="shutdown")
async def act_shutdown(delay: int = 0) -> str: return await asyncio.to_thread(shutdown, delay)

@activity.defn(name="restart")
async def act_restart(delay: int = 0) -> str: return await asyncio.to_thread(restart, delay)

@activity.defn(name="sleep_pc")
async def act_sleep_pc() -> str: return await asyncio.to_thread(sleep_pc)

@activity.defn(name="show_notification")
async def act_show_notification(title: str, message: str) -> str: return await asyncio.to_thread(show_notification, title, message)

@activity.defn(name="set_wallpaper")
async def act_set_wallpaper(path: str) -> str: return await asyncio.to_thread(set_wallpaper, path)

@activity.defn(name="press_key")
async def act_press_key(key: str) -> str: return await asyncio.to_thread(press_key, key)

@activity.defn(name="type_text")
async def act_type_text(text: str) -> str: return await asyncio.to_thread(type_text, text)

@activity.defn(name="get_datetime")
async def act_get_datetime() -> str: return await asyncio.to_thread(get_datetime)

@activity.defn(name="set_reminder")
async def act_set_reminder(message: str, seconds: int) -> str: return await asyncio.to_thread(set_reminder, message, seconds)

@activity.defn(name="calculate")
async def act_calculate(expression: str) -> str: return await asyncio.to_thread(calculate, expression)

# ── System new activities ─────────────────────────────────────────────────────
@activity.defn(name="get_screen_resolution")
async def act_get_screen_resolution() -> str: return await asyncio.to_thread(get_screen_resolution)

@activity.defn(name="empty_recycle_bin")
async def act_empty_recycle_bin() -> str: return await asyncio.to_thread(empty_recycle_bin)

@activity.defn(name="get_env_var")
async def act_get_env_var(name: str) -> str: return await asyncio.to_thread(get_env_var, name)

@activity.defn(name="set_brightness")
async def act_set_brightness(level: int) -> str: return await asyncio.to_thread(set_brightness, level)

@activity.defn(name="get_installed_apps")
async def act_get_installed_apps() -> str: return await asyncio.to_thread(get_installed_apps)

@activity.defn(name="open_task_manager")
async def act_open_task_manager() -> str: return await asyncio.to_thread(open_task_manager)

@activity.defn(name="clear_temp_files")
async def act_clear_temp_files() -> str: return await asyncio.to_thread(clear_temp_files)

@activity.defn(name="get_startup_programs")
async def act_get_startup_programs() -> str: return await asyncio.to_thread(get_startup_programs)

@activity.defn(name="rename_file")
async def act_rename_file(src: str, new_name: str) -> str: return await asyncio.to_thread(rename_file, src, new_name)

@activity.defn(name="append_to_file")
async def act_append_to_file(path: str, content: str) -> str: return await asyncio.to_thread(append_to_file, path, content)

@activity.defn(name="get_mouse_position")
async def act_get_mouse_position() -> str: return await asyncio.to_thread(get_mouse_position)

@activity.defn(name="move_mouse")
async def act_move_mouse(x: int, y: int) -> str: return await asyncio.to_thread(move_mouse, x, y)

@activity.defn(name="mouse_click")
async def act_mouse_click(x: int, y: int) -> str: return await asyncio.to_thread(mouse_click, x, y)

@activity.defn(name="mouse_double_click")
async def act_mouse_double_click(x: int, y: int) -> str: return await asyncio.to_thread(mouse_double_click, x, y)

@activity.defn(name="right_click")
async def act_right_click(x: int, y: int) -> str: return await asyncio.to_thread(right_click, x, y)

@activity.defn(name="scroll_mouse")
async def act_scroll_mouse(direction: str = "down", clicks: int = 3) -> str: return await asyncio.to_thread(scroll_mouse, direction, clicks)

# ── Camera activities ─────────────────────────────────────────────────────────
@activity.defn(name="open_camera")
async def act_open_camera() -> str: return await asyncio.to_thread(open_camera)

@activity.defn(name="click_photo")
async def act_click_photo() -> str: return await asyncio.to_thread(click_photo)

@activity.defn(name="close_camera")
async def act_close_camera() -> str: return await asyncio.to_thread(close_camera)

@activity.defn(name="record_video")
async def act_record_video(filename: str = None, duration: int = 5) -> str: return await asyncio.to_thread(record_video, filename, duration)

@activity.defn(name="get_camera_info")
async def act_get_camera_info() -> str: return await asyncio.to_thread(get_camera_info)

# ── Browser new activities ────────────────────────────────────────────────────
@activity.defn(name="search_duckduckgo")
async def act_search_duckduckgo(query: str) -> str: return await search_duckduckgo(query)

@activity.defn(name="open_twitter")
async def act_open_twitter() -> str: return await open_twitter()

@activity.defn(name="open_reddit")
async def act_open_reddit() -> str: return await open_reddit()

@activity.defn(name="open_linkedin")
async def act_open_linkedin() -> str: return await open_linkedin()

@activity.defn(name="open_stackoverflow")
async def act_open_stackoverflow() -> str: return await open_stackoverflow()

@activity.defn(name="open_netflix")
async def act_open_netflix() -> str: return await open_netflix()

@activity.defn(name="open_spotify_web")
async def act_open_spotify_web() -> str: return await open_spotify_web()

@activity.defn(name="get_page_screenshot_base64")
async def act_get_page_screenshot_base64() -> str: return await get_page_screenshot_base64()

@activity.defn(name="highlight_element")
async def act_highlight_element(selector: str) -> str: return await highlight_element(selector)

@activity.defn(name="count_elements")
async def act_count_elements(selector: str) -> str: return await count_elements(selector)

@activity.defn(name="get_element_text")
async def act_get_element_text(selector: str) -> str: return await get_element_text(selector)

@activity.defn(name="open_incognito")
async def act_open_incognito(url: str = "about:blank") -> str: return await open_incognito(url)

# ── API activities ────────────────────────────────────────────────────────────
@activity.defn(name="get_weather")
async def act_get_weather(city: str) -> str: return await get_weather(city)

@activity.defn(name="get_weather_detailed")
async def act_get_weather_detailed(city: str) -> str: return await get_weather_detailed(city)

@activity.defn(name="get_news")
async def act_get_news(topic: str = "technology") -> str: return await get_news(topic)

@activity.defn(name="get_crypto_price")
async def act_get_crypto_price(coin: str = "bitcoin") -> str: return await get_crypto_price(coin)

@activity.defn(name="get_currency_rate")
async def act_get_currency_rate(from_cur: str = "USD", to_cur: str = "INR") -> str: return await get_currency_rate(from_cur, to_cur)

@activity.defn(name="get_stock_price")
async def act_get_stock_price(symbol: str) -> str: return await get_stock_price(symbol)

@activity.defn(name="define_word")
async def act_define_word(word: str) -> str: return await define_word(word)

@activity.defn(name="translate_text")
async def act_translate_text(text: str, target_lang: str = "hi") -> str: return await translate_text(text, target_lang)

@activity.defn(name="get_synonyms")
async def act_get_synonyms(word: str) -> str: return await get_synonyms(word)

@activity.defn(name="get_joke")
async def act_get_joke() -> str: return await get_joke()

@activity.defn(name="get_quote")
async def act_get_quote() -> str: return await get_quote()

@activity.defn(name="get_fact")
async def act_get_fact() -> str: return await get_fact()

@activity.defn(name="get_time_in_city")
async def act_get_time_in_city(city: str) -> str: return await get_time_in_city(city)

@activity.defn(name="shorten_url")
async def act_shorten_url(url: str) -> str: return await shorten_url(url)

@activity.defn(name="get_qr_code")
async def act_get_qr_code(text: str) -> str: return await get_qr_code(text)

@activity.defn(name="search_wikipedia")
async def act_search_wikipedia(query: str) -> str: return await search_wikipedia(query)

@activity.defn(name="get_github_user")
async def act_get_github_user(username: str) -> str: return await get_github_user(username)

@activity.defn(name="api_get")
async def act_api_get(url: str, headers: dict = None) -> str: return await api_get(url, headers)

@activity.defn(name="api_post")
async def act_api_post(url: str, data: dict = None) -> str: return await api_post(url, data)

@activity.defn(name="check_website_status")
async def act_check_website_status(url: str) -> str: return await check_website_status(url)

@activity.defn(name="get_ip_info")
async def act_get_ip_info(ip: str = "") -> str: return await get_ip_info(ip)

@activity.defn(name="get_moon_phase")
async def act_get_moon_phase() -> str: return await get_moon_phase()

@activity.defn(name="get_nasa_apod")
async def act_get_nasa_apod() -> str: return await get_nasa_apod()

@activity.defn(name="get_random_dog")
async def act_get_random_dog() -> str: return await get_random_dog()

@activity.defn(name="get_random_cat")
async def act_get_random_cat() -> str: return await get_random_cat()

@activity.defn(name="get_country_info")
async def act_get_country_info(country: str) -> str: return await get_country_info(country)

@activity.defn(name="get_holidays")
async def act_get_holidays(country: str = "US", year: int = 2025) -> str: return await get_holidays(country, year)

@activity.defn(name="get_air_quality")
async def act_get_air_quality(city: str) -> str: return await get_air_quality(city)

@activity.defn(name="uuid_generate")
async def act_uuid_generate() -> str: return await uuid_generate()

@activity.defn(name="get_color_info")
async def act_get_color_info(hex_color: str) -> str: return await get_color_info(hex_color)

@activity.defn(name="get_advice")
async def act_get_advice() -> str: return await get_advice()

@activity.defn(name="get_trivia")
async def act_get_trivia(category: str = "general") -> str: return await get_trivia(category)


# ── Registry ──────────────────────────────────────────────────────────────────
ACTIVITY_MAP = {
    "open_website": act_open_website, "search_youtube": act_search_youtube,
    "click_first_video": act_click_first_video, "search_google": act_search_google,
    "search_bing": act_search_bing, "search_amazon": act_search_amazon,
    "click": act_click, "click_button": act_click_button, "type": act_type,
    "clear_and_type": act_clear_and_type, "press_enter": act_press_enter,
    "press_escape": act_press_escape, "scroll": act_scroll,
    "scroll_to_top": act_scroll_to_top, "scroll_to_bottom": act_scroll_to_bottom,
    "fill_form": act_fill_form, "scrape": act_scrape, "get_table_data": act_get_table_data,
    "send_email": act_send_email, "go_back": act_go_back, "go_forward": act_go_forward,
    "refresh_page": act_refresh_page, "get_current_url": act_get_current_url,
    "get_page_title": act_get_page_title, "get_page_text": act_get_page_text,
    "get_links": act_get_links, "zoom_page": act_zoom_page,
    "take_browser_screenshot": act_take_browser_screenshot,
    "take_full_page_screenshot": act_take_full_page_screenshot,
    "wait_for_element": act_wait_for_element, "hover": act_hover,
    "select_option": act_select_option, "open_youtube": act_open_youtube,
    "open_gmail": act_open_gmail, "open_github": act_open_github,
    "open_google_maps": act_open_google_maps, "open_google_translate": act_open_google_translate,
    "open_wikipedia": act_open_wikipedia, "open_new_tab": act_open_new_tab,
    "close_browser": act_close_browser, "download_file": act_download_file,
    "open_app": act_open_app, "close_app": act_close_app, "run_command": act_run_command,
    "take_screenshot": act_take_screenshot, "wait": act_wait, "respond": act_respond,
    "get_system_info": act_get_system_info, "get_battery": act_get_battery,
    "get_cpu_usage": act_get_cpu_usage, "get_ram_usage": act_get_ram_usage,
    "get_disk_usage": act_get_disk_usage, "get_running_processes": act_get_running_processes,
    "kill_process": act_kill_process, "copy_to_clipboard": act_copy_to_clipboard,
    "get_clipboard": act_get_clipboard, "set_volume": act_set_volume,
    "mute_volume": act_mute_volume, "volume_up": act_volume_up, "volume_down": act_volume_down,
    "create_file": act_create_file, "read_file": act_read_file, "delete_file": act_delete_file,
    "list_files": act_list_files, "move_file": act_move_file, "copy_file": act_copy_file,
    "zip_files": act_zip_files, "unzip_file": act_unzip_file, "find_files": act_find_files,
    "get_file_info": act_get_file_info, "search_in_file": act_search_in_file,
    "word_count": act_word_count, "get_ip_address": act_get_ip_address,
    "ping": act_ping, "get_wifi_info": act_get_wifi_info, "get_network_speed": act_get_network_speed,
    "lock_screen": act_lock_screen, "shutdown": act_shutdown, "restart": act_restart,
    "sleep_pc": act_sleep_pc, "show_notification": act_show_notification,
    "set_wallpaper": act_set_wallpaper, "press_key": act_press_key, "type_text": act_type_text,
    "get_datetime": act_get_datetime, "set_reminder": act_set_reminder, "calculate": act_calculate,
    "open_camera": act_open_camera, "click_photo": act_click_photo, "close_camera": act_close_camera,
    "record_video": act_record_video, "get_camera_info": act_get_camera_info,
    "get_screen_resolution": act_get_screen_resolution, "empty_recycle_bin": act_empty_recycle_bin,
    "get_env_var": act_get_env_var, "set_brightness": act_set_brightness,
    "get_installed_apps": act_get_installed_apps, "open_task_manager": act_open_task_manager,
    "clear_temp_files": act_clear_temp_files, "get_startup_programs": act_get_startup_programs,
    "rename_file": act_rename_file, "append_to_file": act_append_to_file,
    "get_mouse_position": act_get_mouse_position, "move_mouse": act_move_mouse,
    "mouse_click": act_mouse_click, "mouse_double_click": act_mouse_double_click,
    "right_click": act_right_click, "scroll_mouse": act_scroll_mouse,
    "search_duckduckgo": act_search_duckduckgo, "open_twitter": act_open_twitter,
    "open_reddit": act_open_reddit, "open_linkedin": act_open_linkedin,
    "open_stackoverflow": act_open_stackoverflow, "open_netflix": act_open_netflix,
    "open_spotify_web": act_open_spotify_web,
    "get_page_screenshot_base64": act_get_page_screenshot_base64,
    "highlight_element": act_highlight_element, "count_elements": act_count_elements,
    "get_element_text": act_get_element_text, "open_incognito": act_open_incognito,
    "get_weather": act_get_weather, "get_weather_detailed": act_get_weather_detailed,
    "get_news": act_get_news, "get_crypto_price": act_get_crypto_price,
    "get_currency_rate": act_get_currency_rate, "get_stock_price": act_get_stock_price,
    "define_word": act_define_word, "translate_text": act_translate_text,
    "get_synonyms": act_get_synonyms, "get_joke": act_get_joke, "get_quote": act_get_quote,
    "get_fact": act_get_fact, "get_time_in_city": act_get_time_in_city,
    "shorten_url": act_shorten_url, "get_qr_code": act_get_qr_code,
    "search_wikipedia": act_search_wikipedia, "get_github_user": act_get_github_user,
    "api_get": act_api_get, "api_post": act_api_post, "check_website_status": act_check_website_status,
    "get_ip_info": act_get_ip_info, "get_moon_phase": act_get_moon_phase,
    "get_nasa_apod": act_get_nasa_apod, "get_random_dog": act_get_random_dog,
    "get_random_cat": act_get_random_cat, "get_country_info": act_get_country_info,
    "get_holidays": act_get_holidays, "get_air_quality": act_get_air_quality,
    "uuid_generate": act_uuid_generate, "get_color_info": act_get_color_info,
    "get_advice": act_get_advice, "get_trivia": act_get_trivia,
}

ALL_ACTIVITIES = list(ACTIVITY_MAP.values())
