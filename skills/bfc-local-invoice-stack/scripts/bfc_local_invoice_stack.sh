#!/usr/bin/env bash

set -euo pipefail

DEFAULT_BFC_ROOT="$HOME/Documents/myHeytea/code/codex-downloads/service/scm/bfc"
BFC_ROOT="${BFC_ROOT:-$DEFAULT_BFC_ROOT}"
RUNTIME_DIR="${BFC_LOCAL_RUNTIME_DIR:-$HOME/.codex/run/bfc-local-invoice-stack}"
START_TIMEOUT_SECONDS="${BFC_START_TIMEOUT_SECONDS:-180}"
LAUNCHD_LABEL_PREFIX="com.heytea.codex.bfc-local-invoice-stack"
INFRA_CONTAINERS=(local-mysql8 local-redis7 local-eureka local-rabbitmq)
AUTH_BYPASS=0

usage() {
  cat <<'EOF'
Usage:
  bfc_local_invoice_stack.sh status
  bfc_local_invoice_stack.sh start infra|center|api [--auth-bypass]
  bfc_local_invoice_stack.sh logs center|manager|backend [--follow]
  bfc_local_invoice_stack.sh stop services|infra|all

Targets:
  infra   MySQL, Redis, Eureka, and RabbitMQ containers
  center  infra plus center-hsp-invoice
  api     center plus manager-hsp-invoice and service-hsp-invoice-backend
EOF
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

ensure_runtime_dir() {
  mkdir -p "$RUNTIME_DIR"
}

ensure_bfc_root() {
  [[ -d "$BFC_ROOT/center-hsp-invoice" ]] || die "BFC_ROOT is invalid: $BFC_ROOT"
}

resolve_java_home() {
  if [[ -n "${BFC_JAVA_HOME:-}" ]]; then
    JAVA8_HOME="$BFC_JAVA_HOME"
  elif [[ -d "/Library/Java/JavaVirtualMachines/jdk1.8.0_351.jdk/Contents/Home" ]]; then
    JAVA8_HOME="/Library/Java/JavaVirtualMachines/jdk1.8.0_351.jdk/Contents/Home"
  elif JAVA8_HOME="$(/usr/libexec/java_home -v 1.8 2>/dev/null)"; then
    :
  else
    die "Java 8 not found; set BFC_JAVA_HOME"
  fi
  [[ -x "$JAVA8_HOME/bin/java" ]] || die "invalid Java home: $JAVA8_HOME"
}

docker_ready() {
  docker info >/dev/null 2>&1
}

ensure_docker_engine() {
  require_command docker
  if docker_ready; then
    return
  fi

  if [[ -d "/Applications/Docker.app" ]]; then
    printf 'Starting Docker Desktop...\n'
    open -gja Docker
  else
    die "Docker engine is unavailable and Docker.app was not found"
  fi

  local elapsed=0
  while (( elapsed < 120 )); do
    if docker_ready; then
      printf 'Docker engine is ready.\n'
      return
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  die "Docker engine did not become ready within 120 seconds"
}

container_exists() {
  docker container inspect "$1" >/dev/null 2>&1
}

container_running() {
  [[ "$(docker inspect -f '{{.State.Running}}' "$1" 2>/dev/null || true)" == "true" ]]
}

wait_tcp() {
  local port="$1"
  local timeout="$2"
  local elapsed=0
  while (( elapsed < timeout )); do
    if nc -z 127.0.0.1 "$port" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done
  return 1
}

start_infra() {
  ensure_docker_engine
  require_command nc

  local missing=()
  local stopped=()
  local container
  for container in "${INFRA_CONTAINERS[@]}"; do
    if ! container_exists "$container"; then
      missing+=("$container")
    elif ! container_running "$container"; then
      stopped+=("$container")
    fi
  done

  if (( ${#missing[@]} > 0 )); then
    die "required containers are missing: ${missing[*]}; bootstrap is intentionally not automatic"
  fi
  if (( ${#stopped[@]} > 0 )); then
    docker start "${stopped[@]}" >/dev/null
    printf 'Started containers: %s\n' "${stopped[*]}"
  else
    printf 'Docker containers already running.\n'
  fi

  for container in "${INFRA_CONTAINERS[@]}"; do
    container_running "$container" || die "container stopped during startup: $container"
  done

  local ports=(3306 6379 8001 5672)
  local port
  for port in "${ports[@]}"; do
    wait_tcp "$port" 60 || die "local dependency port $port is not ready"
  done
  printf 'Infrastructure ready: mysql=3306 redis=6379 eureka=8001 rabbitmq=5672\n'
}

health_url() {
  case "$1" in
    center) printf '%s' 'http://127.0.0.1:5407/actuator/health' ;;
    manager) printf '%s' 'http://127.0.0.1:5406/actuator/health' ;;
    backend) printf '%s' 'http://127.0.0.1:5405/actuator/health' ;;
    *) return 1 ;;
  esac
}

service_management_port() {
  case "$1" in
    center) printf '%s' '5407' ;;
    manager) printf '%s' '5406' ;;
    backend) printf '%s' '5405' ;;
    *) return 1 ;;
  esac
}

