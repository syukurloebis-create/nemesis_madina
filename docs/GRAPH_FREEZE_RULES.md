# Graph Freeze Rules - NEMESIS

## Purpose
Prevent further architectural fragmentation during migration.

## Rules

### Rule 1: No New Classes Without Dependency Verification
**Status**: ENFORCED

**Description**: 
Tidak boleh membuat class baru di domain graph sebelum seluruh dependency terpetakan.

**Exception**: 
- Utility classes yang tidak berinteraksi dengan graph
- Test helpers

**Approval**: Architecture Team

---

### Rule 2: No File Deletion Without Import Verification
**Status**: ENFORCED

**Description**:
Tidak boleh menghapus file graph selama masih ada import yang menggunakannya.

**Verification**:
```bash
grep -r "from.*file_name" backend
grep -r "import.*file_name" backend