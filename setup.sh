#!/usr/bin/env bash
# WEP — скрипт установки для Linux
# Запускать из корня репозитория после клонирования:
#   bash setup.sh

set -euo pipefail

# ── Цвета ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[•]${RESET} $*"; }
ok()      { echo -e "${GREEN}[✓]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[!]${RESET} $*"; }
err()     { echo -e "${RED}[✗]${RESET} $*" >&2; }
die()     { err "$*"; exit 1; }
section() { echo -e "\n${BOLD}${CYAN}──── $* ────${RESET}"; }

# ── Утилиты ──────────────────────────────────────────────────────────────────
ask() {
  local prompt="$1" default="${2:-}" var
  if [[ -n "$default" ]]; then
    read -rp "$(echo -e "${YELLOW}?${RESET} $prompt [${default}]: ")" var
    echo "${var:-$default}"
  else
    read -rp "$(echo -e "${YELLOW}?${RESET} $prompt: ")" var
    echo "$var"
  fi
}

ask_secret() {
  local prompt="$1" var
  read -rsp "$(echo -e "${YELLOW}?${RESET} $prompt: ")" var; echo
  echo "$var"
}

ask_yn() {
  local prompt="$1" default="${2:-y}"
  local yn; read -rp "$(echo -e "${YELLOW}?${RESET} $prompt [${default}]: ")" yn
  [[ "${yn:-$default}" =~ ^[Yy]$ ]]
}

gen_secret() { python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null \
               || openssl rand -hex 32; }

# ── Проверка что запускаем из корня проекта ───────────────────────────────────
[[ -f "deploy/docker-compose.prod.yml" ]] \
  || die "Запустите скрипт из корня репозитория wep"

REPO_ROOT="$(pwd)"

# ─────────────────────────────────────────────────────────────────────────────
section "Проверка зависимостей"
# ─────────────────────────────────────────────────────────────────────────────

install_pkg() {
  info "Устанавливаю $1..."
  sudo apt-get install -y "$1" -qq
}

if ! command -v docker &>/dev/null; then
  warn "Docker не найден — устанавливаю..."
  sudo apt-get update -qq
  sudo apt-get install -y ca-certificates curl gnupg -qq
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update -qq
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin -qq
  sudo systemctl enable docker --now
  ok "Docker установлен"
else
  ok "Docker $(docker --version | grep -oP '\d+\.\d+\.\d+')"
fi

if ! docker compose version &>/dev/null; then
  warn "docker compose plugin не найден — устанавливаю..."
  sudo apt-get install -y docker-compose-plugin -qq
fi
ok "docker compose $(docker compose version --short)"

command -v openssl &>/dev/null || install_pkg openssl
command -v python3 &>/dev/null || install_pkg python3

# ─────────────────────────────────────────────────────────────────────────────
section "Конфигурация"
# ─────────────────────────────────────────────────────────────────────────────

echo
DOMAIN=$(ask "Домен сервера (например: wep.example.com)")
[[ -n "$DOMAIN" ]] || die "Домен не может быть пустым"

USE_SSL=false
if ask_yn "Получить SSL-сертификат через Let's Encrypt?"; then
  USE_SSL=true
fi

echo
PG_PASSWORD=$(ask_secret "Пароль PostgreSQL")
[[ -n "$PG_PASSWORD" ]] || die "Пароль не может быть пустым"

MINIO_PASSWORD=$(ask_secret "Пароль MinIO")
[[ -n "$MINIO_PASSWORD" ]] || die "Пароль не может быть пустым"

SECRET_KEY=$(gen_secret)
ok "SECRET_KEY сгенерирован"

# ─────────────────────────────────────────────────────────────────────────────
section "SSL-сертификат"
# ─────────────────────────────────────────────────────────────────────────────

if $USE_SSL; then
  if ! command -v certbot &>/dev/null; then
    info "Устанавливаю certbot..."
    sudo apt-get install -y certbot -qq
  fi
  # Порт 80 должен быть свободен
  if ss -tlnp | grep -q ':80 '; then
    warn "Порт 80 занят — остановите занимающий его процесс и запустите скрипт снова"
    warn "Или получите сертификат вручную: certbot certonly --standalone -d ${DOMAIN}"
    USE_SSL=false
  else
    info "Получаю сертификат для ${DOMAIN}..."
    sudo certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos \
      --register-unsafely-without-email
    ok "Сертификат получен: /etc/letsencrypt/live/${DOMAIN}/"
  fi
