"""
Ferramentas de integração com MinIO / S3
"""

from __future__ import annotations

import json
from typing import Any

import boto3
from botocore.exceptions import ClientError
from django.conf import settings


def create_minio_client() -> boto3.client:  # type: ignore
    """Retorna um client boto3 configurado para o endpoint do MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=getattr(settings, "AWS_S3_REGION_NAME", "us-east-1"),
        config=boto3.session.Config(signature_version="s3v4"),
    )


def bucket_exists(bucket: str) -> bool:
    client = create_minio_client()
    try:
        client.head_bucket(Bucket=bucket)
        return True
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            return False
        raise  # erro inesperado


def create_bucket_if_not_exists(bucket: str | None = None) -> bool:
    """Cria o bucket caso ainda não exista."""
    bucket = bucket or settings.AWS_STORAGE_BUCKET_NAME
    if bucket_exists(bucket):
        return True

    client = create_minio_client()
    client.create_bucket(Bucket=bucket)
    return True


def set_static_prefix_read_only(
    bucket: str | None = None, prefix: str = "static/*"
) -> None:
    """
    Aplica uma bucket-policy que libera leitura anônima no prefixo informado
    (padrão: static/*). Idempotente – substitui ou cria a policy.
    """
    bucket = bucket or settings.AWS_STORAGE_BUCKET_NAME

    policy: dict[str, Any] = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket}/{prefix}"],
            }
        ],
    }

    client = create_minio_client()
    client.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))


def upload_test_file() -> bool:
    """Faz upload de um arquivo texto simples para validar permissões."""
    try:
        client = create_minio_client()
        content = "Arquivo de teste para MinIO".encode()
        client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key="test/test_file.txt",
            Body=content,
            ContentType="text/plain",
        )
        return True
    except Exception:
        return False
