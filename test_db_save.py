import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def run_db_save_check():
    from utils.uae_doh_crawler import fetch_doh_prices, save_prices_to_supabase
    
    print("Fetching DoH data...")
    doh = await fetch_doh_prices()
    print(f"DoH prices retrieved: {len(doh)}")
    
    if doh:
        print("Saving all rows to Supabase to test schema...")
        result = await save_prices_to_supabase(doh)
        print(f"Save result: {result} rows upserted.")


def test_db_save():
    import pytest
    pytest.skip("Manual Supabase write check; run `python test_db_save.py` explicitly.")


if __name__ == "__main__":
    asyncio.run(run_db_save_check())
