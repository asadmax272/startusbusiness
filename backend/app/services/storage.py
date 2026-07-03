"""
Document storage service.

Real Supabase Storage integration (S3-compatible REST API), using the
service role key so the backend can read/write regardless of bucket RLS
policies. Falls back to local disk ONLY when SUPABASE_URL isn't set, which
is intended purely for `docker-compose up` local dev without a Supabase
project — production must set SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY, or
uploaded documents will not survive a redeploy (see docs/DEPLOYMENT_AUDIT.md §4).
"""

import uuid
from pathlib import Path

import httpx

from app.core.config import settings

_LOCAL_ROOT = Path(settings.storage_root)


def _using_supabase() -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


def build_key(order_id: str, file_name: str) -> str:
    ext = Path(file_name).suffix
    return f"{order_id}/{uuid.uuid4().hex}{ext}"


def save_file(key: str, content: bytes) -> None:
    if _using_supabase():
        url = f"{settings.supabase_url}/storage/v1/object/{settings.storage_bucket}/{key}"
        resp = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "apikey": settings.supabase_service_role_key,
                "Content-Type": "application/octet-stream",
                "x-upsert": "true",
            },
            content=content,
            timeout=30,
        )
        resp.raise_for_status()
        return

    path = _LOCAL_ROOT / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def read_file(key: str) -> bytes:
    if _using_supabase():
        url = f"{settings.supabase_url}/storage/v1/object/{settings.storage_bucket}/{key}"
        resp = httpx.get(
            url,
            headers={
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "apikey": settings.supabase_service_role_key,
            },
            timeout=30,
        )
        if resp.status_code == 404:
            raise FileNotFoundError(key)
        resp.raise_for_status()
        return resp.content

    path = _LOCAL_ROOT / key
    if not path.exists():
        raise FileNotFoundError(key)
    return path.read_bytes()


def delete_file(key: str) -> None:
    if _using_supabase():
        url = f"{settings.supabase_url}/storage/v1/object/{settings.storage_bucket}/{key}"
        httpx.delete(
            url,
            headers={
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "apikey": settings.supabase_service_role_key,
            },
            timeout=30,
        )
        return

    path = _LOCAL_ROOT / key
    if path.exists():
        path.unlink()


if not _using_supabase():
    _LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
