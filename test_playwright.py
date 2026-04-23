import asyncio
from typing import Optional

def _fetch_excel_data_sync(urls: list[str]) -> Optional[bytes]:
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        target_href = None
        for url in urls:
            print(f"Trying {url} ...")
            try:
                page.goto(url, timeout=60000)
                page.wait_for_timeout(5000)
                
                links = page.query_selector_all("a[href]")
                print(f"Found {len(links)} links")
                for link in links:
                    href = link.get_attribute("href")
                    if href and any(ext in href.lower() for ext in [".xlsx", ".xls", ".ashx"]):
                        if href.startswith("http"):
                            target_href = href
                        elif href.startswith("/"):
                            from urllib.parse import urlparse
                            parsed = urlparse(url)
                            target_href = f"{parsed.scheme}://{parsed.netloc}{href}"
                        else:
                            from urllib.parse import urljoin
                            target_href = urljoin(url, href)
                        print(f"Found target: {target_href}")
                        break
                
                if target_href:
                    break
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                pass

        if not target_href:
            browser.close()
            return None
            
        print(f"Downloading from {target_href} ...")
        try:
            resp = context.request.get(target_href, timeout=30000)
            if resp.status == 200:
                body = resp.body()
                ct = resp.headers.get('content-type', '').lower()
                print(f"Downloaded {len(body)} bytes. Content-Type: {ct}")
                if len(body) > 10000 and ("excel" in ct or "spreadsheet" in ct or "octet-stream" in ct or "application/vnd" in ct):
                    browser.close()
                    return body
                else:
                    print("Does not look like an excel file.")
            else:
                print(f"Failed to download. Status: {resp.status}")
        except Exception as e:
            print(f"Failed download: {e}")
            pass
            
        browser.close()
        return None

if __name__ == "__main__":
    doh_urls = ["https://www.doh.gov.ae/en/resources/reference-price-list", "https://www.doh.gov.ae/en/resources/Circulars"]
    dha_urls = ["https://www.dha.gov.ae/en/HealthRegulationSector/DrugControl"]
    
    print("Fetching DoH...")
    doh_data = _fetch_excel_data_sync(doh_urls)
    if doh_data:
        print(f"DoH success, bytes: {len(doh_data)}")
    else:
        print("DoH failed.")
        
    print("\nFetching DHA...")
    dha_data = _fetch_excel_data_sync(dha_urls)
    if dha_data:
        print(f"DHA success, bytes: {len(dha_data)}")
    else:
        print("DHA failed.")