service_repo_name() {
  case "$1" in
    center) printf '%s' 'center-hsp-invoice' ;;
    manager) printf '%s' 'manager-hsp-invoice' ;;
    backend) printf '%s' 'service-hsp-invoice-backend' ;;
    *) return 1 ;;
  esac
}

service_listener_matches() {
  if ! command -v lsof >/dev/null 2>&1; then
    return 0
  fi
  local pid
  local command_line
  for pid in $(lsof -nP -iTCP:"$(service_management_port "$1")" -sTCP:LISTEN -t 2>/dev/null || true); do
    command_line="$(ps -p "$pid" -o command= 2>/dev/null || true)"
    if [[ "$command_line" == *"/$(service_repo_name "$1")/target/classes"* ]]; then
      return 0
    fi
  done
  return 1
}

service_healthy() {
  local body
  body="$(curl -fsS --max-time 2 "$(health_url "$1")" 2>/dev/null || true)"
  [[ "$body" == *'"status":"UP"'* ]] && service_listener_matches "$1"
}

service_pid_file() {
  printf '%s/%s.pid' "$RUNTIME_DIR" "$1"
}

service_log_file() {
  printf '%s/%s.log' "$RUNTIME_DIR" "$1"
}

launchd_label() {
  printf '%s.%s' "$LAUNCHD_LABEL_PREFIX" "$1"
}

launchd_target() {
  printf 'gui/%s/%s' "$(id -u)" "$(launchd_label "$1")"
}

launchd_registered() {
  launchctl print "$(launchd_target "$1")" >/dev/null 2>&1
}

launchd_pid() {
  launchctl print "$(launchd_target "$1")" 2>/dev/null |
    awk '/^[[:space:]]*pid = [0-9]+$/ { print $3; exit }' || true
}

service_repo_path() {
  case "$1" in
    center) printf '%s/center-hsp-invoice' "$BFC_ROOT" ;;
    manager) printf '%s/manager-hsp-invoice' "$BFC_ROOT" ;;
    backend) printf '%s/service-hsp-invoice-backend' "$BFC_ROOT" ;;
    *) return 1 ;;
  esac
}

managed_pid_matches() {
  local name="$1"
  local pid="$2"
  local command_line
  local process_cwd
  command_line="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  process_cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' || true)"
  [[ "$command_line" == *"$(service_repo_path "$name")"* ]] ||
    [[ "$process_cwd" == "$(service_repo_path "$name")" && "$command_line" == *mvn* ]]
}

service_managed() {
  local launch_pid
  launch_pid="$(launchd_pid "$1")"
  if [[ -n "$launch_pid" ]] && kill -0 "$launch_pid" >/dev/null 2>&1 &&
    managed_pid_matches "$1" "$launch_pid"; then
    return 0
  fi

  local pid_file
  pid_file="$(service_pid_file "$1")"
  [[ -f "$pid_file" ]] || return 1
  local pid
  pid="$(cat "$pid_file")"
  kill -0 "$pid" >/dev/null 2>&1 && managed_pid_matches "$1" "$pid"
}

wait_service() {
  local name="$1"
  local pid="$2"
  local elapsed=0
  while (( elapsed < START_TIMEOUT_SECONDS )); do
    if service_healthy "$name"; then
      printf '%s is UP after %ss.\n' "$name" "$elapsed"
      return 0
    fi
    if ! kill -0 "$pid" >/dev/null 2>&1; then
      return 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  return 1
}

