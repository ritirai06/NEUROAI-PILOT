"""
Camera tools — OpenCV webcam capture.
"""
import os
import threading
import subprocess
import sys
from datetime import datetime

_cap = None
_window_thread = None


def open_camera() -> str:
    """Open webcam in visible window."""
    global _window_thread

    script = '''
import cv2
import sys
import time

try:
    import win32gui
    import win32con
    HAS_WIN32 = True
except:
    HAS_WIN32 = False

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("NO_CAMERA")
    sys.exit(1)

window_name = "NeuroAI Camera - Press Q to close"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

if HAS_WIN32:
    time.sleep(0.3)
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        win32gui.SetForegroundWindow(hwnd)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow(window_name, frame)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w")
    tmp.write(script)
    tmp.close()

    def _run():
        subprocess.Popen(
            [sys.executable, tmp.name],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )

    _window_thread = threading.Thread(target=_run, daemon=True)
    _window_thread.start()
    return "✅ Camera opened — press Q to close"


def click_photo(filename: str = None) -> str:
    """Capture a photo from webcam."""
    try:
        import cv2
    except ImportError:
        return "❌ OpenCV not installed"

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "❌ No camera found"

    import time
    time.sleep(0.5)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return "❌ Failed to capture frame"

    if not filename:
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    path = os.path.join(os.getcwd(), filename)
    cv2.imwrite(path, frame)
    return f"📸 Photo saved: {path}"


def close_camera() -> str:
    global _cap
    if _cap:
        _cap.release()
        _cap = None
        try:
            import cv2
            cv2.destroyAllWindows()
        except Exception:
            pass
        return "✅ Camera closed"
    return "⚠️ Camera was not open"


def record_video(filename: str = None, duration: int = 5) -> str:
    """Record a video clip from the webcam."""
    try:
        import cv2
    except ImportError:
        return "❌ OpenCV not installed"

    if not filename:
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    path = os.path.join(os.getcwd(), filename)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "❌ No camera found"

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    fps = 20.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(path, fourcc, fps, (w, h))

    import time
    start = time.time()
    while time.time() - start < duration:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    return f"🎥 Video saved: {path} ({duration}s)"


def get_camera_info() -> str:
    """Return available camera indices and their properties."""
    try:
        import cv2
    except ImportError:
        return "❌ OpenCV not installed"

    info = []
    for i in range(4):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            info.append(f"Camera {i}: {w}x{h} @ {fps:.0f}fps")
            cap.release()
    return "\n".join(info) if info else "No cameras found"
