#!/bin/bash
# start_nemesis.sh - Menjalankan kembali NEMESIS dari image yang ada

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              NEMESIS CONTAINER RESTART                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================
# STOP DAN HAPUS CONTAINER LAMA (JIKA ADA)
# ============================================================
echo -e "${BLUE}[STEP 1]${NC} Membersihkan container lama..."

# Hentikan container dengan nama yang sama jika ada
docker stop nemesis_api 2>/dev/null
docker rm nemesis_api 2>/dev/null

echo -e "${GREEN}✅ Selesai${NC}"

# ============================================================
# BUAT VOLUME (UNTUK PERSISTENCE)
# ============================================================
echo ""
echo -e "${BLUE}[STEP 2]${NC} Membuat volume persistent..."

# Buat volume jika belum ada
docker volume create nemesis_data 2>/dev/null
docker volume create nemesis_evidence 2>/dev/null
docker volume create nemesis_logs 2>/dev/null

echo -e "${GREEN}✅ Volume siap:${NC}"
docker volume ls | grep nemesis

# ============================================================
# JALANKAN CONTAINER BARU
# ============================================================
echo ""
echo -e "${BLUE}[STEP 3]${NC} Menjalankan container..."

docker run -d \
    --name nemesis_api \
    --restart unless-stopped \
    -p 8000:8000 \
    -v nemesis_data:/app/data \
    -v nemesis_evidence:/app/evidence \
    -v nemesis_logs:/app/logs \
    nemesis_madina-nemesis-api:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container berhasil dijalankan${NC}"
else
    echo -e "${RED}❌ Gagal menjalankan container${NC}"
    exit 1
fi

# ============================================================
# TUNGGU CONTAINER SIAP
# ============================================================
echo ""
echo -e "${BLUE}[STEP 4]${NC} Menunggu container siap..."

sleep 5

# ============================================================
# CEK STATUS CONTAINER
# ============================================================
echo ""
echo -e "${BLUE}[STEP 5]${NC} Cek status..."

if docker ps | grep -q nemesis_api; then
    echo -e "${GREEN}✅ Container running${NC}"
    
    # Cek logs
    echo ""
    echo -e "${BLUE}📝 Logs terbaru:${NC}"
    docker logs nemesis_api --tail 10
else
    echo -e "${RED}❌ Container tidak running${NC}"
    echo ""
    echo "Logs error:"
    docker logs nemesis_api --tail 30
    exit 1
fi

# ============================================================
# TEST API
# ============================================================
echo ""
echo -e "${BLUE}[STEP 6]${NC} Testing API..."

# Tunggu sebentar
sleep 3

# Test endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/cases/ 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ API merespon (HTTP $HTTP_CODE)${NC}"
    
    # Coba create case
    echo ""
    echo -e "${BLUE}📝 Membuat case test...${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8000/cases/ \
        -H "Content-Type: application/json" \
        -d '{"title": "Test Case", "description": "Testing after recovery", "priority": "high"}')
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        echo -e "${GREEN}✅ Case berhasil dibuat!${NC}"
        CASE_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "   Case ID: $CASE_ID"
    else
        echo -e "${YELLOW}⚠️ Gagal membuat case${NC}"
        echo "   Response: $RESPONSE"
    fi
else
    echo -e "${RED}❌ API tidak merespon (HTTP $HTTP_CODE)${NC}"
fi

# ============================================================
# HASIL AKHIR
# ============================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              NEMESIS IS RUNNING!                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Container Info:"
echo "   • Nama: nemesis_api"
echo "   • Image: nemesis_madina-nemesis-api:latest"
echo "   • Port: http://localhost:8000"
echo ""
echo "📋 Perintah Berguna:"
echo "   • Lihat logs:   docker logs -f nemesis_api"
echo "   • Masuk container: docker exec -it nemesis_api bash"
echo "   • Hentikan:     docker stop nemesis_api"
echo "   • Start ulang:  docker start nemesis_api"
echo ""
echo "🔗 API Endpoints:"
echo "   • GET  /cases/              - List semua cases"
echo "   • POST /cases/              - Buat case baru"
echo "   • GET  /cases/{id}/summary  - Ringkasan case"
echo "   • GET  /cases/{id}/timeline - Timeline case"
echo "   • GET  /cases/{id}/lineage  - Lineage dengan hash chain"
echo ""
echo "💾 Volume Persistence:"
echo "   • Data:    nemesis_data"
echo "   • Evidence: nemesis_evidence"
echo "   • Logs:    nemesis_logs"
echo ""
echo "⚠️  Catatan: Data case LAMA sudah hilang karena sebelumnya tidak pakai volume"
echo "   Tapi mulai sekarang data akan tersimpan di volume!"
echo ""