start_service() {
  local name="$1"
  if service_healthy "$name"; then
    if [[ "$name" == "backend" ]] && (( AUTH_BYPASS == 1 )); then
      printf 'WARNING: backend is already UP; its existing auth mode is unchanged.\n'
    fi
    printf '%s already UP; reused existing process.\n' "$name"
    return
  fi

  ensure_bfc_root
  ensure_runtime_dir
  resolve_java_home
  require_command mvn
  require_command curl
  require_command launchctl

  if service_managed "$name"; then
    local existing_pid
    existing_pid="$(launchd_pid "$name")"
    if [[ -z "$existing_pid" ]]; then
      existing_pid="$(cat "$(service_pid_file "$name")")"
    fi
    printf '%s is starting under PID %s; waiting for health.\n' "$name" "$existing_pid"
    if wait_service "$name" "$existing_pid"; then
      return
    fi
    die "$name process is running but health did not become UP"
  fi

  local repo
  local -a command
  case "$name" in
    center)
      repo="$BFC_ROOT/center-hsp-invoice"
      command=(mvn --no-transfer-progress spring-boot:run -Dspring-boot.run.profiles=local-eureka)
      ;;
    manager)
      repo="$BFC_ROOT/manager-hsp-invoice"
      command=(mvn --no-transfer-progress spring-boot:run -Dspring-boot.run.profiles=local-eureka
        "-Dspring-boot.run.arguments=--heytea.starter.gray.enabled=false --CENTER-HSP-INVOICE.ribbon.listOfServers=127.0.0.1:30318 --CENTER-HSP-INVOICE.ribbon.eureka.enabled=false --spring.rabbitmq.listener.simple.auto-startup=false --eureka.instance.hostname=127.0.0.1 --eureka.instance.prefer-ip-address=true --eureka.instance.ip-address=127.0.0.1")
      ;;
    backend)
      repo="$BFC_ROOT/service-hsp-invoice-backend"
      local backend_args="--server.port=30316 --management.server.port=5405 --eureka.client.service-url.defaultZone=http://127.0.0.1:8001/eureka/ --heytea.starter.gray.enabled=false --manager-hsp-invoice.ribbon.listOfServers=127.0.0.1:30317 --manager-hsp-invoice.ribbon.eureka.enabled=false --spring.rabbitmq.listener.simple.auto-startup=false --heytea.shop.metadata.storeIdSdk.host=127.0.0.1:9"
      if (( AUTH_BYPASS == 1 )); then
        backend_args="$backend_args --spring.aop.auto=false"
        printf 'WARNING: enabling local-only backend auth bypass.\n'
      fi
      command=(mvn --no-transfer-progress spring-boot:run "-Dspring-boot.run.arguments=$backend_args")
      ;;
    *)
      die "unknown service: $name"
      ;;
  esac

  local log_file
  local pid_file
  local label
  log_file="$(service_log_file "$name")"
  pid_file="$(service_pid_file "$name")"
  label="$(launchd_label "$name")"
  if launchd_registered "$name"; then
    launchctl remove "$label"
  fi
  : >"$log_file"
  launchctl submit -l "$label" -o "$log_file" -e "$log_file" -- \
    /bin/bash -c 'cd "$1" && shift && exec "$@"' _ "$repo" \
    env JAVA_HOME="$JAVA8_HOME" PATH="$JAVA8_HOME/bin:$PATH" "${command[@]}"

  local pid
  local attempts=0
  while (( attempts < 50 )); do
    pid="$(launchd_pid "$name")"
    [[ -n "$pid" ]] && break
    sleep 0.1
    attempts=$((attempts + 1))
  done
  if [[ -z "$pid" ]]; then
    launchctl remove "$label" >/dev/null 2>&1 || true
    die "launchd did not report a PID for $name"
  fi
  printf '%s' "$pid" >"$pid_file"
  printf 'Started %s with PID %s; log=%s\n' "$name" "$pid" "$log_file"
  if ! wait_service "$name" "$pid"; then
    tail -n 40 "$log_file" >&2 || true
    launchctl remove "$label" >/dev/null 2>&1 || true
    die "$name failed to become UP within ${START_TIMEOUT_SECONDS}s"
  fi
}

