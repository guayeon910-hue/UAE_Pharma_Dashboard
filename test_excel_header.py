import sys

def inspect_excel():
    from playwright.sync_api import sync_playwright
    import io
    import openpyxl
    
    url = "https://www.doh.gov.ae/-/media/Feature/shafifya/Prices/Drugs.ashx"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0")
        try:
            resp = context.request.get(url, timeout=30000)
            if resp.status == 200:
                body = resp.body()
                print(f"Downloaded {len(body)} bytes.")
                wb = openpyxl.load_workbook(io.BytesIO(body), read_only=True, data_only=True)
                ws = wb.active
                for i, row in enumerate(ws.iter_rows(values_only=True)):
                    print(f"Row {i}: {row}")
                    if i > 10:
                        break
        except Exception as e:
            print(e)
        browser.close()

if __name__ == "__main__":
    inspect_excel()
