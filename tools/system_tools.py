import subprocess, sys, os, json, psutil, time, shutil, platform

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "apps.json")

def _platform():
    return "windows" if sys.platform.startswith("win") else ("mac" if sys.platform.startswith("darwin") else "linux")

def _apps():
    with open(CONFIG_PATH) as f:
        return json.load(f)["apps"]

# ── App control ───────────────────────────────────────────────────────────────

def open_app(app: str) -> str:
    p, apps = _platform(), _apps()
    key = app.lower().strip()
    if key not in apps:
        try:
            subprocess.Popen(key, shell=True)
            return f"Launched: {app}"
        except Exception as e:
            return f"App '{app}' not found: {e}"
    cmd = os.path.expandvars(apps[key].get(p, ""))
    if not cmd:
        return f"No command for {app} on {p}"
    try:
        subprocess.Popen(cmd, shell=True)
        return f"Opened {app}"
    except Exception as e:
        return f"Failed to open {app}: {e}"

def close_app(app: str) -> str:
    killed = [proc.info["name"] for proc in psutil.process_iter(["pid","name"])
              if app.lower() in proc.info["name"].lower() and not proc.kill()]
    return f"Closed: {', '.join(killed)}" if killed else f"No process found: {app}"

def run_command(cmd: str) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = r.stdout.strip() or r.stderr.strip()
        return out if out else f"Done (exit {r.returncode})"
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"

def take_screenshot(filename: str = "screenshot.png") -> str:
    path = os.path.join(os.getcwd(), filename)
    try:
        ps = (f'Add-Type -AssemblyName System.Windows.Forms,System.Drawing;'
              f'$b=New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,'
              f'[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height);'
              f'$g=[System.Drawing.Graphics]::FromImage($b);'
              f'$g.CopyFromScreen(0,0,0,0,$b.Size);'
              f"$b.Save('{path}');$g.Dispose();$b.Dispose()")
        subprocess.run(["powershell","-Command",ps], check=True, timeout=10)
        return f"Screenshot saved: {path}"
    except Exception as e:
        return f"Screenshot failed: {e}"

def wait(seconds: float) -> str:
    time.sleep(float(seconds))
    return f"Waited {seconds}s"

def respond(message: str) -> str:
    return message

# ── Clipboard ─────────────────────────────────────────────────────────────────

def copy_to_clipboard(text: str) -> str:
    try:
        subprocess.run(["powershell","-Command",f"Set-Clipboard -Value '{text}'"], check=True, timeout=5)
        return f"Copied to clipboard: {text[:50]}"
    except Exception as e:
        return f"Clipboard error: {e}"

