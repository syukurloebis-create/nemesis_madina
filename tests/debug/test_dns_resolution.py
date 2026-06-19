"""
Debug test untuk DNS resolution issues
Mengidentifikasi masalah network antara containers
"""

import subprocess
import json

def test_dns_resolution():
    """Test DNS resolution dari setiap container"""
    print("\n🔍 TEST: DNS Resolution Across Containers")
    print("=" * 60)
    
    containers = ['api1', 'api2', 'api3', 'nginx']
    targets = ['postgres', 'redis', 'nats', 'localhost']
    
    results = {}
    
    for container in containers:
        print(f"\n📦 Container: {container}")
        print("-" * 40)
        
        for target in targets:
            # Try multiple DNS resolution methods
            cmd_python = f"docker exec nemesis_madina-{container}-1 python -c \"import socket; print(socket.gethostbyname('{target}'))\" 2>/dev/null"
            result_py = subprocess.run(cmd_python, shell=True, capture_output=True, text=True)
            
            cmd_ping = f"docker exec nemesis_madina-{container}-1 ping -c 1 -W 1 {target} 2>/dev/null | head -1"
            result_ping = subprocess.run(cmd_ping, shell=True, capture_output=True, text=True)
            
            status = "✅" if result_py.returncode == 0 else "❌"
            ip = result_py.stdout.strip() if result_py.returncode == 0 else "unresolved"
            
            print(f"  {target}: {status} {ip}")
            
            # Store results for summary
            if container not in results:
                results[container] = {}
            results[container][target] = ip if result_py.returncode == 0 else None
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DNS RESOLUTION SUMMARY")
    print("=" * 60)
    
    all_success = True
    for container, targets in results.items():
        failed = [t for t, ip in targets.items() if ip is None]
        if failed:
            all_success = False
            print(f"❌ {container}: Cannot resolve {', '.join(failed)}")
    
    if all_success:
        print("✅ All containers can resolve all targets")
    
    return all_success

def test_network_latency():
    """Test network latency between containers"""
    print("\n🔍 TEST: Network Latency")
    print("=" * 60)
    
    containers = ['api1', 'api2', 'api3']
    
    for container in containers:
        cmd = f"""
docker exec nemesis_madina-{container}-1 python -c "
import time
import socket

def test_latency(host, port):
    try:
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((host, port))
        latency = (time.time() - start) * 1000
        sock.close()
        return latency
    except Exception as e:
        return None

services = [('postgres', 5432), ('redis', 6379), ('nats', 4222)]
for host, port in services:
    latency = test_latency(host, port)
    if latency:
        print(f'{host}:{port} = {latency:.2f}ms')
    else:
        print(f'{host}:{port} = FAILED')
" 2>/dev/null
"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"\n📦 {container}:")
        for line in result.stdout.strip().split('\n'):
            if line:
                print(f"   {line}")

if __name__ == "__main__":
    test_dns_resolution()
    test_network_latency()