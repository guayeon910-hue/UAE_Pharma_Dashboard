import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_crawler():
    from utils.uae_doh_crawler import fetch_doh_prices, fetch_dha_prices
    
    print("Testing DoH...")
    doh = await fetch_doh_prices()
    print(f"DoH prices retrieved: {len(doh)}")
    if doh:
        print(f"Sample DoH: {doh[0]}")
        
    print("\nTesting DHA...")
    dha = await fetch_dha_prices()
    print(f"DHA prices retrieved: {len(dha)}")
    if dha:
        print(f"Sample DHA: {dha[0]}")

if __name__ == "__main__":
    asyncio.run(test_crawler())
