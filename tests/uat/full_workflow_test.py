# tests/uat/full_workflow_test.py
import asyncio
import httpx
import json

async def test_full_investigation_workflow():
    """Complete UAT test for investigation workflow"""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. Login
        resp = await client.post(f"{base_url}/auth/login", json={
            "username": "admin",
            "password": "Admin123!"
        })
        assert resp.status_code == 200
        token = resp.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create Case
        resp = await client.post(f"{base_url}/cases/", headers=headers, json={
            "title": "UAT Test - Fraud Investigation",
            "description": "Testing complete workflow"
        })
        assert resp.status_code == 200
        case_id = resp.json()['id']
        print(f"✅ Case created: {case_id}")
        
        # 3. Upload Evidence
        files = {"file": ("evidence.txt", b"Test evidence content")}
        resp = await client.post(f"{base_url}/evidence/upload", headers=headers, files=files, data={"case_id": case_id})
        assert resp.status_code == 200
        evidence_id = resp.json()['id']
        print(f"✅ Evidence uploaded: {evidence_id}")
        
        # 4. Record Custody Transfer
        resp = await client.post(f"{base_url}/custody/{evidence_id}/transfer", headers=headers, json={
            "from_custodian": "admin",
            "to_custodian": "investigator",
            "reason": "Handover for analysis"
        })
        assert resp.status_code == 200
        print(f"✅ Custody transfer recorded")
        
        # 5. Verify Integrity
        resp = await client.get(f"{base_url}/integrity/verify/{case_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()['status'] == 'PASS'
        print(f"✅ Integrity verified")
        
        # 6. Export Evidence Package
        resp = await client.post(f"{base_url}/export/case/{case_id}", headers=headers)
        assert resp.status_code == 200
        print(f"✅ Evidence package exported")
        
        print("\n🎉 UAT Test PASSED!")
        return True

if __name__ == "__main__":
    asyncio.run(test_full_investigation_workflow())