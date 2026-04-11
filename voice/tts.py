import threading
import os
import queue


class TextToSpeech:
    def __init__(self):
        self._q: queue.Queue = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def speak(self, text: str, block: bool = False):
        if not text or not text.strip():
            return
        # Strip emoji and special chars that crash pyttsx3
        clean = text.encode("ascii", "ignore").decode("ascii").strip()
        if not clean:
            return
        if block:
            self._speak_now(clean)
        else:
            self._q.put(clean)

    def _worker(self):
        """Dedicated thread — pyttsx3 must run on same thread always."""
        engine = None
        while True:
            try:
                text = self._q.get(timeout=1)
            except queue.Empty:
                continue
            try:
                if engine is None:
                    engine = self._init_engine()
                if engine:
                    engine.say(text)
                    engine.runAndWait()
            except Exception as e:
                print(f"[TTS] Error: {e}")
                engine = None  # reset on crash

    def _init_engine(self):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 0.9)
            # Prefer Microsoft Zira (female) on Windows
            voices = engine.getProperty("voices")
            for v in voices:
                if any(x in v.name.lower() for x in ("zira", "female", "hazel")):
                    engine.setProperty("voice", v.id)
                    break
            return engine
        except Exception as e:
            print(f"[TTS] Init failed: {e}")
            return None

    def _speak_now(self, text: str):
        """Blocking speak — used when block=True."""
        done = threading.Event()
        def _run():
            try:
                import pyttsx3
                e = pyttsx3.init()
                e.setProperty("rate", 165)
                e.say(text)
                e.runAndWait()
            except Exception as ex:
                print(f"[TTS] Blocking speak error: {ex}")
            finally:
                done.set()
        threading.Thread(target=_run, daemon=True).start()
        done.wait(timeout=15)
