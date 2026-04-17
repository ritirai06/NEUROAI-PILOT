"""
Camera tools.
Prefers opening the native camera app visibly; falls back to OpenCV preview.
"""
import os
import subprocess
import sys
import tempfile
import threading
from datetime import datetime

_cap = None
_window_thread = None


def open_camera() -> str:
    """Open camera visibly on screen."""
    global _window_thread

    # Primary path on Windows: native Camera app.
    if os.name == "nt":
        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "", "microsoft.windows.camera:"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return "OK Camera app opened"
        except Exception:
            pass

    # Fallback path: OpenCV live preview in separate process.
    script = r"""
import cv2
import sys

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("NO_CAMERA")
    sys.exit(1)

window_name = "NeuroAI Camera - Press Q to close"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow(window_name, frame)
    if (cv2.waitKey(1) & 0xFF) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
"""
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8")
        tmp.write(script)
        tmp.close()

        def _run():
            subprocess.Popen(
                [sys.executable, tmp.name],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
            )

        _window_thread = threading.Thread(target=_run, daemon=True)
        _window_thread.start()
        return "OK Camera preview opened - press Q to close"
    except Exception as e:
        return f"ERROR Camera open failed: {e}"


def click_photo(filename: str = None) -> str:
    """Capture a photo from webcam."""
    try:
        import cv2
    except ImportError:
        return "ERROR OpenCV not installed"

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "ERROR No camera found"

    import time
    time.sleep(0.5)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "ERROR Failed to capture frame"

    if not filename:
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    path = os.path.join(os.getcwd(), filename)
    cv2.imwrite(path, frame)
    return f"Photo saved: {path}"


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
        return "OK Camera closed"
    return "WARN Camera was not open"


def record_video(filename: str = None, duration: int = 5) -> str:
    """Record a video clip from the webcam."""
    try:
        import cv2
    except ImportError:
        return "ERROR OpenCV not installed"

    if not filename:
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    path = os.path.join(os.getcwd(), filename)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "ERROR No camera found"

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
    return f"Video saved: {path} ({duration}s)"


def get_camera_info() -> str:
    """Return available camera indices and their properties."""
    try:
        import cv2
    except ImportError:
        return "ERROR OpenCV not installed"

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
