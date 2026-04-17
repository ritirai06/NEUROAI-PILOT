"""
Desktop automation tools using pyautogui + pygetwindow.
All UI actions are intended to be visible on screen.
"""
import os
import random
import subprocess
import time
import urllib.parse

import pyautogui
import pygetwindow as gw

from tools.window_manager import WindowManager, launch_visible

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


def _human_delay(min_s: float = 0.2, max_s: float = 0.5) -> None:
    time.sleep(random.uniform(min_s, max_s))


def _browser_command(browser: str) -> tuple[str, str]:
    b = (browser or "chrome").lower().strip()
    if b == "edge":
        return "msedge.exe", "edge"
    if b == "firefox":
        return "firefox.exe", "firefox"
    return "chrome.exe", "chrome"


def _focus_browser_window(browser_name: str) -> bool:
    hints = {
        "chrome": ["Google Chrome", "Chrome"],
        "edge": ["Microsoft Edge", "Edge"],
        "firefox": ["Mozilla Firefox", "Firefox"],
    }.get(browser_name, ["Chrome", "Google Chrome"])
    for hint in hints:
        hwnd = WindowManager.find_window_by_title(hint, timeout=1.2)
        if hwnd and WindowManager.bring_to_front(hwnd):
            return True
    return False


def _browser_guest_args(browser_name: str) -> list[str]:
    """
    Launch in a separate guest/private window so localhost portal tab is not reused.
    """
    if browser_name == "edge":
        return ["--guest", "--new-window", "about:blank"]
    if browser_name == "firefox":
        return ["-private-window", "about:blank"]
    return ["--guest", "--new-window", "about:blank"]


def _open_guest_browser_foreground(browser: str = "chrome") -> str:
    cmd, normalized = _browser_command(browser)
    args = _browser_guest_args(normalized)
    try:
        # Open a fresh guest/private window for web searching tasks.
        subprocess.Popen([cmd, *args])
    except Exception:
        # Fallback if direct spawn fails.
        launch_visible(f"{cmd} {' '.join(args)}", title_hint=normalized, maximize=True)

    _human_delay(1.4, 2.5)
    _focus_browser_window(normalized)
    _human_delay(0.2, 0.4)
    return normalized


def focus_window(title_keyword: str) -> str:
    try:
        all_wins = gw.getAllWindows()
        wins = [w for w in all_wins if title_keyword.lower() in w.title.lower() and w.title.strip()]
        if not wins:
            return f"Window '{title_keyword}' not found"
        w = wins[0]
        if w.isMinimized:
            w.restore()
        w.activate()
        time.sleep(0.4)
        return f"Focused: {w.title}"
    except Exception as e:
        return f"Focus error: {e}"


def list_open_windows() -> str:
    try:
        wins = [w.title for w in gw.getAllWindows() if w.title.strip()]
        return "Open windows:\n" + "\n".join(f"- {t}" for t in wins[:20])
    except Exception as e:
        return f"Window list error: {e}"


def close_window(title_keyword: str) -> str:
    try:
        wins = [w for w in gw.getAllWindows() if title_keyword.lower() in w.title.lower()]
        if not wins:
            return f"Window '{title_keyword}' not found"
        wins[0].close()
        return f"Closed: {wins[0].title}"
    except Exception as e:
        return f"Close window error: {e}"


def maximize_window(title_keyword: str) -> str:
    try:
        wins = [w for w in gw.getAllWindows() if title_keyword.lower() in w.title.lower()]
        if not wins:
            return f"Window '{title_keyword}' not found"
        wins[0].maximize()
        return f"Maximized: {wins[0].title}"
    except Exception as e:
        return f"Maximize error: {e}"


def minimize_window(title_keyword: str) -> str:
    try:
        wins = [w for w in gw.getAllWindows() if title_keyword.lower() in w.title.lower()]
        if not wins:
            return f"Window '{title_keyword}' not found"
        wins[0].minimize()
        return f"Minimized: {wins[0].title}"
    except Exception as e:
        return f"Minimize error: {e}"


def hotkey(*keys) -> str:
    try:
        pyautogui.hotkey(*keys)
        return f"Hotkey: {'+'.join(keys)}"
    except Exception as e:
        return f"Hotkey error: {e}"


def desktop_type(text: str, interval: float = 0.04) -> str:
    try:
        pyautogui.write(str(text), interval=interval)
        return f"Typed: {text}"
    except Exception as e:
        return f"Type error: {e}"


