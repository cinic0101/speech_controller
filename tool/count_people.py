import base64

import cv2

from componment.ai import OpenAIClient
from tool.tool import Tool


class CountPeople(Tool):

    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    def _capture_image(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("無法存取相機，請檢查相機權限")
            return None

        ret, frame = cap.read()
        cap.release()
        return frame if ret else None

    def _frame_to_base64(self, frame):
        _, buffer = cv2.imencode(".jpg", frame)
        b64 = base64.b64encode(buffer).decode()
        return b64

    def run(self):
        frame = self._capture_image()
        if frame is not None:
            b64_image = self._frame_to_base64(frame)
            return self.openai_client.complete(
                user_prompt=f"圖片裡有幾個人？", b64_image=b64_image, temperature=0
            )
        else:
            return None
