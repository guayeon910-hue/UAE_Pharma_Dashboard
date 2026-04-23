"""Supabase products 테이블 래퍼 — UAE 전용.

⚠️ 안전 정책:
    이 모듈의 모든 쓰기 함수는 country='UAE' 행만 건드립니다.
    다른 팀(SG·UY 등)의 데이터를 읽거나 덮어쓰거나 삭제하지 않습니다.
    UAE 전용 보조 테이블(uae_price_reference 등)은 별도 utils 모듈에서 관리합니다.

환경변수:
  SUPABASE_URL
  SUPABASE_KEY
  SUPABASE_TIMEOUT_SEC (선택, 기본 8초)
  SUPABASE_DISABLED    (선택, 1/true/yes면 null client 사용)
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)

# ── UAE 격리 상수 ──────────────────────────────────────────────────────────────
_UAE_COUNTRY       = "UAE"
_UAE_SOURCE_PREFIX = "UAE:"   # source_name이 반드시 이 prefix로 시작해야 함

_client_cache: Any = None


class _NullResult:
    def __init__(self, data: list[dict[str, Any]] | None = None):
        self.data = data or []


class _NullQuery:
    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def is_(self, *_args, **_kwargs):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def or_(self, *_args, **_kwargs):
        return self

    def upsert(self, *_args, **_kwargs):
        return self

    def insert(self, *_args, **_kwargs):
        return self

    def update(self, *_args, **_kwargs):
        return self

    def delete(self, *_args, **_kwargs):
        return self

    def execute(self):
        return _NullResult()


class _NullSupabaseClient:
    def table(self, *_args, **_kwargs):
        return _NullQuery()


_NULL_CLIENT = _NullSupabaseClient()


def _env_truthy(name: str) -> bool:
    raw = str(os.environ.get(name, "") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def reset_client_cache() -> None:
    global _client_cache
    _client_cache = None


def get_client():
    """Supabase 클라이언트 싱글톤 반환.

    DB가 느리거나 자격증명이 없을 때도 앱 전체가 멈추지 않도록
    null client로 폴백합니다.
    """
    global _client_cache
    if _client_cache is None:
        if _env_truthy("SUPABASE_DISABLED"):
            log.warning("SUPABASE_DISABLED=1 설정으로 null client를 사용합니다.")
            _client_cache = _NULL_CLIENT
            return _client_cache

        url = str(os.environ.get("SUPABASE_URL", "") or "").strip()
        key = str(os.environ.get("SUPABASE_KEY", "") or "").strip()
        if not url or not key:
            log.warning("Supabase 자격증명이 없어 null client로 폴백합니다.")
            _client_cache = _NULL_CLIENT
            return _client_cache

        try:
            from supabase import create_client
            from supabase.lib.client_options import SyncClientOptions

            timeout = float(os.environ.get("SUPABASE_TIMEOUT_SEC", "8") or "8")
            _client_cache = create_client(
                url,
                key,
                options=SyncClientOptions(
                    postgrest_client_timeout=timeout,
                    storage_client_timeout=max(5, int(timeout)),
                    function_client_timeout=min(5, max(1, int(timeout))),
                    auto_refresh_token=False,
                    persist_session=False,
                ),
            )
        except Exception as exc:
            log.warning("Supabase client 초기화 실패 → null client 폴백: %s", exc)
            _client_cache = _NULL_CLIENT
    return _client_cache


get_supabase_client = get_client


# ── UAE 안전 가드 ──────────────────────────────────────────────────────────────

def _assert_uae_row(row: dict[str, Any]) -> None:
    """row가 UAE 소유 데이터인지 확인. 위반 시 ValueError 발생.

    공유 products 테이블에 다른 팀 데이터를 실수로 덮어쓰는 것을 방지합니다.
    """
    country     = row.get("country", "")
    source_name = row.get("source_name", "")
    product_id  = row.get("product_id", "")

    errors: list[str] = []
    if country and country != _UAE_COUNTRY:
        errors.append(f"country='{country}' (expected 'UAE')")
    if source_name and not source_name.startswith(_UAE_SOURCE_PREFIX):
        errors.append(f"source_name='{source_name}' (must start with 'UAE:')")
    if product_id and not product_id.startswith("UAE_"):
        errors.append(f"product_id='{product_id}' (must start with 'UAE_')")

    if errors:
        raise ValueError(
            f"[DB 안전장치] UAE가 아닌 데이터를 쓰려고 했습니다: {', '.join(errors)}. "
            "다른 팀의 데이터에 영향을 줄 수 없습니다."
        )


# ── 조회 함수 ─────────────────────────────────────────────────────────────────

def fetch_all_products(country: str = _UAE_COUNTRY) -> list[dict[str, Any]]:
    """products 테이블에서 UAE 품목 전체 조회 (deleted_at is null).

    country 인자는 항상 'UAE'로 고정됩니다. 다른 값을 전달하면 경고 후 'UAE'로 덮어씁니다.
    """
    if country != _UAE_COUNTRY:
        log.warning("[DB 안전장치] fetch_all_products: country='%s' 무시 → 'UAE' 강제 적용", country)
        country = _UAE_COUNTRY

    try:
        sb = get_client()
        r = (
            sb.table("products")
            .select("*")
            .eq("country", country)
            .is_("deleted_at", "null")
            .order("crawled_at", desc=True)
            .execute()
        )
        return r.data or []
    except Exception as exc:
        log.warning("fetch_all_products 실패 → 빈 리스트 폴백: %s", exc)
        return []


def fetch_kup_products(country: str = _UAE_COUNTRY) -> list[dict[str, Any]]:
    """UAE KUP 파이프라인 품목만 조회 (source_name='UAE:kup_pipeline').

    country 인자는 항상 'UAE'로 고정됩니다.
    """
    if country != _UAE_COUNTRY:
        log.warning("[DB 안전장치] fetch_kup_products: country='%s' 무시 → 'UAE' 강제 적용", country)
        country = _UAE_COUNTRY

    try:
        sb = get_client()
        r = (
            sb.table("products")
            .select("*")
            .eq("country", country)
            .eq("source_name", f"{country}:kup_pipeline")
            .is_("deleted_at", "null")
            .execute()
        )
        return r.data or []
    except Exception as exc:
        log.warning("fetch_kup_products 실패 → 빈 리스트 폴백: %s", exc)
        return []


# ── 쓰기 함수 ─────────────────────────────────────────────────────────────────

def upsert_product(row: dict[str, Any]) -> bool:
    """products 테이블에 UAE 행 upsert. 비-UAE 행은 ValueError 발생.

    ⚠️  country='UAE', source_name='UAE:...' 인 행만 허용합니다.
    """
    # 안전 가드: UAE가 아닌 데이터 차단
    row.setdefault("country", _UAE_COUNTRY)
    _assert_uae_row(row)

    sb = get_client()
    if sb is _NULL_CLIENT:
        log.warning("upsert_product 건너뜀: Supabase client 사용 불가")
        return False

    now = datetime.now(timezone.utc).isoformat()
    row.setdefault("crawled_at", now)
    row.setdefault("confidence", 0.5)
    try:
        sb.table("products").upsert(
            row,
            on_conflict="product_id",
        ).execute()
        return True
    except Exception as exc:
        log.error("upsert_product 실패: %s", exc)
        return False