fi

if ! $USE_SSL; then
  warn "SSL не настроен. Приложение будет доступно по HTTP."
  warn "Для включения SSL: sudo certbot certonly --standalone -d ${DOMAIN}"
  warn "Затем обновите frontend/nginx-prod.conf и пересоберите: docker compose -f deploy/docker-compose.prod.yml up -d --build frontend"
fi

# ─────────────────────────────────────────────────────────────────────────────
section "Настройка конфигурационных файлов"
# ─────────────────────────────────────────────────────────────────────────────

PROTOCOL="https"; $USE_SSL || PROTOCOL="http"

# deploy/.env
cat > "${REPO_ROOT}/deploy/.env" <<EOF
POSTGRES_USER=wep
POSTGRES_PASSWORD=${PG_PASSWORD}
POSTGRES_DB=wep_db

SECRET_KEY=${SECRET_KEY}

MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=${MINIO_PASSWORD}
MINIO_BUCKET=wep-media
MINIO_PUBLIC_URL=${PROTOCOL}://${DOMAIN}/media

BACKEND_CORS_ORIGINS=["${PROTOCOL}://${DOMAIN}"]
EOF
ok "deploy/.env создан"

# frontend/.env (VITE_API_URL пустой — nginx проксирует /api/)
cat > "${REPO_ROOT}/frontend/.env" <<EOF
VITE_API_URL=
VITE_APP_TITLE=WEP
EOF
ok "frontend/.env создан"

# nginx-prod.conf: заменить your-domain на реальный
NGINX_CONF="${REPO_ROOT}/frontend/nginx-prod.conf"
if grep -q "your-domain" "$NGINX_CONF"; then
  sed -i "s/your-domain/$DOMAIN/g" "$NGINX_CONF"
  ok "nginx-prod.conf: домен обновлён на ${DOMAIN}"
fi

# Если SSL не настроен — переключить nginx на plain HTTP
if ! $USE_SSL; then
  cat > "$NGINX_CONF" <<NGINX
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://backend:8023/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    location /media/ {
        proxy_pass http://minio:9000/;
        proxy_set_header Host \$host;
        proxy_buffering off;
    }
}
NGINX
  ok "nginx-prod.conf: переключён на HTTP (без SSL)"
fi

# ─────────────────────────────────────────────────────────────────────────────
section "Сборка и запуск контейнеров"
# ─────────────────────────────────────────────────────────────────────────────

cd "${REPO_ROOT}/deploy"

info "Собираю образы и запускаю сервисы..."
docker compose -f docker-compose.prod.yml up -d --build

ok "Контейнеры запущены"

# ─────────────────────────────────────────────────────────────────────────────
section "Миграции базы данных"
# ─────────────────────────────────────────────────────────────────────────────

info "Жду готовности backend..."
RETRIES=20
until docker compose -f docker-compose.prod.yml exec -T backend \
      wget -qO- http://localhost:8023/api/v1/health &>/dev/null; do
  RETRIES=$((RETRIES - 1))
  [[ $RETRIES -gt 0 ]] || die "Backend не поднялся за отведённое время"
  sleep 5
done
ok "Backend готов"

info "Применяю миграции..."
docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head
ok "Миграции применены"

# ─────────────────────────────────────────────────────────────────────────────
section "Готово"
# ─────────────────────────────────────────────────────────────────────────────

echo
echo -e "${GREEN}${BOLD}Приложение запущено!${RESET}"
echo -e "  URL:         ${BOLD}${PROTOCOL}://${DOMAIN}${RESET}"
echo -e "  API docs:    ${BOLD}${PROTOCOL}://${DOMAIN}/api/docs${RESET}"
echo
echo -e "${CYAN}Полезные команды:${RESET}"
echo -e "  Статус:      docker compose -f deploy/docker-compose.prod.yml ps"
echo -e "  Логи:        docker compose -f deploy/docker-compose.prod.yml logs -f"
echo -e "  Остановить:  docker compose -f deploy/docker-compose.prod.yml down"
echo -e "  Обновить:    git pull && bash setup.sh"
echo
