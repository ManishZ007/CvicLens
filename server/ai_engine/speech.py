"""Bounded, local speech transcription. Audio is never persisted."""
import io
import os
from functools import lru_cache
from pathlib import Path
from threading import Lock

MAX_BYTES = 10 * 1024 * 1024
MAX_SECONDS = 60
_lock = Lock()


class SpeechUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_model():
    path = Path(os.environ.get(
        "CIVICLENS_WHISPER_MODEL",
        str(Path(__file__).resolve().parent.parent / "models" / "whisper-base"),
    ))
    if not (path / "model.bin").is_file():
        raise SpeechUnavailable("Speech model unavailable. Follow ai_engine/SPEECH_SETUP.md.")
    try:
        from faster_whisper import WhisperModel
        return WhisperModel(str(path), device="cpu", compute_type="int8", local_files_only=True)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise SpeechUnavailable("Could not load the local speech model.") from exc


def decode_audio(data):
    try:
        import av
        import numpy as np
    except ImportError as exc:
        raise SpeechUnavailable("Install the server speech dependencies first.") from exc
    chunks, count = [], 0
    try:
        with av.open(io.BytesIO(data)) as container:
            resampler = av.AudioResampler(format="fltp", layout="mono", rate=16000)
            for frame in container.decode(audio=0):
                for converted in resampler.resample(frame):
                    samples = converted.to_ndarray().reshape(-1)
                    count += samples.size
                    if count > MAX_SECONDS * 16000:
                        raise ValueError("Audio must be 60 seconds or shorter.")
                    chunks.append(samples)
            for converted in resampler.resample(None):
                samples = converted.to_ndarray().reshape(-1)
                count += samples.size
                if count > MAX_SECONDS * 16000:
                    raise ValueError("Audio must be 60 seconds or shorter.")
                chunks.append(samples)
    except (av.FFmpegError, IndexError) as exc:
        raise ValueError("Upload a valid audio recording.") from exc
    if not count:
        raise ValueError("The recording contains no audio.")
    return np.concatenate(chunks)


def transcribe_audio(data, language):
    if language not in {"en", "hi", "mr"}:
        raise ValueError("Choose English, Hindi or Marathi.")
    if not data or len(data) > MAX_BYTES:
        raise ValueError("Upload audio between 1 byte and 10 MB.")
    audio = decode_audio(data)
    # One CPU inference at a time; a busy server returns promptly.
    if not _lock.acquire(blocking=False):
        raise SpeechUnavailable("Speech service is busy. Try again shortly.")
    try:
        model = get_model()
        segments, _ = model.transcribe(
            audio, language=language, beam_size=5, vad_filter=True,
            condition_on_previous_text=False,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
    except (RuntimeError, OSError) as exc:
        if isinstance(exc, SpeechUnavailable):
            raise
        raise SpeechUnavailable("Speech transcription failed. Try again.") from exc
    finally:
        _lock.release()
    return {"text": text, "language": language, "duration_seconds": round(len(audio) / 16000, 2),
            "method": "faster-whisper"}