def desktop_press(key: str) -> str:
    try:
        pyautogui.press(key)
        return f"Pressed: {key}"
    except Exception as e:
        return f"Press error: {e}"


def desktop_click(x: int, y: int) -> str:
    try:
        pyautogui.click(x, y)
        return f"Clicked at ({x}, {y})"
    except Exception as e:
        return f"Click error: {e}"


def desktop_double_click(x: int, y: int) -> str:
    try:
        pyautogui.doubleClick(x, y)
        return f"Double-clicked at ({x}, {y})"
    except Exception as e:
        return f"Double-click error: {e}"


def desktop_right_click(x: int, y: int) -> str:
    try:
        pyautogui.rightClick(x, y)
        return f"Right-clicked at ({x}, {y})"
    except Exception as e:
        return f"Right-click error: {e}"


def desktop_scroll(direction: str = "down", amount: int = 3) -> str:
    try:
        clicks = -amount if direction == "down" else amount
        pyautogui.scroll(clicks)
        return f"Scrolled {direction} {amount}x"
    except Exception as e:
        return f"Scroll error: {e}"


def select_all() -> str:
    pyautogui.hotkey("ctrl", "a")
    return "Selected all"


def copy() -> str:
    pyautogui.hotkey("ctrl", "c")
    return "Copied"


def paste() -> str:
    pyautogui.hotkey("ctrl", "v")
    return "Pasted"


def undo() -> str:
    pyautogui.hotkey("ctrl", "z")
    return "Undo"


def save_file() -> str:
    pyautogui.hotkey("ctrl", "s")
    return "Saved"


def new_file() -> str:
    pyautogui.hotkey("ctrl", "n")
    return "New file"


def calculator_compute(expression: str) -> str:
    from tools.visual_calculator import visual_calculator_compute
    return visual_calculator_compute(expression, step_delay=0.3)


def calculator_compute_with_voice(expression: str) -> str:
    from tools.visual_calculator import voice_calculator_compute
    return voice_calculator_compute(expression, step_delay=0.3)


def notepad_write(text: str) -> str:
    try:
        launch_visible("notepad.exe", title_hint="Notepad", maximize=False)
        _human_delay(1.0, 1.6)
        hwnd = WindowManager.find_window_by_title("Notepad", timeout=2.0)
        if hwnd:
            WindowManager.bring_to_front(hwnd)
        _human_delay(0.2, 0.5)
        pyautogui.write(text, interval=random.uniform(0.06, 0.12))
        return f"Notepad: typed '{text[:50]}'"
    except Exception as e:
        return f"Notepad error: {e}"


def notepad_save_as(filename: str) -> str:
    try:
        focus_window("Notepad")
        pyautogui.hotkey("ctrl", "shift", "s")
        time.sleep(0.8)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.write(filename, interval=0.04)
        pyautogui.press("enter")
        time.sleep(0.5)
        return f"Saved as: {filename}"
    except Exception as e:
        return f"Save error: {e}"


def open_website_visible(url: str, browser: str = "chrome") -> str:
    try:
        normalized = _open_guest_browser_foreground(browser)
        target = str(url).strip()
        if not target.startswith(("http://", "https://", "about:")):
            target = "https://" + target
        pyautogui.hotkey("ctrl", "l")
        _human_delay()
        pyautogui.write(target, interval=random.uniform(0.06, 0.11))
        _human_delay()
        pyautogui.press("enter")
        _human_delay(0.5, 0.9)
        return f"Opened in {normalized}: {target}"
    except Exception as e:
        return f"Open website error: {e}"


def search_duckduckgo_visible(query: str, browser: str = "chrome") -> str:
    q = urllib.parse.quote_plus(str(query))
    return open_website_visible(f"https://duckduckgo.com/?q={q}", browser=browser)


def open_youtube_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://www.youtube.com", browser=browser)


def open_gmail_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://mail.google.com", browser=browser)


def open_github_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://github.com", browser=browser)


def open_google_maps_visible(location: str = "", browser: str = "chrome") -> str:
    if location:
        q = urllib.parse.quote_plus(str(location))
        return open_website_visible(f"https://www.google.com/maps/search/{q}", browser=browser)
    return open_website_visible("https://www.google.com/maps", browser=browser)


def open_google_translate_visible(text: str = "", target: str = "hi", browser: str = "chrome") -> str:
    q = urllib.parse.quote_plus(str(text))
    return open_website_visible(f"https://translate.google.com/?sl=auto&tl={target}&text={q}&op=translate", browser=browser)


