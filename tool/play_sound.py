import os
import platform

from tool.tool import Tool


class PlaySound(Tool):

    def __init__(self, audio_file: str):
        self.audio_file = audio_file

    def run(self):
        system = platform.system()
        if system == "Darwin":
            os.system(f"afplay {self.audio_file}")
        elif system == "Linux":
            os.system(f"mpg123 {self.audio_file}")
        else:
            try:
                from playsound import playsound

                playsound(self.audio_file)
            except Exception as e:
                print(f"🔇 播放失敗：{e}")
