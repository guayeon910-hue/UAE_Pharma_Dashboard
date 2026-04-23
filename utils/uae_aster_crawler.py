import asyncio
import json
import logging
import re
from typing import Optional
from playwright.async_api import async_playwright

from utils.db import get_client

logger = logging.getLogger("uae.aster_crawler")

class AsterPharmacyCrawler:
    """Aster Pharmacy 실시간 검색 크롤러"""

    def __init__(self):
        self.base_url = "https://www.myaster.com/en/online-pharmacy/searchresult?text="

    async def search_and_save(self, keyword: str) -> bool:
        """키워드로 검색하고 결과를 Supabase에 저장합니다."""
        if not keyword or len(keyword) < 3:
            return False

        logger.info(f"[Aster] Searching for: {keyword}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()

            products_found = []

            try:
                # 검색 페이지 로드
                search_url = f"{self.base_url}{keyword}"
                await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
                
                # __NEXT_DATA__ 추출
                try:
                    data_text = await page.locator('#__NEXT_DATA__').inner_text(timeout=5000)
                    data = json.loads(data_text)
                    items = data.get('props', {}).get('pageProps', {}).get('facetResponse', {}).get('data', [])
                    
                    for item in items:
                        title = item.get("name", "")
                        if not title:
                            continue
                            
                        price = item.get("price")
                        special_price = item.get("specialPrice")
                        
                        final_price = special_price if special_price else price
                        if not final_price:
                            continue

                        # Extract INN or use keyword
                        inn = keyword
                        manufacturer = item.get("brandDetails", {}).get("brandName", "")
                        
                        products_found.append({
                            "trade_name": title,
                            "inn": inn,
                            "pharmacy_price_aed": float(final_price),
                            "manufacturer": manufacturer,
                            "source": "Aster Pharmacy"
                        })
                except Exception as e:
                    logger.error(f"[Aster] Failed to parse __NEXT_DATA__: {e}")
                            
            except Exception as e:
                logger.error(f"[Aster] Navigation/Parse error: {e}")
            finally:
                await browser.close()

        if products_found:
            logger.info(f"[Aster] Found {len(products_found)} products. Saving to Supabase...")
            self._save_to_db(products_found)
            return True
        else:
            logger.info("[Aster] No products found.")
            return False

    def _save_to_db(self, products: list[dict]):
        sb = get_client()
        upsert_payload = []
        for p in products:
            trade_name = p["trade_name"][:255]
            inn = p["inn"][:255] if p["inn"] else "Unknown"
            
            upsert_payload.append({
                "source_label": p["source"],
                "trade_name": trade_name,
                "inn_name": inn,
                "pharmacy_price_aed": p["pharmacy_price_aed"],
                "manufacturer": p["manufacturer"][:255]
            })
            
        try:
            res = sb.table("uae_price_reference").upsert(
                upsert_payload, 
                on_conflict="inn_name,trade_name,source_label"
            ).execute()
            logger.info(f"[Aster] Upsert successful: {len(res.data)} rows affected.")
        except Exception as e:
            logger.error(f"[Aster] Supabase upsert error: {e}")

async def test_run():
    crawler = AsterPharmacyCrawler()
    await crawler.search_and_save("Seretide")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_run())
