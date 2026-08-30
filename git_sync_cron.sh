#!/usr/bin/env bash
# Sincroniza hacia GitHub los archivos que actualiza el cron de
# analista-futbol (api_to_csv.py + analisis_ia_diario_completo.py).
# Sin esto, el contenedor efimero del Cron Job de Render descarga los
# datos y los tira al terminar -- nunca llegan al repo ni al servicio web.
#
# DRY_RUN=true : hace todo (add/commit/rebase) menos el push real.
#                Usar para probar en el cron de produccion sin riesgo.
set -euo pipefail

cd "$(dirname "$0")"

# El contenedor donde corre el Cron Job no trae configurado un remoto
# "origin" como lo haria un "git clone" normal (probablemente Render lo
# saca del checkout de ejecucion por seguridad). Sin esto, cualquier uso
# de "origin" mas abajo (fetch, rebase, push) revienta con "'origin' does
# not appear to be a git repository" -- confirmado en la corrida real de
# hoy, la falla era en el primer "git fetch origin main", no en el push.
REPO_URL="https://x-access-token:${GIT_PUSH_TOKEN}@github.com/Hoover182/analista-futbol.git"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

git config user.name "Cron analista-futbol"
git config user.email "cron@analista-futbol.local"

# "git add -u" (no "-A"/"."): stagea SOLO cambios a archivos ya
# trackeados, nunca agrega archivos nuevos/sin trackear -- evita el
# riesgo de comitear algo inesperado, pero sin necesitar una lista
# hardcodeada de nombres de archivo. Se cambio de una lista fija de 4
# archivos a esto porque dos corridas reales seguidas encontraron un
# archivo trackeado modificado que la lista no contemplaba, ensuciando
# el arbol antes del rebase (mismo sintoma las dos veces: "cannot
# rebase: You have unstaged changes"). Con -u, cualquier archivo ya
# trackeado que estos scripts (o algo del contenedor) modifiquen queda
# comiteado, sin adivinar nombres de antemano.
git add -u

if git diff --cached --quiet; then
  echo "Sin cambios para commitear."
  exit 0
fi

git commit -m "Actualizacion automatica del cron ($(date -u +%Y-%m-%dT%H:%M:%SZ))"

# El commit ya existe (arbol de trabajo limpio de aca en mas), asi que
# no hace falta stash para traer cambios remotos -- rebase opera sobre
# commits, no sobre archivos sin commitear. Esto evita depender de que
# un "git stash" haya funcionado antes de un "pull --rebase" (la causa
# real de la falla anterior: el stash fallaba en silencio por el "|| true"
# y el pull --rebase se encontraba el arbol sucio).
git fetch origin main
git rebase origin/main

if [ "${DRY_RUN:-false}" = "true" ]; then
  echo "DRY_RUN activo -- NO se hace push. Esto es lo que se hubiera subido:"
  git show --stat HEAD
  exit 0
fi

git push origin HEAD:main
