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
        verdict = result.get("verdict")
        
        from analysis.perplexity_references import fetch_references
        refs = await fetch_references(product_key)
        
        from datetime import datetime, timezone as _tz
        from report_generator import build_report
        
        _refs_map = {product_key: refs}
        _report = build_report(
            kup_rows,
            datetime.now(_tz.utc).isoformat(),
            [result],
            references=_refs_map,
        )
        print("Success")
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
