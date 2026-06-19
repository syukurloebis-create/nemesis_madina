#!/usr/bin/env python3
"""
Setup Runner - Menjalankan semua setup script secara berurutan
"""
import subprocess
import sys
import os

# Set working directory
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(WORK_DIR)

def run_script(script_name):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {script_name}")
    print('='*60)
    
    # Gunakan Python dari virtual environment
    python_exe = sys.executable
    script_path = os.path.join(WORK_DIR, script_name)
    
    # Set environment untuk import
    env = os.environ.copy()
    env['PYTHONPATH'] = WORK_DIR + os.pathsep + env.get('PYTHONPATH', '')
    
    result = subprocess.run(
        [python_exe, script_path],
        cwd=WORK_DIR,
        env=env
    )
    
    if result.returncode != 0:
        print(f"❌ ERROR: {script_name} failed with code {result.returncode}")
        return False
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 NEMESIS V8+ SETUP RUNNER")
    print("=" * 60)
    print(f"Python: {sys.executable}")
    print(f"Working dir: {os.getcwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    scripts = [
        "fix_hash_chain.py",
        "fix_auth.py",
        "seed_evidence.py",
        "create_snapshots.py"
    ]
    
    for script in scripts:
        if not run_script(script):
            print(f"\n❌ Setup FAILED at {script}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ ALL SETUP COMPLETE!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("  1. Test login: admin/admin123")
    print("  2. Test API: http://localhost:8000/cases/")
    print("  3. Start Phase 2: Evidence Intelligence")
    print("  4. Start Phase 3: Decision Provenance")