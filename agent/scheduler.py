import json
import os
import threading
import time
from datetime import datetime

SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), "..", "memory", "schedules.json")


class Scheduler:
    def __init__(self):
        os.makedirs(os.path.dirname(SCHEDULE_FILE), exist_ok=True)
        self._tasks = self._load()
        self._running = False

    def _load(self) -> list:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE) as f:
                return json.load(f)
        return []

    def _save(self):
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(self._tasks, f, indent=2)

    def add_task(self, command: str, cron: str):
        """cron format: 'HH:MM' for daily tasks."""
        self._tasks.append({"command": command, "cron": cron, "last_run": None})
        self._save()

    def remove_task(self, index: int):
        if 0 <= index < len(self._tasks):
            self._tasks.pop(index)
            self._save()

    def list_tasks(self) -> list:
        return self._tasks

    def start(self, execute_fn):
        """Start background scheduler thread."""
        self._running = True
        thread = threading.Thread(target=self._loop, args=(execute_fn,), daemon=True)
        thread.start()

    def stop(self):
        self._running = False

    def _loop(self, execute_fn):
        while self._running:
            now = datetime.now().strftime("%H:%M")
            today = datetime.now().strftime("%Y-%m-%d")
            for task in self._tasks:
                if task["cron"] == now and task.get("last_run") != today:
                    task["last_run"] = today
                    self._save()
                    try:
                        execute_fn(task["command"])
                    except Exception as e:
                        print(f"[Scheduler] Error running task: {e}")
            time.sleep(30)
