import asyncio
import traceback

async def main():
    try:
        from utils.db import fetch_kup_products
        kup_rows = fetch_kup_products("UAE")
        product_key = "UAE_sereterol_activair"
        db_row = next((r for r in kup_rows if r.get("product_id") == product_key), None)
        
        from analysis.uae_export_analyzer import analyze_product
        result = await analyze_product(product_key, db_row)
        print("Verdict:", result.get("verdict"))
        print("Rationale:", result.get("rationale"))
        
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
