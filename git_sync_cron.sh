#!/usr/bin/env bash
# Sincroniza hacia GitHub los archivos que actualiza el cron de
# analista-futbol (api_to_csv.py + analisis_ia_diario_completo.py).
# Sin esto, el contenedor efimero del Cron Job de Render descarga los
# datos y los tira al terminar -- nunca llegan al repo ni al servicio web.
#
# DRY_RUN=true : hace todo (stash/pull/add/commit) menos el push real.
#                Usar para probar en el cron de produccion sin riesgo.
set -euo pipefail

cd "$(dirname "$0")"

ARCHIVOS=(futbol_partidos.csv cache_team_ids.json ligas_auto_detectadas.json cuotas_cache.json)

git config user.name "Cron analista-futbol"
git config user.email "cron@analista-futbol.local"

# api_to_csv.py y analisis_ia_diario_completo.py ya corrieron antes que
# este script (encadenados en el Start Command) y dejaron estos archivos
# modificados en el working tree. Los guardamos aparte, nos aseguramos de
# estar sobre la punta real de main, y los volvemos a traer -- por si el
# checkout de este contenedor no arranco exactamente al dia con origin.
git stash push --include-untracked -- "${ARCHIVOS[@]}" || true
git pull --rebase origin main
git stash pop || true

git add "${ARCHIVOS[@]}"

if git diff --cached --quiet; then
  echo "Sin cambios para commitear."
  exit 0
fi

git commit -m "Actualizacion automatica del cron ($(date -u +%Y-%m-%dT%H:%M:%SZ))"

if [ "${DRY_RUN:-false}" = "true" ]; then
  echo "DRY_RUN activo -- NO se hace push. Esto es lo que se hubiera subido:"
  git show --stat HEAD
  exit 0
fi

git remote set-url origin "https://x-access-token:${GIT_PUSH_TOKEN}@github.com/Hoover182/analista-futbol.git"
git push origin main
