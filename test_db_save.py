import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_db_save():
    from utils.uae_doh_crawler import fetch_doh_prices, save_prices_to_supabase
    
    print("Fetching DoH data...")
    doh = await fetch_doh_prices()
    print(f"DoH prices retrieved: {len(doh)}")
    
    if doh:
        print("Saving all rows to Supabase to test schema...")
        result = await save_prices_to_supabase(doh)
        print(f"Save result: {result} rows upserted.")

if __name__ == "__main__":
    asyncio.run(test_db_save())
