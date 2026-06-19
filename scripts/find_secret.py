# find_secret.py
import jwt

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1OWZhMzExMy1jNWIyLTRjMGUtOTMzMC1hMjllMWZmNDQ5MjgiLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6IkFETUlOIiwiaW5zdGl0dXRpb25faWQiOiJpbnNwZWt0b3JhdC0xIiwiZXhwIjoxNzgxMTMxNDE1LCJ0eXBlIjoiYWNjZXNzIn0.6Nzk89P5BRpLIbNT5nTXG8I32KnK6b7NwKnDotmFHaE"

# Daftar kemungkinan secret key
possible_secrets = [
    "nemesis-super-secret-key-change-in-production",  # dari auth.py
    "nemesis-madina-v8-secret-key-2024",
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
    "your-secret-key",
    "secret",
    "admin",
    "nemesis-madina",
]

print("🔍 Searching for correct SECRET_KEY...\n")

for secret in possible_secrets:
    try:
        payload = jwt.decode(
            TOKEN, 
            secret, 
            algorithms=["HS256"],
            options={"verify_exp": False}
        )
        print(f"✅ FOUND! SECRET_KEY = '{secret}'")
        print(f"   Payload: {payload}")
        break
    except jwt.InvalidSignatureError:
        print(f"   ❌ Invalid signature with: {secret[:20]}...")
    except Exception as e:
        print(f"   ❌ Error with {secret[:20]}...: {e}")
else:
    print("\n❌ No matching secret key found in list")
    print("\n💡 Alternative: Check .env file for JWT_SECRET or SECRET_KEY")