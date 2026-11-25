#!/bin/sh
# Exécute la chaîne complète, dans l'ordre, avec l'interpréteur indiqué par PYTHON (par défaut python3).
# Usage : PYTHON=scripts/lot3-quantites/cache/venv/bin/python sh scripts/lot3-quantites/executer.sh
set -e
ICI=$(cd "$(dirname "$0")" && pwd)
PY=${PYTHON:-python3}
export PYTHONHASHSEED=0   # ordre d'itération des ensembles de chaînes figé (précaution)
mkdir -p "$ICI/cache/log"
# Crec_reconstit.pkl est recréé à chaque exécution complète (voir s31_C_as_primary.py).
rm -f "$ICI/cache/Crec_reconstit.pkl"
for s in s00_load s03_B_ecarts s05_buildC s30_loadC s31_C_as_primary s06_recompo s10_cloture_note \
         m1_B07 c1_loadG m1_B02 m1_B04 m2_Bc1 c1_C2 m1_B09 r3_C5_brut r3_pieces_a r3_pieces_b; do
  echo "== $s"
  "$PY" "$ICI/$s.py" > "$ICI/cache/log/$s.txt" 2>&1 || { echo "échec : $s (voir cache/log/$s.txt)"; exit 1; }
done
echo "Pièces régénérées : $ICI/cache/pieces/"
