"""Async S3-compatible (MinIO) object storage service using httpx."""

import base64
import hashlib
import hmac
from datetime import UTC, datetime

import httpx
from shared_config import S3Settings


class S3Service:
    """Lightweight async S3 service for MinIO.

    Uses simple httpx PUT/GET against MinIO's S3-compatible API.
    Sufficient for MVP; does not require boto3.
    """

    def __init__(self, settings: S3Settings) -> None:
        self._endpoint = settings.s3_endpoint.rstrip("/")
        self._bucket = settings.s3_bucket
        self._access_key = settings.s3_access_key
        self._secret_key = settings.s3_secret_key

    def get_url(self, key: str) -> str:
        """Return the full URL for a stored object."""
        return f"{self._endpoint}/{self._bucket}/{key}"

    def _sign_v2(
        self,
        method: str,
        path: str,
        content_type: str,
        date: str,
    ) -> str:
        """Generate an AWS Signature V2 Authorization header value.

        MinIO supports V2 signatures which are simpler than V4.
        """
        string_to_sign = f"{method}\n\n{content_type}\n{date}\n{path}"
        signature = hmac.new(
            self._secret_key.encode(),
            string_to_sign.encode(),
            hashlib.sha1,
        ).digest()
        encoded = base64.b64encode(signature).decode()
        return f"AWS {self._access_key}:{encoded}"

    async def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file to the bucket.

        Args:
            key: Object key (path within bucket).
            data: File content as bytes.
            content_type: MIME type of the object.

        Returns:
            Public URL of the uploaded object.
        """
        url = self.get_url(key)
        path = f"/{self._bucket}/{key}"
        date = datetime.now(tz=UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")
        auth = self._sign_v2("PUT", path, content_type, date)

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=5.0)) as client:
            response = await client.put(
                url,
                content=data,
                headers={
                    "Content-Type": content_type,
                    "Date": date,
                    "Authorization": auth,
                },
            )
            response.raise_for_status()
        return url

    async def download(self, key: str) -> bytes:
        """Download a file from the bucket.

        Args:
            key: Object key (path within bucket).

        Returns:
            File content as bytes.
        """
        url = self.get_url(key)
        path = f"/{self._bucket}/{key}"
        date = datetime.now(tz=UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")
        auth = self._sign_v2("GET", path, "", date)

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=5.0)) as client:
            response = await client.get(
                url,
                headers={
                    "Date": date,
                    "Authorization": auth,
                },
            )
            response.raise_for_status()
            return response.content