def get_clipboard() -> str:
    try:
        r = subprocess.run(["powershell","-Command","Get-Clipboard"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or "Clipboard is empty"
    except Exception as e:
        return f"Clipboard error: {e}"

# ── Volume control ────────────────────────────────────────────────────────────

def set_volume(level: int) -> str:
    level = max(0, min(100, int(level)))
    try:
        ps = f"$obj = New-Object -ComObject WScript.Shell; 1..50 | ForEach-Object {{ $obj.SendKeys([char]174) }}; $vol = [math]::Round({level}/2); 1..$vol | ForEach-Object {{ $obj.SendKeys([char]175) }}"
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Volume error: {e}"

def mute_volume() -> str:
    try:
        ps = "$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]173)"
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return "Volume muted"
    except Exception as e:
        return f"Mute error: {e}"

def volume_up(amount: int = 10) -> str:
    try:
        ps = f"$obj = New-Object -ComObject WScript.Shell; 1..{amount//2} | ForEach-Object {{ $obj.SendKeys([char]175) }}"
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Volume increased by {amount}%"
    except Exception as e:
        return f"Volume error: {e}"

def volume_down(amount: int = 10) -> str:
    try:
        ps = f"$obj = New-Object -ComObject WScript.Shell; 1..{amount//2} | ForEach-Object {{ $obj.SendKeys([char]174) }}"
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Volume decreased by {amount}%"
    except Exception as e:
        return f"Volume error: {e}"

# ── System info ───────────────────────────────────────────────────────────────

def get_system_info() -> str:
    try:
        cpu    = psutil.cpu_percent(interval=1)
        mem    = psutil.virtual_memory()
        disk   = psutil.disk_usage("/")
        boot   = psutil.boot_time()
        uptime = time.time() - boot
        hours  = int(uptime // 3600)
        mins   = int((uptime % 3600) // 60)
        return (
            f"System: {platform.node()} | {platform.system()} {platform.release()}\n"
            f"CPU: {cpu}% | Cores: {psutil.cpu_count()}\n"
            f"RAM: {mem.percent}% used ({mem.used//1024//1024}MB / {mem.total//1024//1024}MB)\n"
            f"Disk: {disk.percent}% used ({disk.used//1024//1024//1024}GB / {disk.total//1024//1024//1024}GB)\n"
            f"Uptime: {hours}h {mins}m"
        )
    except Exception as e:
        return f"System info error: {e}"

def get_battery() -> str:
    try:
        b = psutil.sensors_battery()
        if not b:
            return "No battery (desktop PC)"
        status = "Charging" if b.power_plugged else "Discharging"
        mins   = int(b.secsleft // 60) if b.secsleft > 0 else 0
        return f"Battery: {b.percent:.0f}% | {status} | {mins}min remaining"
    except Exception as e:
        return f"Battery error: {e}"

def get_cpu_usage() -> str:
    try:
        per_core = psutil.cpu_percent(interval=1, percpu=True)
        avg      = sum(per_core) / len(per_core)
        return f"CPU: {avg:.1f}% avg | Cores: {', '.join(f'{c:.0f}%' for c in per_core[:4])}"
    except Exception as e:
        return f"CPU error: {e}"

def get_ram_usage() -> str:
    try:
        m = psutil.virtual_memory()
        s = psutil.swap_memory()
        return (f"RAM: {m.percent}% ({m.used//1024//1024}MB used / {m.total//1024//1024}MB total)\n"
                f"Swap: {s.percent}% ({s.used//1024//1024}MB / {s.total//1024//1024}MB)")
    except Exception as e:
        return f"RAM error: {e}"

def get_disk_usage(path: str = "/") -> str:
    try:
        if sys.platform.startswith("win"):
            path = "C:\\"
        d = psutil.disk_usage(path)
        return (f"Disk ({path}): {d.percent}% used\n"
                f"Used: {d.used//1024//1024//1024}GB | Free: {d.free//1024//1024//1024}GB | Total: {d.total//1024//1024//1024}GB")
    except Exception as e:
        return f"Disk error: {e}"

def get_running_processes(limit: int = 10) -> str:
    try:
        procs = sorted(psutil.process_iter(["pid","name","cpu_percent","memory_percent"]),
                       key=lambda p: p.info["memory_percent"] or 0, reverse=True)
        lines = [f"{p.info['name'][:25]:<25} PID:{p.info['pid']:<6} CPU:{p.info['cpu_percent']:.1f}% MEM:{p.info['memory_percent']:.1f}%"
                 for p in procs[:limit] if p.info["name"]]
        return "Top processes:\n" + "\n".join(lines)
    except Exception as e:
        return f"Process error: {e}"

def kill_process(name: str) -> str:
    killed = []
    for proc in psutil.process_iter(["pid","name"]):
        if name.lower() in proc.info["name"].lower():
            try:
                proc.kill()
                killed.append(proc.info["name"])
            except Exception:
                pass
    return f"Killed: {', '.join(killed)}" if killed else f"No process named '{name}'"

# ── File operations ───────────────────────────────────────────────────────────

def create_file(path: str, content: str = "") -> str:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File created: {path}"
    except Exception as e:
        return f"Create file error: {e}"

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(3000)
        return content if content else "File is empty"
    except Exception as e:
        return f"Read file error: {e}"

def delete_file(path: str) -> str:
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"Deleted file: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Deleted folder: {path}"
        return f"Not found: {path}"
    except Exception as e:
        return f"Delete error: {e}"

def list_files(path: str = ".") -> str:
    try:
        items = os.listdir(path)
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        dirs  = [d for d in items if os.path.isdir(os.path.join(path, d))]
        out   = f"Path: {os.path.abspath(path)}\n"
        out  += f"Folders ({len(dirs)}): {', '.join(dirs[:10])}\n" if dirs else ""
        out  += f"Files ({len(files)}): {', '.join(files[:15])}" if files else "No files"
        return out
    except Exception as e:
        return f"List files error: {e}"

def move_file(src: str, dst: str) -> str:
    try:
        shutil.move(src, dst)
        return f"Moved: {src} → {dst}"
    except Exception as e:
        return f"Move error: {e}"

def copy_file(src: str, dst: str) -> str:
    try:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return f"Copied: {src} → {dst}"
    except Exception as e:
        return f"Copy error: {e}"

def zip_files(source: str, output: str = None) -> str:
    try:
        out = output or source.rstrip("/\\") + ".zip"
        shutil.make_archive(out.replace(".zip",""), "zip", source)
        return f"Zipped: {out}"
    except Exception as e:
        return f"Zip error: {e}"

def unzip_file(path: str, dest: str = ".") -> str:
    try:
        shutil.unpack_archive(path, dest)
        return f"Unzipped: {path} → {dest}"
    except Exception as e:
        return f"Unzip error: {e}"

def find_files(folder: str, pattern: str) -> str:
    import fnmatch
    try:
        matches = []
        for root, _, files in os.walk(folder):
            for f in files:
                if fnmatch.fnmatch(f.lower(), pattern.lower()):
                    matches.append(os.path.join(root, f))
        if not matches:
            return f"No files matching '{pattern}' in {folder}"
        return f"Found {len(matches)} files:\n" + "\n".join(matches[:20])
    except Exception as e:
        return f"Find error: {e}"

def get_file_info(path: str) -> str:
    try:
        s = os.stat(path)
        size = s.st_size
        unit = "B"
        if size > 1024*1024: size, unit = size//1024//1024, "MB"
        elif size > 1024: size, unit = size//1024, "KB"
        modified = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s.st_mtime))
        return f"File: {path}\nSize: {size}{unit} | Modified: {modified} | Type: {'dir' if os.path.isdir(path) else 'file'}"
    except Exception as e:
        return f"File info error: {e}"

# ── Network ───────────────────────────────────────────────────────────────────

def get_ip_address() -> str:
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        r = subprocess.run(["powershell","-Command","(Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing).Content"],
                           capture_output=True, text=True, timeout=8)
        public_ip = r.stdout.strip() if r.returncode == 0 else "unavailable"
        return f"Hostname: {hostname}\nLocal IP: {local_ip}\nPublic IP: {public_ip}"
    except Exception as e:
        return f"IP error: {e}"

def ping(host: str) -> str:
    try:
        r = subprocess.run(["ping","-n","4",host], capture_output=True, text=True, timeout=15)
        lines = [l for l in r.stdout.splitlines() if "ms" in l or "Average" in l or "Lost" in l]
        return "\n".join(lines) if lines else r.stdout[:300]
    except Exception as e:
        return f"Ping error: {e}"

def get_wifi_info() -> str:
    try:
        r = subprocess.run(["netsh","wlan","show","interfaces"], capture_output=True, text=True, timeout=8)
        lines = [l.strip() for l in r.stdout.splitlines()
                 if any(k in l for k in ["SSID","Signal","State","Radio"])]
        return "\n".join(lines) if lines else "No WiFi info available"
    except Exception as e:
        return f"WiFi error: {e}"

def get_network_speed() -> str:
    try:
        n1 = psutil.net_io_counters()
        time.sleep(1)
        n2 = psutil.net_io_counters()
        sent = (n2.bytes_sent - n1.bytes_sent) // 1024
        recv = (n2.bytes_recv - n1.bytes_recv) // 1024
        return f"Network speed: Upload {sent} KB/s | Download {recv} KB/s"
    except Exception as e:
        return f"Network speed error: {e}"

# ── Window / display ──────────────────────────────────────────────────────────

def lock_screen() -> str:
    try:
        subprocess.run(["rundll32.exe","user32.dll,LockWorkStation"], timeout=5)
        return "Screen locked"
    except Exception as e:
        return f"Lock error: {e}"

def shutdown(delay: int = 0) -> str:
    try:
        subprocess.run(["shutdown","/s",f"/t {delay}"], timeout=5)
        return f"Shutdown scheduled in {delay}s"
    except Exception as e:
        return f"Shutdown error: {e}"

def restart(delay: int = 0) -> str:
    try:
        subprocess.run(["shutdown","/r",f"/t {delay}"], timeout=5)
        return f"Restart scheduled in {delay}s"
    except Exception as e:
        return f"Restart error: {e}"

def sleep_pc() -> str:
    try:
        subprocess.run(["rundll32.exe","powrprof.dll,SetSuspendState 0,1,0"], timeout=5)
        return "PC going to sleep"
    except Exception as e:
        return f"Sleep error: {e}"

def show_notification(title: str, message: str) -> str:
    try:
        ps = (f'Add-Type -AssemblyName System.Windows.Forms;'
              f'$n = New-Object System.Windows.Forms.NotifyIcon;'
              f'$n.Icon = [System.Drawing.SystemIcons]::Information;'
              f'$n.Visible = $true;'
              f'$n.ShowBalloonTip(3000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info);'
              f'Start-Sleep -Seconds 4; $n.Dispose()')
        subprocess.Popen(["powershell","-Command",ps])
        return f"Notification sent: {title}"
    except Exception as e:
        return f"Notification error: {e}"

def set_wallpaper(path: str) -> str:
    try:
        ps = f"Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;public class W{{[DllImport(\"user32.dll\")]public static extern bool SystemParametersInfo(int a,int b,string c,int d);}}'; [W]::SystemParametersInfo(20,0,'{path}',3)"
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Wallpaper set: {path}"
    except Exception as e:
        return f"Wallpaper error: {e}"

# ── Keyboard / mouse ──────────────────────────────────────────────────────────

def press_key(key: str) -> str:
    try:
        ps = f"$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys('{key}')"
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Key press error: {e}"

def type_text(text: str) -> str:
    try:
        ps = f"$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys('{text}')"
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Typed: {text}"
    except Exception as e:
        return f"Type error: {e}"

# ── Date / time ───────────────────────────────────────────────────────────────

def get_datetime() -> str:
    import datetime
    now = datetime.datetime.now()
    return (f"Date: {now.strftime('%A, %B %d, %Y')}\n"
            f"Time: {now.strftime('%I:%M:%S %p')}\n"
            f"Timezone: {time.tzname[0]}")

def set_reminder(message: str, seconds: int) -> str:
    import threading
    def _remind():
        time.sleep(seconds)
        show_notification("NeuroAI Reminder", message)
    threading.Thread(target=_remind, daemon=True).start()
    return f"Reminder set: '{message}' in {seconds}s"

# ── Calculator ────────────────────────────────────────────────────────────────

def calculate(expression: str) -> str:
    try:
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return "Invalid expression"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"

# ── Text utilities ────────────────────────────────────────────────────────────

def search_in_file(path: str, keyword: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        matches = [(i+1, l.strip()) for i, l in enumerate(lines) if keyword.lower() in l.lower()]
        if not matches:
            return f"'{keyword}' not found in {path}"
        return f"Found {len(matches)} matches:\n" + "\n".join(f"Line {n}: {l}" for n, l in matches[:10])
    except Exception as e:
        return f"Search error: {e}"

def word_count(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        words = len(text.split())
        lines = text.count("\n") + 1
        chars = len(text)
        return f"File: {path}\nWords: {words} | Lines: {lines} | Characters: {chars}"
    except Exception as e:
        return f"Word count error: {e}"

# ── New tools ─────────────────────────────────────────────────────────────────

def get_screen_resolution() -> str:
    try:
        r = subprocess.run(["powershell","-Command",
            "Add-Type -AssemblyName System.Windows.Forms; $s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds; Write-Output \"$($s.Width)x$($s.Height)\""],
            capture_output=True, text=True, timeout=8)
        return f"Screen resolution: {r.stdout.strip()}"
    except Exception as e:
        return f"Resolution error: {e}"

def empty_recycle_bin() -> str:
    try:
        subprocess.run(["powershell","-Command","Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], timeout=10)
        return "Recycle bin emptied"
    except Exception as e:
        return f"Recycle bin error: {e}"

def get_env_var(name: str) -> str:
    val = os.environ.get(name)
    return f"{name} = {val}" if val else f"Environment variable '{name}' not found"

def set_brightness(level: int) -> str:
    level = max(0, min(100, int(level)))
    try:
        ps = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
        subprocess.run(["powershell","-Command",ps], timeout=8)
        return f"Brightness set to {level}%"
    except Exception as e:
        return f"Brightness error: {e}"

def get_installed_apps() -> str:
    try:
        r = subprocess.run(["powershell","-Command",
            "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName | Where-Object {$_.DisplayName} | Sort-Object DisplayName | Select-Object -First 30 | ForEach-Object {$_.DisplayName}"],
            capture_output=True, text=True, timeout=15)
        apps = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        return f"Installed apps ({len(apps)}):\n" + "\n".join(apps)
    except Exception as e:
        return f"Installed apps error: {e}"

def open_task_manager() -> str:
    try:
        subprocess.Popen(["taskmgr.exe"])
        return "Task Manager opened"
    except Exception as e:
        return f"Task Manager error: {e}"

def clear_temp_files() -> str:
    try:
        temp = os.environ.get("TEMP", "C:\\Windows\\Temp")
        count = 0
        for f in os.listdir(temp):
            fp = os.path.join(temp, f)
            try:
                if os.path.isfile(fp):
                    os.remove(fp)
                    count += 1
                elif os.path.isdir(fp):
                    shutil.rmtree(fp, ignore_errors=True)
                    count += 1
            except Exception:
                pass
        return f"Cleared {count} temp items from {temp}"
    except Exception as e:
        return f"Clear temp error: {e}"

def get_startup_programs() -> str:
    try:
        r = subprocess.run(["powershell","-Command",
            "Get-CimInstance Win32_StartupCommand | Select-Object Name,Command | ForEach-Object {\"$($_.Name): $($_.Command)\"}"],
            capture_output=True, text=True, timeout=10)
        lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        return "Startup programs:\n" + "\n".join(lines) if lines else "No startup programs found"
    except Exception as e:
        return f"Startup programs error: {e}"

def rename_file(src: str, new_name: str) -> str:
    try:
        dst = os.path.join(os.path.dirname(src), new_name)
        os.rename(src, dst)
        return f"Renamed: {src} → {dst}"
    except Exception as e:
        return f"Rename error: {e}"

def append_to_file(path: str, content: str) -> str:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Appended to: {path}"
    except Exception as e:
        return f"Append error: {e}"

def get_mouse_position() -> str:
    try:
        r = subprocess.run(["powershell","-Command",
            "Add-Type -AssemblyName System.Windows.Forms; $p=[System.Windows.Forms.Cursor]::Position; Write-Output \"$($p.X),$($p.Y)\""],
            capture_output=True, text=True, timeout=5)
        return f"Mouse position: {r.stdout.strip()}"
    except Exception as e:
        return f"Mouse position error: {e}"

def move_mouse(x: int, y: int) -> str:
    try:
        ps = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x},{y})"
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Mouse moved to ({x}, {y})"
    except Exception as e:
        return f"Move mouse error: {e}"

def mouse_click(x: int, y: int) -> str:
    try:
        ps = (f"Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;"
              f"public class M{{[DllImport(\"user32.dll\")]public static extern void mouse_event(int f,int x,int y,int c,int e);}}';"
              f"[M]::mouse_event(0x8001,{x},{y},0,0);[M]::mouse_event(0x8002,{x},{y},0,0)")
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Clicked at ({x}, {y})"
    except Exception as e:
        return f"Mouse click error: {e}"

def mouse_double_click(x: int, y: int) -> str:
    mouse_click(x, y)
    mouse_click(x, y)
    return f"Double-clicked at ({x}, {y})"

def right_click(x: int, y: int) -> str:
    try:
        ps = (f"Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;"
              f"public class M{{[DllImport(\"user32.dll\")]public static extern void mouse_event(int f,int x,int y,int c,int e);}}';"
              f"[M]::mouse_event(0x8008,{x},{y},0,0);[M]::mouse_event(0x8010,{x},{y},0,0)")
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Right-clicked at ({x}, {y})"
    except Exception as e:
        return f"Right click error: {e}"

def scroll_mouse(direction: str = "down", clicks: int = 3) -> str:
    try:
        delta = -120 * clicks if direction == "down" else 120 * clicks
        ps = (f"Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;"
              f"public class M{{[DllImport(\"user32.dll\")]public static extern void mouse_event(int f,int x,int y,int c,int e);}}';"
              f"[M]::mouse_event(0x0800,0,0,{delta},0)")
        subprocess.run(["powershell","-Command",ps], timeout=5)
        return f"Scrolled {direction} {clicks} clicks"
    except Exception as e:
        return f"Scroll error: {e}"
