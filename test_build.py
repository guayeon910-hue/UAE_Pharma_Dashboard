import asyncio
from datetime import datetime
from report_generator import build_report

async def main():
    result = {
        "product_id": "sereterol-activair",
        "error": "알 수 없는 product_id: sereterol-activair",
        "analyzed_at": datetime.now().isoformat(),
    }
    try:
        report = build_report(
            [{"product_id": "sereterol-activair"}], 
            datetime.now().isoformat(), 
            [result], 
            {"sereterol-activair": []}
        )
        print("Success")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
