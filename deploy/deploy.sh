#!/usr/bin/env bash

# Guard against Windows carriage returns breaking execution on remote hosts.
if grep -q $'\r' "$0" 2>/dev/null; then
  printf '%s\n' "Error: deploy.sh contains Windows-style line endings (CRLF)." >&2
  printf '%s\n' "Run 'dos2unix deploy.sh' or re-checkout the repository with Unix line endings." >&2
  exit 1
fi

if [[ -n "${BASH_VERSION:-}" ]]; then
  set -Eeuo pipefail 2>/dev/null || set -Eeuo
else
  echo "This script must be run with bash." >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
PROD_COMPOSE_FILE="$ROOT_DIR/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/.env"
LOG_DIR="${DEPLOY_LOG_DIR:-$ROOT_DIR/deploy/logs}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/deploy_${TIMESTAMP}.log"
RELATIVE_LOG_PATH="${LOG_FILE#$ROOT_DIR/}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required to deploy this application." >&2
  exit 1
fi

if command -v docker compose >/dev/null 2>&1; then
  DOCKER_COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  DOCKER_COMPOSE=(docker-compose)
else
  echo "Docker Compose v2 (docker compose) or v1 (docker-compose) is required." >&2
  exit 1
fi

if [[ ! -f "$DEFAULT_COMPOSE_FILE" ]]; then
  echo "docker-compose.yml was not found in $ROOT_DIR." >&2
  exit 1
fi

COMPOSE_FILES=("$DEFAULT_COMPOSE_FILE")

if ! mkdir -p "$LOG_DIR" 2>/dev/null; then
  echo "Unable to create log directory at $LOG_DIR." >&2
  exit 1
fi

if [[ ! -w "$LOG_DIR" ]]; then
  echo "Log directory $LOG_DIR is not writable." >&2
  exit 1
fi

if ! command -v tee >/dev/null 2>&1; then
  echo "The 'tee' command is required but was not found in PATH." >&2
  exit 1
fi

