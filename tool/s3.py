import os

import boto3

from tool.tool import Tool


class UploadFileToS3(Tool):

    def __init__(self, files: list[str], bucket_name: str):
        self.s3 = boto3.client("s3")
        self.files = files
        self.bucket_name = bucket_name

    def run(self):
        for file in self.files:
            filename = os.path.basename(file)
            self.s3.upload_file(file, self.bucket_name, filename)
            print(f"📄 {filename} 已上傳至 {self.bucket_name}")
