from typing import Optional

from dotenv import load_dotenv

from componment.ai import OpenAIClient
from componment.audio import AudioRecorder
from tool.count_people import CountPeople
from tool.play_sound import PlaySound
from tool.s3 import UploadFileToS3
from tool.speech_to_text import SpeechToText

load_dotenv()

openai_client = OpenAIClient()
audio_recorder = AudioRecorder()


def transcribe_audio(file_path: str) -> Optional[str]:
    return openai_client.transcribe(
        prompt="這是語音指令，可能包含：播放聲音、語音轉文字、STT、偵測人數、現場人數等詞彙。",
        audio_path=file_path,
        language="zh",
    )


def classify_intent(user_command: str) -> str:
    system_prompt = (
        "你是一個語音指令意圖分類器，請從以下意圖中選擇一個最符合輸入指令的：\n"
        "1. 播放聲音（如：播放嗽叭、播放聲音、讓喇叭發聲）\n"
        "2. 語音轉文字（如：STT、語音轉文字）\n"
        "3. 偵測人數（如：現場人數、鏡頭中人數）\n"
        "只回答意圖名稱，不需多餘說明。"
    )

    return openai_client.complete(
        system_prompt=system_prompt,
        user_prompt=user_command,
        temperature=0,
    )


def should_turn_on_speaker(user_command: str) -> bool:
    user_prompt = f"""
                你是一個語音助理。請判斷以下語句是否表示要讓喇叭發聲：
                「{user_command}」
                如果語意接近「播放嗽叭」、「播放聲音」、「讓喇叭發聲」等，請回答「是」，否則回答「否」。
                """
    return openai_client.true_or_false(user_prompt)


def should_run_speech_to_text(user_command: str) -> bool:
    user_prompt = f"""
                你是一個語音助理。請判斷以下語句是否表示要執行語音轉文字（Speech-to-Text）操作：
                「{user_command}」
                如果語意接近「STT」、「語音轉文字」、「語音辨識」等，請回答「是」，否則回答「否」。
                """
    return openai_client.true_or_false(user_prompt)


def should_count_people(user_command: str) -> bool:
    user_prompt = f"""
                你是一個語音助理。請判斷以下語句是否表示要執行透過camera取得畫面中人數操作：
                「{user_command}」
                如果語意接近「現場人數」、「鏡頭中人數」等，請回答「是」，否則回答「否」。
                """
    return openai_client.true_or_false(user_prompt)


if __name__ == "__main__":
    intent_file_name = "tmp/intent.wav"
    audio_recorder.record_with_vad(filename=intent_file_name, timeout=5)
    transcript = transcribe_audio(intent_file_name)
    intent = classify_intent(user_command=transcript)

    print(f"🧠 偵測意圖為：{intent}")
    match intent:
        case "播放聲音":
            if should_turn_on_speaker(user_command=transcript):
                print(f"📢 意圖：{transcript} --> 「播放聲音」中...")
                PlaySound(audio_file="sound/button-pressed.mp3").run()
            else:
                print(f"🔕 意圖：{transcript} --> 非「{intent}」指令")
        case "語音轉文字":
            if should_run_speech_to_text(user_command=transcript):
                print(f"📢 意圖：{transcript} --> 執行「語音轉文字」中...")
                files = SpeechToText(
                    openai_client=openai_client, audio_recorder=audio_recorder
                ).run()
                UploadFileToS3(
                    files=files,
                    bucket_name="ai-voice-assistant",
                ).run()
            else:
                print(f"🔕 意圖：{transcript} --> 非「{intent}」指令")
        case "偵測人數":
            if should_count_people(user_command=transcript):
                print(f"📢 意圖：{transcript} --> 執行「偵測人數」中...")
                people = CountPeople(
                    openai_client=openai_client,
                ).run()
                print(f"👥 {people}")
            else:
                print(f"🔕 意圖：{transcript} --> 非「{intent}」指令")
        case _:
            print(f"🔍 意圖：{transcript}：無法辨識")