def open_wikipedia_visible(query: str = "", browser: str = "chrome") -> str:
    term = str(query or "Wikipedia").replace(" ", "_")
    q = urllib.parse.quote_plus(term)
    return open_website_visible(f"https://en.wikipedia.org/wiki/{q}", browser=browser)


def open_twitter_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://twitter.com", browser=browser)


def open_reddit_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://www.reddit.com", browser=browser)


def open_linkedin_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://www.linkedin.com", browser=browser)


def open_stackoverflow_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://stackoverflow.com", browser=browser)


def open_netflix_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://www.netflix.com", browser=browser)


def open_spotify_web_visible(browser: str = "chrome") -> str:
    return open_website_visible("https://open.spotify.com", browser=browser)


def open_incognito_visible(url: str = "about:blank", browser: str = "chrome") -> str:
    return open_website_visible(url or "about:blank", browser=browser)


def search_google_visible(query: str, browser: str = "chrome") -> str:
    try:
        normalized = _open_guest_browser_foreground(browser)
        pyautogui.hotkey("ctrl", "l")
        _human_delay()
        pyautogui.write(str(query), interval=random.uniform(0.06, 0.11))
        _human_delay()
        pyautogui.press("enter")
        _human_delay(0.5, 0.9)
        return f"Searched in {normalized}: {query}"
    except Exception as e:
        return f"Search error: {e}"


def search_youtube_visible(query: str, browser: str = "chrome") -> str:
    q = urllib.parse.quote_plus(str(query))
    return open_website_visible(f"https://www.youtube.com/results?search_query={q}", browser=browser)


def click_first_video_visible() -> str:
    try:
        _human_delay(0.6, 1.0)
        for _ in range(6):
            pyautogui.press("tab")
            _human_delay(0.08, 0.15)
        pyautogui.press("enter")
        _human_delay(0.5, 1.0)
        return "Triggered first video (best effort)"
    except Exception as e:
        return f"Click first video error: {e}"


def app_type_and_enter(app_title: str, text: str) -> str:
    try:
        result = focus_window(app_title)
        if "not found" in result:
            return result
        time.sleep(0.3)
        pyautogui.write(str(text), interval=0.04)
        pyautogui.press("enter")
        return f"Typed '{text}' in {app_title} and pressed Enter"
    except Exception as e:
        return f"App type error: {e}"


def open_and_type(app: str, text: str) -> str:
    try:
        launch_visible(app, title_hint=app, maximize=False)
        time.sleep(1.5)
        pyautogui.write(str(text), interval=0.04)
        return f"Opened {app} and typed: {text}"
    except Exception as e:
        return f"Open and type error: {e}"


def search_in_start_menu(query: str) -> str:
    try:
        pyautogui.press("win")
        time.sleep(0.6)
        pyautogui.write(query, interval=0.05)
        time.sleep(0.5)
        return f"Searched Start Menu: {query}"
    except Exception as e:
        return f"Start menu error: {e}"


def open_run_dialog(command: str) -> str:
    try:
        pyautogui.hotkey("win", "r")
        time.sleep(0.5)
        pyautogui.write(command, interval=0.05)
        pyautogui.press("enter")
        return f"Run dialog: {command}"
    except Exception as e:
        return f"Run dialog error: {e}"


def switch_window() -> str:
    try:
        pyautogui.hotkey("alt", "tab")
        return "Switched window (Alt+Tab)"
    except Exception as e:
        return f"Switch error: {e}"


def show_desktop() -> str:
    try:
        pyautogui.hotkey("win", "d")
        return "Showing desktop"
    except Exception as e:
        return f"Show desktop error: {e}"


def take_desktop_screenshot(filename: str = "desktop_screenshot.png") -> str:
    try:
        path = os.path.join(os.getcwd(), filename)
        pyautogui.screenshot(path)
        return f"Screenshot saved: {path}"
    except Exception as e:
        return f"Screenshot error: {e}"


def get_screen_size() -> str:
    try:
        w, h = pyautogui.size()
        return f"Screen size: {w}x{h}"
    except Exception as e:
        return f"Screen size error: {e}"


def get_mouse_pos() -> str:
    try:
        x, y = pyautogui.position()
        return f"Mouse position: ({x}, {y})"
    except Exception as e:
        return f"Mouse pos error: {e}"
