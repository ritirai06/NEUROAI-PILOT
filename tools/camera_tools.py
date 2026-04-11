"""
Camera tools — OpenCV webcam capture.
"""
import os
import threading
from datetime import datetime

_cap = None
_window_thread = None


def open_camera() -> str:
    """Open webcam in a live preview window."""
    global _cap, _window_thread
    try:
        import cv2
    except ImportError:
        return "❌ OpenCV not installed. Run: pip install opencv-python"

    if _cap and _cap.isOpened():
        return "⚠️ Camera already open"

    _cap = cv2.VideoCapture(0)
    if not _cap.isOpened():
        _cap = None
        return "❌ No camera found. Check webcam connection."

    def _show():
        while _cap and _cap.isOpened():
            ret, frame = _cap.read()
            if not ret:
                break
            cv2.imshow("NeuroAI Camera — Press Q to close, S to snap", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                click_photo()
        cv2.destroyAllWindows()

    _window_thread = threading.Thread(target=_show, daemon=True)
    _window_thread.start()
    return "✅ Camera opened — press S to snap, Q to close"


def click_photo(filename: str = None) -> str:
    """Capture a photo from the open webcam."""
    global _cap
    try:
        import cv2
    except ImportError:
        return "❌ OpenCV not installed"

    # Open camera if not already open
    if _cap is None or not _cap.isOpened():
        result = open_camera()
        if "❌" in result:
            return result
        import time; time.sleep(1)  # let camera warm up

    ret, frame = _cap.read()
    if not ret:
        return "❌ Failed to capture frame"

    if not filename:
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    path = os.path.join(os.getcwd(), filename)
    import cv2
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
