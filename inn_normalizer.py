"""WHO INN 매칭 (헌법 v3). 브랜드 맵 기반으로 inn_name 등을 채움."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, TypedDict


class NormalizedRecord(TypedDict, total=False):
    inn_name: str
    inn_id: str
    inn_match_type: str


@dataclass
class NormalizedResult:
    success: bool
    inn_name: str | None = None
    inn_id: str | None = None
    inn_match_type: str = "none"


BRAND_TO_INN: dict[str, str] = {
    "hydrine": "hydroxyurea",
    "gadvoa": "gadobutrol",
    "sereterol": "fluticasone / salmeterol",
    "activair": "fluticasone / salmeterol",
    "omethyl": "omega-3-acid ethyl esters",
    "rosumeg": "rosuvastatin / omega-3-acid ethyl esters",
    "atmeg": "atorvastatin / omega-3-acid ethyl esters",
    "ciloduo": "cilostazol / rosuvastatin",
    "gastiin": "mosapride",
}


class InnNormalizer:
    def __init__(self) -> None:
        self._brand_map: dict[str, str] = {}

    def load_reference(self) -> None:
        """Load the bundled brand-to-INN reference map."""
        for brand, inn in BRAND_TO_INN.items():
            self.register_brand(brand, inn)

    def register_brand(self, brand: str, inn: str) -> None:
        self._brand_map[brand.strip().lower()] = inn.strip()

    def normalize(self, text: str) -> NormalizedResult:
        record = self.normalize_record({"trade_name": text, "scientific_name": text})
        inn_name = record.get("inn_name")
        return NormalizedResult(
            success=bool(inn_name),
            inn_name=inn_name,
            inn_id=record.get("inn_id"),
            inn_match_type=record.get("inn_match_type", "none"),
        )

    def normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        trade = (record.get("trade_name") or "").strip()
        if not trade:
            record["inn_match_type"] = "none"
            return record

        inn = self._brand_map.get(trade.lower())
        if inn is None:
            for key, val in self._brand_map.items():
                if key.lower() in trade.lower() or trade.lower() in key.lower():
                    inn = val
                    break

        if inn:
            slug = re.sub(r"[^a-z0-9]+", "_", inn.lower()).strip("_")
            record["inn_name"] = inn
            record["inn_id"] = f"inn_{slug}"
            record["inn_match_type"] = "brand_map"
        else:
            sci = (record.get("scientific_name") or "").strip()
            if sci:
                slug = re.sub(r"[^a-z0-9]+", "_", sci.lower()).strip("_")[:80]
                record["inn_name"] = sci.split("&&")[0].strip()
                record["inn_id"] = f"fallback_{slug}"
                record["inn_match_type"] = "scientific_fallback"
            else:
                record["inn_match_type"] = "unresolved"

        return record


_inn = InnNormalizer()
_inn.load_reference()

INNNormalizer = InnNormalizer
