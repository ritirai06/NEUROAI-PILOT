import os
import tempfile
import threading


class SpeechToText:
    def __init__(self, engine: str = None):
        self.engine = engine or os.getenv("STT_ENGINE", "google")

    def listen(self, duration: int = 5) -> str:
        try:
            audio_path = self._record(duration)
            if not audio_path:
                return ""
            if self.engine == "whisper":
                return self._transcribe_whisper(audio_path)
            return self._transcribe_google(audio_path)
        except Exception as e:
            return f"STT error: {e}"

    def _record(self, duration: int) -> str | None:
        try:
            import sounddevice as sd
            import soundfile as sf
        except ImportError:
            raise RuntimeError("sounddevice/soundfile not installed. Run: pip install sounddevice soundfile")

        sample_rate = 16000
        try:
            # Check mic is available
            devices = sd.query_devices()
            input_devs = [d for d in devices if d["max_input_channels"] > 0]
            if not input_devs:
                raise RuntimeError("No microphone found")

            print(f"[STT] Recording {duration}s...")
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
                blocking=True,
            )
            path = os.path.join(tempfile.gettempdir(), "neuroai_input.wav")
            sf.write(path, audio, sample_rate)
            return path
        except Exception as e:
            raise RuntimeError(f"Microphone error: {e}")

    def _transcribe_google(self, audio_path: str) -> str:
        try:
            import speech_recognition as sr
        except ImportError:
            raise RuntimeError("SpeechRecognition not installed. Run: pip install SpeechRecognition")

        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise RuntimeError(f"Google STT API error: {e}")

    def _transcribe_whisper(self, audio_path: str) -> str:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise RuntimeError("faster-whisper not installed")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path, beam_size=5)
        return " ".join(s.text for s in segments).strip()

    def transcribe_file(self, path: str) -> str:
        if self.engine == "whisper":
            return self._transcribe_whisper(path)
        return self._transcribe_google(path)
