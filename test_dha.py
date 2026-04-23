import urllib.parse

def _test_download():
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = context.new_page()
        
        url = "https://www.dha.gov.ae/uploads/022022/PriceList en2022239251.xlsx"
        parsed = urllib.parse.urlparse(url)
        safe_path = urllib.parse.quote(parsed.path)
        safe_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, safe_path, parsed.params, parsed.query, parsed.fragment))
        
        print(f"Safe URL: {safe_url}")
        try:
            resp = context.request.get(safe_url, timeout=30000)
            print(resp.status)
            if resp.status == 200:
                body = resp.body()
                ct = resp.headers.get("content-type")
                print(f"Size: {len(body)}, Content-Type: {ct}")
        except Exception as e:
            print(f"Error: {e}")

        browser.close()

if __name__ == "__main__":
    _test_download()
