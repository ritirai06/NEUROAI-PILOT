"""
Window Manager - Force applications to foreground and ensure visibility.
Handles minimized, hidden, and background windows on Windows OS.
"""
import time
import subprocess
import psutil
from typing import Optional, Tuple

try:
    import win32gui
    import win32con
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class WindowManager:
    """Manages window visibility and focus on Windows."""
    
    @staticmethod
    def find_window_by_pid(pid: int, timeout: float = 5.0) -> Optional[int]:
        """Find window handle by process ID."""
        if not HAS_WIN32:
            return None
        
        hwnd_list = []
        
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnd_list.append(hwnd)
            return True
        
        start = time.time()
        while time.time() - start < timeout:
            hwnd_list.clear()
            win32gui.EnumWindows(callback, None)
            if hwnd_list:
                return hwnd_list[0]
            time.sleep(0.2)
        
        return None
    
    @staticmethod
    def find_window_by_title(title_fragment: str, timeout: float = 5.0) -> Optional[int]:
        """Find window handle by title fragment."""
        if not HAS_WIN32:
            return None
        
        hwnd_list = []
        
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title_fragment.lower() in window_title.lower():
                    hwnd_list.append(hwnd)
            return True
        
        start = time.time()
        while time.time() - start < timeout:
            hwnd_list.clear()
            win32gui.EnumWindows(callback, None)
            if hwnd_list:
                return hwnd_list[0]
            time.sleep(0.2)
        
        return None
    
    @staticmethod
    def find_window_by_class(class_name: str, timeout: float = 5.0) -> Optional[int]:
        """Find window by class name."""
        if not HAS_WIN32:
            return None
        
        start = time.time()
        while time.time() - start < timeout:
            hwnd = win32gui.FindWindow(class_name, None)
            if hwnd:
                return hwnd
            time.sleep(0.2)
        
        return None
    
    @staticmethod
    def bring_to_front(hwnd: int, max_attempts: int = 3) -> bool:
        """Bring window to foreground with retry mechanism."""
        if not HAS_WIN32 or not hwnd:
            return False
        
        for attempt in range(max_attempts):
            try:
                # Check if minimized and restore
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.3)
                
                # Show window if hidden
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.1)
                
                # Bring to top
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )
                time.sleep(0.1)
                
                # Remove topmost flag but keep on top
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_NOTOPMOST,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
                
                # Set foreground
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.1)
                
                # Verify it's in foreground
                if win32gui.GetForegroundWindow() == hwnd:
                    return True
                
                # Fallback: simulate Alt key to bypass Windows restrictions
                import win32api
                win32api.keybd_event(0x12, 0, 0, 0)  # Alt down
                time.sleep(0.05)
                win32gui.SetForegroundWindow(hwnd)
                win32api.keybd_event(0x12, 0, 2, 0)  # Alt up
                
                if win32gui.GetForegroundWindow() == hwnd:
                    return True
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    print(f"Failed to bring window to front: {e}")
                time.sleep(0.3)
        
        return False
    
    @staticmethod
    def maximize_window(hwnd: int) -> bool:
        """Maximize window."""
        if not HAS_WIN32 or not hwnd:
            return False
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception:
            return False
    
    @staticmethod
    def center_window(hwnd: int, width: int = 1200, height: int = 800) -> bool:
        """Center window on screen with specified size."""
        if not HAS_WIN32 or not hwnd:
            return False
        
        try:
            import win32api
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                x, y, width, height,
                win32con.SWP_SHOWWINDOW
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_window_info(hwnd: int) -> dict:
        """Get window information."""
        if not HAS_WIN32 or not hwnd:
            return {}
        
        try:
            rect = win32gui.GetWindowRect(hwnd)
            title = win32gui.GetWindowText(hwnd)
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_minimized = win32gui.IsIconic(hwnd)
            is_maximized = win32gui.IsZoomed(hwnd)
            
            return {
                "title": title,
                "position": (rect[0], rect[1]),
                "size": (rect[2] - rect[0], rect[3] - rect[1]),
                "visible": is_visible,
                "minimized": is_minimized,
                "maximized": is_maximized,
            }
        except Exception:
            return {}
    
    @classmethod
    def launch_and_focus(
        cls,
        command: str,
        wait_time: float = 2.0,
        title_hint: Optional[str] = None,
        maximize: bool = True
    ) -> Tuple[Optional[subprocess.Popen], bool]:
        """
        Launch application and ensure it's visible and focused.
        
        Args:
            command: Command to execute
            wait_time: Time to wait for window to appear
            title_hint: Window title fragment to search for
            maximize: Whether to maximize the window
        
        Returns:
            (process, success)
        """
        try:
            # Launch process
            if isinstance(command, str):
                process = subprocess.Popen(
                    command,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if HAS_WIN32 else 0
                )
            else:
                process = subprocess.Popen(command)
            
            pid = process.pid
            time.sleep(0.5)
            
            # Find window
            hwnd = None
            
            # Try by PID first
            hwnd = cls.find_window_by_pid(pid, timeout=wait_time)
            
            # Try by title if hint provided
            if not hwnd and title_hint:
                hwnd = cls.find_window_by_title(title_hint, timeout=wait_time)
            
            # If still not found, try to find any new window
            if not hwnd:
                time.sleep(wait_time)
                hwnd = cls.find_window_by_pid(pid, timeout=1.0)
            
            if hwnd:
                # Bring to front
                success = cls.bring_to_front(hwnd)
                
                # Maximize if requested
                if success and maximize:
                    cls.maximize_window(hwnd)
                
                return process, success
            
            return process, False
            
        except Exception as e:
            print(f"Launch error: {e}")
            return None, False
    
    @classmethod
    def focus_existing_window(cls, title_fragment: str, maximize: bool = False) -> bool:
        """Focus an already running application by window title."""
        hwnd = cls.find_window_by_title(title_fragment, timeout=2.0)
        if hwnd:
            success = cls.bring_to_front(hwnd)
            if success and maximize:
                cls.maximize_window(hwnd)
            return success
        return False
    
    @classmethod
    def focus_process_window(cls, process_name: str, maximize: bool = False) -> bool:
        """Focus window by process name (e.g., 'chrome.exe')."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    hwnd = cls.find_window_by_pid(proc.info['pid'], timeout=1.0)
                    if hwnd:
                        success = cls.bring_to_front(hwnd)
                        if success and maximize:
                            cls.maximize_window(hwnd)
                        return success
        except Exception:
            pass
        return False


# Convenience functions
def ensure_window_visible(hwnd: int) -> bool:
    """Ensure window is visible and focused."""
    return WindowManager.bring_to_front(hwnd)


def launch_visible(command: str, title_hint: str = None, maximize: bool = True) -> bool:
    """Launch app and ensure it's visible."""
    _, success = WindowManager.launch_and_focus(command, title_hint=title_hint, maximize=maximize)
    return success


def focus_app(title_or_process: str, maximize: bool = False) -> bool:
    """Focus existing app by title or process name."""
    # Try as title first
    if WindowManager.focus_existing_window(title_or_process, maximize):
        return True
    # Try as process name
    if '.' not in title_or_process:
        title_or_process += '.exe'
    return WindowManager.focus_process_window(title_or_process, maximize)
