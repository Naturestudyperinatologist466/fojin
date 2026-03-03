#!/bin/bash
# =============================================================
# 佛津 (FoJin) — CBETA Full Import Orchestration
# =============================================================
# This script orchestrates the complete CBETA data import:
#   1. Import complete catalog (4,868+ texts)
#   2. Import content for all collections
#   3. Backfill identifiers
#   4. Import alternative translations
#   5. Seed knowledge graph
#
# Usage:
#   cd backend
#   bash scripts/import_cbeta_full.sh
#   bash scripts/import_cbeta_full.sh --resume    # Resume from checkpoint
# =============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

PYTHON="${BACKEND_DIR}/.venv/bin/python"
if [ ! -f "$PYTHON" ]; then
    PYTHON="python"
fi

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
    RESUME_FLAG="--resume"
fi

echo "============================================================="
echo "佛津 (FoJin) — CBETA Full Import"
echo "============================================================="
echo "Python: $PYTHON"
echo "Backend: $BACKEND_DIR"
echo ""

# Step 1: Catalog
echo ""
echo "===== [1/5] Importing CBETA catalog... ====="
$PYTHON scripts/import_catalog.py

# Step 2: Content (all collections)
echo ""
echo "===== [2/5] Importing CBETA content (all collections)... ====="
$PYTHON scripts/import_content.py --all --xml-dir data/xml-p5 $RESUME_FLAG

# Step 3: Backfill identifiers
echo ""
echo "===== [3/5] Backfilling CBETA identifiers... ====="
if [ -f scripts/backfill_cbeta_identifiers.py ]; then
    $PYTHON scripts/backfill_cbeta_identifiers.py
else
    echo "  Skipped (script not found)"
fi

# Step 4: Alternative translations
echo ""
echo "===== [4/5] Importing CBETA alternative translations... ====="
if [ -f scripts/import_cbeta_alt_translations.py ]; then
    $PYTHON scripts/import_cbeta_alt_translations.py
else
    echo "  Skipped (script not found)"
fi

# Step 5: Knowledge graph
echo ""
echo "===== [5/5] Extracting structured knowledge graph... ====="
$PYTHON scripts/extract_structured_kg.py

echo ""
echo "============================================================="
echo "CBETA Full Import Complete!"
echo "============================================================="

# Show stats
echo ""
$PYTHON scripts/import_stats.py
