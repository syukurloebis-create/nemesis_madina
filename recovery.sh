#!/bin/bash
# Mount volume dan hapus file yang bermasalah
docker run --rm -v nemesis_madina_backend:/data alpine sh -c "
  rm -f /data/routers/cases_analysis.py
  rm -f /data/routers/intelligence.py
  cp /data/main.py.backup /data/main.py
  echo 'Recovery completed'
"
