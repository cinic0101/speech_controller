from componment.ai import OpenAIClient
from componment.audio import AudioRecorder
from tool.tool import Tool


class SpeechToText(Tool):
    def __init__(self, openai_client: OpenAIClient, audio_recorder: AudioRecorder):
        self.audio_recorder = audio_recorder
        self.openai_client = openai_client

    def run(self) -> list[str]:
        file_path = "tmp/stt_audio.wav"
        self.audio_recorder.record_with_vad(filename=file_path, timeout=5)
        transcript = self.openai_client.transcribe(
            audio_path=file_path,
            language="zh"
        )
        output_path = file_path.replace(".wav", ".txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"📝 辨識結果已存入：{output_path}")
        return [file_path, output_path]
