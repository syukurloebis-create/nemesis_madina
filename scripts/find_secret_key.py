# find_secret_key.py
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1OWZhMzExMy1jNWIyLTRjMGUtOTMzMC1hMjllMWZmNDQ5MjgiLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6IkFETUlOIiwiaW5zdGl0dXRpb25faWQiOiJpbnNwZWt0b3JhdC0xIiwiZXhwIjoxNzgxMTMxNDE1LCJ0eXBlIjoiYWNjZXNzIn0.6Nzk89P5BRpLIbNT5nTXG8I32KnK6b7NwKnDotmFHaE"

# Kumpulkan semua kemungkinan secret key dari berbagai sumber
possible_secrets = []

# 1. Dari environment variables
possible_secrets.append(os.getenv("SECRET_KEY"))
possible_secrets.append(os.getenv("JWT_SECRET_KEY"))
possible_secrets.append(os.getenv("JWT_SECRET"))

# 2. Dari file .env (baca langsung)
env_file = ".env"
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.startswith("SECRET_KEY=") or line.startswith("JWT_SECRET_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                possible_secrets.append(key)

# 3. Common defaults
possible_secrets.extend([
    "nemesis-super-secret-key-change-in-production",
    "nemesis-madina-v8-secret-key-2024",
    "nemesis-madina-secret-key",
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
    "your-super-secret-key-change-this",
    "secret",
    "admin123",
    "password",
    "nemesis",
    "madina",
])

# Filter None values
possible_secrets = [s for s in possible_secrets if s]

print("🔍 Searching for correct SECRET_KEY...\n")
print(f"Testing {len(possible_secrets)} possible keys\n")

found = False
for secret in possible_secrets:
    try:
        payload = jwt.decode(
            TOKEN, 
            secret, 
            algorithms=["HS256", "HS512"],
            options={"verify_exp": False}
        )
        print(f"\n✅✅✅ FOUND! SECRET_KEY = '{secret}'")
        print(f"   Payload: {payload}")
        found = True
        break
    except jwt.InvalidSignatureError:
        print(f"   ❌ Invalid signature: {secret[:30]}...")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:50]}...")

if not found:
    print("\n❌ No matching secret key found in list")
    print("\n💡 Manual decode attempt without verification:")
    print("   Token structure:")
    import base64
    parts = TOKEN.split('.')
    if len(parts) == 3:
        header = base64.urlsafe_b64decode(parts[0] + '==').decode()
        payload = base64.urlsafe_b64decode(parts[1] + '==').decode()
        print(f"   Header: {header}")
        print(f"   Payload: {payload}")