import asyncio

def _find_links(urls: list[str]):
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = context.new_page()
        
        for url in urls:
            print(f"\n--- Checking {url} ---")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                
                links = page.query_selector_all("a[href]")
                for link in links:
                    href = link.get_attribute("href")
                    text = link.inner_text().strip().replace('\n', ' ')
                    if href and any(ext in href.lower() for ext in [".xlsx", ".xls", ".ashx", "price"]):
                        print(f"Text: {text} | Href: {href}")
            except Exception as e:
                print(f"Error: {e}")

        browser.close()

if __name__ == "__main__":
    _find_links([
        "https://www.doh.gov.ae/en/resources/reference-price-list",
        "https://www.doh.gov.ae/en/resources/Circulars",
        "https://www.dha.gov.ae/en/HealthRegulationSector/DrugControl"
    ])
