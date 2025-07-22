import queue
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import webrtcvad


@dataclass
class VADConfig:
    audio_queue = queue.Queue()
    vad = webrtcvad.Vad(2)
    sample_rate: int = 16000
    frame_duration_ms: int = 30

    @property
    def frame_size(self) -> int:
        return int(self.sample_rate * self.frame_duration_ms / 1000)

    def audio_callback(self, indata, frames, time_info, status):
        audio = np.int16(indata[:, 0] * 32767)
        is_speech = self.vad.is_speech(audio.tobytes(), self.sample_rate)
        if is_speech:
            self.audio_queue.put(audio)


class AudioRecorder:

    def __init__(self, vad_config: Optional[VADConfig] = None):
        self.vad_config = vad_config or VADConfig()

    def record_with_vad(self, filename: str, timeout: int) -> bool:
        print("🎙️ 等待語音輸入...")
        frames = []
        start_time = None

        with sd.InputStream(
            channels=1,
            samplerate=self.vad_config.sample_rate,
            blocksize=self.vad_config.frame_size,
            callback=self.vad_config.audio_callback,
        ):
            while True:
                try:
                    frame = self.vad_config.audio_queue.get(timeout=timeout)
                    frames.append(frame)
                    if start_time is None:
                        start_time = time.time()
                    if time.time() - start_time > timeout:
                        break
                except queue.Empty:
                    break

        if frames:
            audio = np.concatenate(frames)
            wav.write(filename, self.vad_config.sample_rate, audio)
            print(f"✅ 自動錄音完成：{filename}")
            return True
        else:
            print("⚠️ 沒有偵測到語音")
            return False
