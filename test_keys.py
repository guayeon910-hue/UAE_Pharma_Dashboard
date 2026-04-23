import os
from dotenv import load_dotenv
load_dotenv('.env', override=True)

checks = {
    'SUPABASE_URL': bool(os.getenv('SUPABASE_URL')),
    'SUPABASE_KEY': bool(os.getenv('SUPABASE_KEY')),
    'CLAUDE_API_KEY': bool(os.getenv('CLAUDE_API_KEY') or os.getenv('ANTHROPIC_API_KEY')),
    'PERPLEXITY_API_KEY': bool(os.getenv('PERPLEXITY_API_KEY'))
}
print("Environment Key Status:")
for k, v in checks.items():
    print(f"{k}: {'OK' if v else 'MISSING'}")

try:
    from supabase import create_client
    sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    # verify connection by fetching 1 row
    r = sb.table("products").select("product_id").eq("country", "UAE").limit(1).execute()
    print("Supabase DB Connection: OK")
except Exception as e:
    print(f"Supabase DB Connection: FAILED ({e})")
