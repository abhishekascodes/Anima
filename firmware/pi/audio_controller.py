# sound playback and jaw servo flap sync for anima

import os
import struct
import time
import wave
from pathlib import Path


class SoundManager:
    def __init__(self, serial_bridge=None, audio_dir="firmware/audio"):
        self.bridge = serial_bridge
        self.audio_dir = Path(audio_dir)

    def play(self, sound_name, sync_jaw=True):
        path = self.audio_dir / sound_name
        if not path.exists():
            return

        with wave.open(str(path), "rb") as wf:
            rate = wf.getframerate()
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            total_frames = wf.getnframes()
            data = wf.readframes(total_frames)

        # Chunk audio into 30ms slices to track speech envelope
        chunk_ms = 30
        frames_per_chunk = int(rate * (chunk_ms / 1000.0))
        bytes_per_chunk = frames_per_chunk * channels * width

        for offset in range(0, len(data), bytes_per_chunk):
            chunk = data[offset : offset + bytes_per_chunk]
            if len(chunk) < 2:
                break

            # Calculate RMS amplitude
            samples = struct.unpack(f"<{len(chunk)//2}h", chunk)
            rms = (sum(s * s for s in samples) / len(samples)) ** 0.5

            if sync_jaw and self.bridge:
                # Open jaw if volume is above threshold
                if rms > 3000:
                    self.bridge.send("SERVO 3 1750")  # Mouth open
                else:
                    self.bridge.send("SERVO 3 1500")  # Mouth closed

            time.sleep(chunk_ms / 1000.0)

        # Ensure mouth is closed after audio finishes
        if sync_jaw and self.bridge:
            self.bridge.send("SERVO 3 1500")


if __name__ == "__main__":
    import sys

    mgr = SoundManager()
    target = sys.argv[1] if len(sys.argv) > 1 else "countdown_pip.wav"
    print(f"Testing sound playback on: {target}")
    mgr.play(target)
    print("Done!")