print_status() {
  printf '%-18s %-10s %-10s\n' 'COMPONENT' 'STATE' 'OWNER'
  if ! command -v docker >/dev/null 2>&1 || ! docker_ready; then
    printf '%-18s %-10s %-10s\n' 'docker-engine' 'DOWN' '-'
  else
    printf '%-18s %-10s %-10s\n' 'docker-engine' 'UP' 'external'
    local container
    for container in "${INFRA_CONTAINERS[@]}"; do
      if ! container_exists "$container"; then
        printf '%-18s %-10s %-10s\n' "$container" 'MISSING' '-'
      elif container_running "$container"; then
        printf '%-18s %-10s %-10s\n' "$container" 'UP' 'docker'
      else
        printf '%-18s %-10s %-10s\n' "$container" 'DOWN' 'docker'
      fi
    done
  fi

  local service
  for service in center manager backend; do
    if service_healthy "$service"; then
      if service_managed "$service"; then
        printf '%-18s %-10s %-10s\n' "$service" 'UP' 'skill'
      else
        printf '%-18s %-10s %-10s\n' "$service" 'UP' 'external'
      fi
    else
      printf '%-18s %-10s %-10s\n' "$service" 'DOWN' '-'
    fi
  done
}

kill_tree() {
  local pid="$1"
  local child
  for child in $(pgrep -P "$pid" 2>/dev/null || true); do
    kill_tree "$child"
  done
  kill "$pid" >/dev/null 2>&1 || true
}

stop_service() {
  local name="$1"
  local pid_file
  pid_file="$(service_pid_file "$name")"
  if launchd_registered "$name"; then
    launchctl remove "$(launchd_label "$name")"
    rm -f "$pid_file"
    printf 'Stopped launchd-managed %s service.\n' "$name"
    return
  fi
  if [[ ! -f "$pid_file" ]]; then
    printf '%s is not managed by this skill; skipped.\n' "$name"
    return
  fi
  local pid
  pid="$(cat "$pid_file")"
  if kill -0 "$pid" >/dev/null 2>&1 && managed_pid_matches "$name" "$pid"; then
    kill_tree "$pid"
    printf 'Stopped managed %s process tree at PID %s.\n' "$name" "$pid"
  elif kill -0 "$pid" >/dev/null 2>&1; then
    printf '%s PID file is stale and points to an unrelated process; skipped PID %s.\n' "$name" "$pid"
  fi
  rm -f "$pid_file"
}

stop_services() {
  stop_service backend
  stop_service manager
  stop_service center
}

stop_infra() {
  require_command docker
  if ! docker_ready; then
    printf 'Docker engine is already stopped.\n'
    return
  fi
  local running=()
  local container
  for container in "${INFRA_CONTAINERS[@]}"; do
    if container_exists "$container" && container_running "$container"; then
      running+=("$container")
    fi
  done
  if (( ${#running[@]} > 0 )); then
    docker stop "${running[@]}" >/dev/null
    printf 'Stopped containers: %s\n' "${running[*]}"
  else
    printf 'Infrastructure containers already stopped.\n'
  fi
}

show_logs() {
  local name="$1"
  local follow="${2:-}"
  local log_file
  log_file="$(service_log_file "$name")"
  [[ -f "$log_file" ]] || die "no managed log found for $name"
  if [[ "$follow" == "--follow" ]]; then
    tail -n 100 -f "$log_file"
  else
    tail -n 100 "$log_file"
  fi
}

main() {
  [[ "$START_TIMEOUT_SECONDS" =~ ^[0-9]+$ ]] || die "BFC_START_TIMEOUT_SECONDS must be an integer"
  local action="${1:-status}"
  case "$action" in
    status)
      print_status
      ;;
    start)
      local target="${2:-center}"
      if [[ "${3:-}" == "--auth-bypass" ]]; then
        AUTH_BYPASS=1
      elif [[ -n "${3:-}" ]]; then
        die "unknown option: ${3}"
      fi
      start_infra
      case "$target" in
        infra) ;;
        center) start_service center ;;
        api)
          start_service center
          start_service manager
          start_service backend
          ;;
        *) die "unknown start target: $target" ;;
      esac
      print_status
      ;;
    logs)
      [[ -n "${2:-}" ]] || die "logs requires center, manager, or backend"
      show_logs "$2" "${3:-}"
      ;;
    stop)
      case "${2:-services}" in
        services) stop_services ;;
        infra) stop_infra ;;
        all)
          stop_services
          stop_infra
          ;;
        *) die "unknown stop target: ${2}" ;;
      esac
      print_status
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      usage >&2
      die "unknown action: $action"
      ;;
  esac
}

main "$@"