if [[ -L "$ENV_FILE" ]]; then
  env_dir="$(cd "$(dirname "$ENV_FILE")" && pwd)"
  link_target="$(readlink "$ENV_FILE")"

  if [[ -z "$link_target" ]]; then
    echo "Deployment aborted: $ENV_FILE is a symbolic link without a target. Replace it with a regular file containing the deployment secrets." >&2
    exit 1
  fi

  if [[ "$link_target" != /* ]]; then
    link_target="$env_dir/$link_target"
  fi

  if [[ ! -f "$link_target" ]]; then
    echo "Deployment aborted: $ENV_FILE points to $link_target, which does not exist or is not a regular file." >&2
    exit 1
  fi

  temp_env_file="$(mktemp "$ENV_FILE.tmp.XXXXXX")"
  cp "$link_target" "$temp_env_file"
  rm "$ENV_FILE"
  mv "$temp_env_file" "$ENV_FILE"
  echo "Replaced symbolic link $ENV_FILE with a regular copy of $link_target." >&2
fi

if [[ ! -e "$ENV_FILE" ]]; then
  echo "Deployment aborted: $ENV_FILE was not found. Populate it with production secrets and retry." >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Deployment aborted: $ENV_FILE is missing or does not resolve to a readable file containing the deployment secrets." >&2
  exit 1
fi

chmod 600 "$ENV_FILE" 2>/dev/null || true

required_env_vars=(
  DB_ROOT_PASSWORD
  DB_NAME
  DB_USER
  DB_PASSWORD
)

for var in "${required_env_vars[@]}"; do
  if ! grep -Eq "^[[:space:]]*${var}=[[:space:]]*[^[:space:]#]" "$ENV_FILE"; then
    echo "The variable $var is missing or empty in $ENV_FILE." >&2
    exit 1
  fi
done

exec > >(tee -a "$LOG_FILE") 2>&1

handle_exit() {
  local exit_code=$?
  if (( exit_code == 0 )); then
    printf '\n[%(%Y-%m-%d %H:%M:%S)T] Deployment log saved to %s\n' -1 "$RELATIVE_LOG_PATH"
  else
    printf '\n[%(%Y-%m-%d %H:%M:%S)T] Deployment failed with exit code %s. Review %s for details.\n' -1 "$exit_code" "$RELATIVE_LOG_PATH" >&2
  fi
}

trap 'handle_exit' EXIT

log() {
  printf '\n[%(%Y-%m-%d %H:%M:%S)T] %s\n' -1 "$1"
}

compose() {
  local args=()
  for file in "${COMPOSE_FILES[@]}"; do
    args+=(-f "$file")
  done
  "${DOCKER_COMPOSE[@]}" --env-file "$ENV_FILE" "${args[@]}" "$@"
}

cd "$ROOT_DIR"

ENVIRONMENT_VALUE=""
if grep -Eq "^[[:space:]]*ENVIRONMENT[[:space:]]*=" "$ENV_FILE"; then
  raw_environment="$(grep -E "^[[:space:]]*ENVIRONMENT[[:space:]]*=" "$ENV_FILE" | tail -n1 | cut -d '=' -f2-)"
  raw_environment="${raw_environment%%#*}"
  raw_environment="${raw_environment//\"/}"
  ENVIRONMENT_VALUE="$(printf '%s' "$raw_environment" | xargs | tr '[:lower:]' '[:upper:]')"
fi

read_env_value() {
  local key="$1"
  local value=""

  if grep -Eq "^[[:space:]]*${key}[[:space:]]*=" "$ENV_FILE"; then
    value="$(grep -E "^[[:space:]]*${key}[[:space:]]*=" "$ENV_FILE" | tail -n1 | cut -d '=' -f2-)"
    value="${value%%#*}"
    value="${value//\"/}"
    value="$(printf '%s' "$value" | xargs)"
  fi

  printf '%s' "$value"
}

port_check_tool=""
if command -v ss >/dev/null 2>&1; then
  port_check_tool="ss"
elif command -v netstat >/dev/null 2>&1; then
  port_check_tool="netstat"
fi

port_in_use() {
  local port="$1"

  case "$port_check_tool" in
    ss)
      ss -H -tnlp 2>/dev/null | awk '{print $4}' | grep -Eq "(^|[:.])${port}$"
      return
      ;;
    netstat)
      netstat -tln 2>/dev/null | awk '{print $4}' | grep -Eq "(^|[:.])${port}$"
      return
      ;;
    *)
      return 1
      ;;
  esac
}

CURRENT_ENV="DEV"
case "$ENVIRONMENT_VALUE" in
  PROD)
    if [[ -f "$PROD_COMPOSE_FILE" ]]; then
      COMPOSE_FILES+=("$PROD_COMPOSE_FILE")
      CURRENT_ENV="PROD"
    else
      echo "Production compose override $PROD_COMPOSE_FILE not found." >&2
      exit 1
    fi
    ;;
  ""|DEV)
    CURRENT_ENV="DEV"
    ;;
  *)
    log "Environment value '$ENVIRONMENT_VALUE' is not recognised; defaulting to development compose settings."
    CURRENT_ENV="DEV (fallback)"
    ;;
esac

# CRITICAL FIX: Stop existing containers BEFORE checking ports
if [[ "$CURRENT_ENV" == "PROD" ]]; then
  log "Stopping existing containers to free up ports"

  # Try to stop containers gracefully (ignore errors if none exist)
  if compose ps -q 2>/dev/null | grep -q .; then
    compose down 2>/dev/null || true
  fi

  # Give containers time to release ports
  sleep 2
fi

# NOW check for port conflicts (should only catch non-Docker services)
if [[ "$CURRENT_ENV" == "PROD" && -n "$port_check_tool" ]]; then
  http_port="$(read_env_value CADDY_HTTP_PORT)"
  https_port="$(read_env_value CADDY_HTTPS_PORT)"
  http_port="${http_port:-80}"
  https_port="${https_port:-443}"

  blocked_ports=()
  declare -A port_descriptions=(
    ["$http_port"]="HTTP"
    ["$https_port"]="HTTPS"
  )

  for port in "$http_port" "$https_port"; do
    if [[ -z "$port" || ! "$port" =~ ^[0-9]+$ ]]; then
      continue
    fi

    if port_in_use "$port"; then
      blocked_ports+=("$port (${port_descriptions[$port]})")
    fi
  done

  if (( ${#blocked_ports[@]} > 0 )); then
    log "The following port(s) required by Caddy are still in use after stopping containers: ${blocked_ports[*]}"
    echo "A conflicting system service may be running. Stop it manually:" >&2
    echo "  sudo systemctl stop nginx && sudo systemctl disable nginx" >&2
    echo "  sudo systemctl stop apache2 && sudo systemctl disable apache2" >&2
    echo "Or set CADDY_HTTP_PORT/CADDY_HTTPS_PORT to unused host ports." >&2
    exit 1
  fi
elif [[ "$CURRENT_ENV" == "PROD" && -z "$port_check_tool" ]]; then
  log "Skipping host port availability check because neither 'ss' nor 'netstat' is installed."
fi

log "Writing deployment output to ${RELATIVE_LOG_PATH}"
log "Environment: $CURRENT_ENV"
compose_display=()
for file in "${COMPOSE_FILES[@]}"; do
  compose_display+=("${file#$ROOT_DIR/}")
done
log "Using compose file(s): ${compose_display[*]}"
log "Ensuring images are up to date"
compose pull --ignore-pull-failures || true

log "Deploying updated stack"

# CRITICAL FIX: Force rebuild frontend without cache in production
# This ensures that file changes (like UnderDevelopment.jsx) are picked up
if [[ "$CURRENT_ENV" == "PROD" ]]; then
  log "Forcing fresh rebuild of frontend to pick up source code changes"
  compose build --no-cache frontend
fi

compose up -d --build --remove-orphans

log "Waiting for backend container to be ready"
# Wait up to 30 seconds for backend container to be healthy
max_wait=30
elapsed=0
while (( elapsed < max_wait )); do
  if compose ps backend 2>/dev/null | grep -q "Up\|healthy"; then
    log "Backend container is ready"
    break
  fi
  sleep 2
  elapsed=$((elapsed + 2))
done

if (( elapsed >= max_wait )); then
  log "Warning: Backend container may not be ready yet, but proceeding with migration attempt"
fi

log "Checking Alembic version table"
check_output="$(compose exec -T backend bash -c "python - <<'PY'\nimport os\nimport pymysql\n\nhost = os.getenv('DB_HOST', 'db')\nport = int(os.getenv('DB_PORT', '3306'))\nuser = os.getenv('DB_USER', 'user')\npassword = os.getenv('DB_PASSWORD', 'password')\ndb_name = os.getenv('DB_NAME', 'app_db')\n\nconn = pymysql.connect(host=host, port=port, user=user, password=password, database=db_name)\ntry:\n    with conn.cursor() as cursor:\n        cursor.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s AND table_name='alembic_version'\", (db_name,))\n        alembic_exists = cursor.fetchone()[0] > 0\n        cursor.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s\", (db_name,))\n        table_count = cursor.fetchone()[0]\nfinally:\n    conn.close()\n\nprint(f\"alembic_version_exists={int(alembic_exists)}\")\nprint(f\"table_count={table_count}\")\nPY" 2>&1)"
check_status=$?
printf '%s\n' "$check_output" | tee -a "$LOG_FILE"
if [[ $check_status -ne 0 ]]; then
  log "WARNING: Unable to verify alembic_version table; proceeding with migration attempt"
else
  if printf '%s\n' "$check_output" | grep -q "alembic_version_exists=0"; then
    table_count="$(printf '%s\n' "$check_output" | awk -F= '/table_count=/{print $2}' | tail -n1)"
    if [[ -n "$table_count" && "$table_count" != "0" ]]; then
      log "Missing alembic_version table on existing DB; stamping baseline"
      if ! compose exec -T backend bash -c "cd /backend/app && python -m alembic stamp 0001_initial"; then
        log "ERROR: Failed to stamp database baseline"
        exit 1
      fi
    fi
  fi
fi

log "Running database migrations"
if compose exec -T backend bash -c "cd /backend/app && python -m alembic upgrade head" 2>&1 | tee -a "$LOG_FILE"; then
  log "Database migrations completed successfully"
else
  migration_exit_code=$?
  log "ERROR: Database migration failed with exit code $migration_exit_code"
  log "Aborting deployment to avoid running with a stale schema"
  log "You can retry after fixing the issue by running: docker exec app-backend bash -c 'cd /backend/app && python -m alembic upgrade head'"
  exit "$migration_exit_code"
fi

log "Pruning unused Docker images"
docker image prune -f >/dev/null 2>&1 || true

log "Deployment complete"
