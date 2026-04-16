"""
Desktop automation tools — pyautogui + pygetwindow.
Real UI interaction: focus windows, type text, click buttons, use calculator, notepad, etc.
"""
import subprocess
import time
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


# ── Window management ─────────────────────────────────────────────────────────

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
        return "Open windows:\n" + "\n".join(f"• {t}" for t in wins[:20])
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


# ── Keyboard automation ───────────────────────────────────────────────────────

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


# ── Calculator automation ─────────────────────────────────────────────────────

def calculator_compute(expression: str) -> str:
    """
    Instantly compute expression via Python eval AND open Windows Calculator
    to show the result visually. Always returns the result.
    """
    # Clean expression
    expr = (expression.replace(" ", "")
                      .replace("x", "*").replace("X", "*")
                      .replace("\u00d7", "*").replace("\u00f7", "/"))
    allowed = set("0123456789+-*/.%()")
    safe = "".join(c for c in expr if c in allowed)

    # ── Step 1: Compute instantly via Python eval ──────────────────────────
    try:
        result = eval(safe)
        if isinstance(result, float) and result == int(result):
            result = int(result)
        result_str = str(result)
    except Exception as e:
        return f"Invalid expression '{expression}': {e}"

    # ── Step 2: Open Calculator and type it visually (best effort) ─────────
    try:
        subprocess.Popen("calc.exe", shell=True)
        time.sleep(1.5)
        focus_window("Calculator")
        time.sleep(0.3)

        key_map = {
            "+": "+", "-": "-", "*": "*", "/": "/",
            "0":"0","1":"1","2":"2","3":"3","4":"4",
            "5":"5","6":"6","7":"7","8":"8","9":"9","." : ".",
        }
        for ch in safe:
            if ch in key_map:
                pyautogui.press(key_map[ch])
                time.sleep(0.05)
        pyautogui.press("enter")
    except Exception:
        pass  # UI is optional — result already computed above

    return f"Calculator: {expression} = {result_str}"


# ── Notepad automation ────────────────────────────────────────────────────────

def notepad_write(text: str) -> str:
    try:
        subprocess.Popen("notepad.exe", shell=True)
        time.sleep(1.2)
        focus_window("Notepad")
        time.sleep(0.3)
        pyautogui.write(text, interval=0.03)
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


# ── App-specific interactions ─────────────────────────────────────────────────

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
        subprocess.Popen(app, shell=True)
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
    import os
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
