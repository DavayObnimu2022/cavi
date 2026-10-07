import io
import uuid
from minio import Minio
from fastapi import UploadFile


class MinioService:
    def __init__(self):
        self.client = Minio(
            "localhost:9000",
            access_key="root",
            secret_key="rootpassword",
            secure=False
        )
        self.bucket = "img"
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    async def upload_file(self, file: UploadFile, prefix: str = "") -> str:
        ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
        filename = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"

        contents = await file.read()
        self.client.put_object(
            self.bucket,
            filename,
            io.BytesIO(contents),
            length=len(contents),
            content_type=file.content_type or "application/octet-stream"
        )
        return filename

    def get_url(self, filename: str) -> str:
        return f"http://localhost:9000/{self.bucket}/{filename}"


minio_service = MinioService()