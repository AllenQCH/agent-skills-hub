#!/usr/bin/env bash
set -euo pipefail

SESSION="${OPENCLI_REUSE_SESSION:-}"
CLOSE_AFTER=0
BIND_CURRENT=0

usage() {
  cat <<'EOF'
Usage:
  opencli_reuse.sh [--session NAME] [--bind-current] [--close-after] <browser-subcommand> [args...]

Examples:
  opencli_reuse.sh open 'https://dbweb.test.heytea.com/#/my-resource'
  opencli_reuse.sh --bind-current open 'https://github.com/'
  opencli_reuse.sh --session github-web --bind-current open 'https://github.com/'
  opencli_reuse.sh state
  opencli_reuse.sh --close-after get url
  opencli_reuse.sh --session bk-console open 'https://devops-bk.heyteago.com/console/platform/entry'
EOF
}

infer_session_from_arg() {
  local arg="$1"
  case "$arg" in
    *account.heytea.com*) echo "heytea-sso-cn" ;;
    *dbweb.test.heytea.com*) echo "dbweb-explore" ;;
    *dbauto.heyteago.com*) echo "dbauto-query" ;;
    *devops-bk.heyteago.com*) echo "bk-console" ;;
    *github.com*) echo "github-web" ;;
    *) echo "opencli-explore" ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session)
      [[ $# -ge 2 ]] || { echo "Missing value for --session" >&2; exit 2; }
      SESSION="$2"
      shift 2
      ;;
    --close-after)
      CLOSE_AFTER=1
      shift
      ;;
    --bind-current)
      BIND_CURRENT=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

[[ $# -gt 0 ]] || { usage >&2; exit 2; }

if [[ -z "$SESSION" ]]; then
  case "$1" in
    open|analyze)
      if [[ $# -ge 2 ]]; then
        SESSION="$(infer_session_from_arg "$2")"
      else
        SESSION="opencli-explore"
      fi
      ;;
    *)
      SESSION="opencli-explore"
      ;;
  esac
fi

if [[ "$BIND_CURRENT" -eq 1 ]]; then
  opencli browser "$SESSION" bind >/dev/null
fi

cleanup() {
  if [[ "$CLOSE_AFTER" -eq 1 ]]; then
    opencli browser "$SESSION" close >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

TMP_ERR="$(mktemp)"
if opencli browser "$SESSION" "$@" 2>"$TMP_ERR"; then
  rm -f "$TMP_ERR"
  exit 0
fi

ERR_MSG="$(cat "$TMP_ERR")"
rm -f "$TMP_ERR"

if [[ "$ERR_MSG" == *"No tab with given id"* ]]; then
  opencli browser "$SESSION" close >/dev/null 2>&1 || true
  opencli browser "$SESSION" "$@"
  exit $?
fi

echo "$ERR_MSG" >&2
exit 1
