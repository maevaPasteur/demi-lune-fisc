#!/bin/sh
# Exécute la chaîne complète, dans l'ordre, avec l'interpréteur indiqué par PYTHON (par défaut python3),
# puis les deux étapes LibreOffice (errata des pièces 38 et 85 à 88, recalcul des pièces 161 à 165).
# Usage : PYTHON=scripts/lot5-tva/cache/venv/bin/python sh scripts/lot5-tva/executer.sh
# SOFFICE (par défaut soffice) désigne l'exécutable LibreOffice.
set -e
ICI=$(cd "$(dirname "$0")" && pwd)
PY=${PYTHON:-python3}
SO=${SOFFICE:-soffice}
export PYTHONHASHSEED=0   # ordre d'itération des ensembles de chaînes figé (précaution)
mkdir -p "$ICI/cache/log"
for s in s00_charger s01_controle_sources s02_p26_origine s03_identite_vatbase s04_decalage_taux_C s05_validation_G \
         s06_tab56_57_articles s07_tva_ligne_a_ligne s08_erreurs_fiches_et_manipulation s08b_prix_caissier s09_pieces \
         s10_rapprochement s11_decomposition_B_C b1_classif b1_calculs b1_b11_format b1_b12_ordre b1_b17_menus \
         b1_b7_b8_b14 b1_b7_zero b2_reconstitution_reglements b3_source_reglement b3_c1_c3 b3_c6_c7 b3_c8_colonnes \
         c1_materialite b4_prep b4_piece1 b4_piece2 b4_piece3 b4_piece4 b4_piece5; do
  echo "== $s"
  "$PY" "$ICI/$s.py" > "$ICI/cache/log/$s.txt" 2>&1 || { echo "échec : $s (voir cache/log/$s.txt)"; exit 1; }
done
# Étapes LibreOffice : les deux modules sont copiés dans un profil LibreOffice propre à la chaîne (cache/lo-profil)
# et exécutés comme macros Python par l'interpréteur intégré à LibreOffice.
PROFIL="$ICI/cache/lo-profil"
mkdir -p "$PROFIL/user/Scripts/python"
cp "$ICI/b4_errata.py" "$ICI/b4_recalc.py" "$PROFIL/user/Scripts/python/"
export LOT5_ICI="$ICI"
for m in 'b4_errata.py$errata' 'b4_recalc.py$recalcule'; do
  echo "== LibreOffice : $m"
  "$SO" --headless --norestore --nologo "-env:UserInstallation=file://$PROFIL" \
        "vnd.sun.star.script:$m?language=Python&location=user" > "$ICI/cache/log/soffice.txt" 2>&1
done
for s in b4_errata_check; do
  echo "== $s"
  "$PY" "$ICI/$s.py" > "$ICI/cache/log/$s.txt" 2>&1 || { echo "échec : $s (voir cache/log/$s.txt)"; exit 1; }
done
echo "== b4_check"
"$PY" "$ICI/b4_check.py" "$ICI"/cache/out/b4/exp_16*.json > "$ICI/cache/log/b4_check.txt" 2>&1
echo "Pièces régénérées : $ICI/cache/pieces/ (161 à 165 recalculées : $ICI/cache/recalc/)"
