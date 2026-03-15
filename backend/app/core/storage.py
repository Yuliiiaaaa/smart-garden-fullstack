# app/core/storage.py
import boto3
from botocore.config import Config
from fastapi import HTTPException, UploadFile
import uuid
import os
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version='s3v4')
        )
        self.bucket = settings.S3_BUCKET_NAME

    async def upload_file(self, file: UploadFile, folder: str = "uploads") -> str:
        # Проверка размера файла
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > settings.MAX_FILE_SIZE:
            raise HTTPException(400, f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes")
        
        # Проверка MIME-типа
        if file.content_type not in settings.ALLOWED_MIME_TYPES:
            raise HTTPException(400, f"File type not allowed: {file.content_type}")

        # Генерация уникального ключа
        ext = os.path.splitext(file.filename)[1]
        key = f"{folder}/{uuid.uuid4()}{ext}"
        
        # Загрузка в S3
        self.client.upload_fileobj(file.file, self.bucket, key, 
                                   ExtraArgs={"ContentType": file.content_type})
        return key

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str | None:
        """Генерирует временную ссылку для безопасного доступа к файлу."""
        try:
            return self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expires_in
            )
        except Exception:
            return None

    def delete_file(self, key: str) -> bool:
        """Удаляет файл из хранилища."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False