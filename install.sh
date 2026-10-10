#!/usr/bin/env bash
# battage installer -- Fedora only (dependencies come from dnf).
#
#   ./install.sh            install (check deps, install missing ones, copy to ~/.local/bin)
#   ./install.sh uninstall  remove the installed script
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
DEPS=(python3 upower)   # command name == Fedora package name for both

die() { echo "error: $*" >&2; exit 1; }
info() { echo ":: $*"; }

check_fedora() {
  [ -r /etc/os-release ] || die "/etc/os-release missing -- cannot detect distro"
  # shellcheck disable=SC1091
  . /etc/os-release
  case " ${ID:-} ${ID_LIKE:-} " in
    *fedora*) : ;;
    *) die "this installer only supports Fedora (detected: ${PRETTY_NAME:-unknown}).
     Install python3 and upower with your own package manager, then copy 'battage'
     to somewhere on your PATH." ;;
  esac
}

ensure_deps() {
  local pkg missing=()
  for pkg in "${DEPS[@]}"; do
    command -v "$pkg" >/dev/null 2>&1 || missing+=("$pkg")
  done
  if ((${#missing[@]})); then
    command -v dnf >/dev/null 2>&1 || die "dnf not found but ${missing[*]} missing"
    info "installing missing dependencies: ${missing[*]}"
    sudo dnf install -y "${missing[@]}"
  else
    info "dependencies present (${DEPS[*]})"
  fi
}

install_battage() {
  [ -f "${SRC_DIR}/battage" ] || die "'battage' not found next to this script"
  mkdir -p "$BIN_DIR"
  install -m755 "${SRC_DIR}/battage" "${BIN_DIR}/battage"
  info "installed ${BIN_DIR}/battage"
  case ":${PATH}:" in
    *":${BIN_DIR}:"*) : ;;
    *) echo "note: ${BIN_DIR} is not on your PATH. Add it with:"
       echo "      echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc" ;;
  esac
  if ! compgen -G "/var/lib/upower/history-charge-*.dat" >/dev/null; then
    echo "note: no charge history in /var/lib/upower yet -- upower logs it only"
    echo "      while the machine runs. Check 'systemctl status upower'."
  fi
}

uninstall_battage() {
  rm -f "${BIN_DIR}/battage"
  info "removed ${BIN_DIR}/battage"
}

case "${1:-install}" in
  install)   check_fedora; ensure_deps; install_battage ;;
  uninstall) uninstall_battage ;;
  *) die "usage: $0 [install|uninstall]" ;;
esac
