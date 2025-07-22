from typing import Optional

from openai import OpenAI, NotGiven, NOT_GIVEN


class OpenAIClient:

    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI()
        self.model = model

    def transcribe(
        self,
        audio_path: str,
        prompt: str | NotGiven = NOT_GIVEN,
        language: str | NotGiven = NOT_GIVEN,
    ) -> Optional[str]:
        try:
            with open(audio_path, "rb") as f:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", file=f, language=language, prompt=prompt
                )
            print(f"🗣️ Whisper 辨識結果：{transcript.text}")
            return transcript.text
        except Exception as e:
            print(f"❌ Whisper 轉錄失敗：{e}")
            return None

    def complete(
        self,
        user_prompt: str,
        temperature: float,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        b64_image: Optional[str] = None,
    ) -> str:
        if b64_image:
            user_role_prompt = {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            }
        else:
            user_role_prompt = {"role": "user", "content": user_prompt}

        if system_prompt:
            messages = [
                {"role": "system", "content": system_prompt},
                user_role_prompt,
            ]
        else:
            messages = [user_role_prompt]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        reply = response.choices[0].message.content.strip()
        return reply

    def true_or_false(self, user_prompt: str) -> bool:
        try:
            reply = self.complete(
                user_prompt=user_prompt,
                temperature=0,
                max_tokens=10,
            )
            return reply.startswith("是")
        except Exception as e:
            print(f"GPT 錯誤：{e}")
            return False
