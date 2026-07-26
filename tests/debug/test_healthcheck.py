"""
Debug test untuk healthcheck issues
Mengetahui mengapa docker ps menunjukkan unhealthy meskipun API berfungsi
"""

import subprocess
import requests
import json
import sys

def test_docker_health_status():
    """Test 1: Cek status healthcheck dari Docker"""
    print("\n🔍 TEST 1: Docker Healthcheck Status")
    print("=" * 50)
    
    containers = ['api1', 'api2', 'api3']
    for container in containers:
        cmd = f"docker inspect nemesis_madina-{container}-1 --format='{{{{.State.Health.Status}}}}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        status = result.stdout.strip()
        
        cmd_curl = f"docker exec nemesis_madina-{container}-1 which curl 2>/dev/null || echo 'not found'"
        has_curl = subprocess.run(cmd_curl, shell=True, capture_output=True, text=True).stdout.strip()
        
        cmd_wget = f"docker exec nemesis_madina-{container}-1 which wget 2>/dev/null || echo 'not found'"
        has_wget = subprocess.run(cmd_wget, shell=True, capture_output=True, text=True).stdout.strip()
        
        print(f"📦 Container {container}:")
        print(f"   Health Status: {status}")
        print(f"   curl available: {'✅' if has_curl != 'not found' else '❌'}")
        print(f"   wget available: {'✅' if has_wget != 'not found' else '❌'}")
        print()

def test_health_endpoint():
    """Test 2: Cek health endpoint via localhost (inside container)"""
    print("\n🔍 TEST 2: Health Endpoint Inside Container")
    print("=" * 50)
    
    containers = ['api1', 'api2', 'api3']
    for container in containers:
        cmd = f"docker exec nemesis_madina-{container}-1 python -c \"import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())\" 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                print(f"✅ {container}: {data.get('status', 'unknown')}")
            except:
                print(f"⚠️ {container}: Could not parse response")
        else:
            print(f"❌ {container}: Failed to connect - {result.stderr[:100]}")

def test_db_connection():
    """Test 3: Database connection dari API container"""
    print("\n🔍 TEST 3: Database Connection Inside Container")
    print("=" * 50)
    
    # Fix: Define script as a multi-line string properly
    script = """
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    engine = create_async_engine('postgresql+asyncpg://nemesis:nemesis123@postgres:5432/nemesis_db')
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT 1 as test'))
        return result.first()[0]
    await engine.dispose()

print(asyncio.run(test()))
"""
    
    containers = ['api1', 'api2', 'api3']
    for container in containers:
        # Fix: Use proper escaping for the script
        cmd = f"docker exec nemesis_madina-{container}-1 python -c {repr(script)} 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip() == '1':
            print(f"✅ {container}: Database connection SUCCESS")
        else:
            print(f"❌ {container}: Database connection FAILED - {result.stderr[:100]}")

if __name__ == "__main__":
    test_docker_health_status()
    test_health_endpoint()
    test_db_connection()