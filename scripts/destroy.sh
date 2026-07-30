#!/usr/bin/env bash
# Tear down the AWS inference backend. Does NOT delete the external model bucket
# or the Vercel frontend. Usage: ./scripts/destroy.sh [--yes]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA="$ROOT/infra"
YES=0

for arg in "$@"; do
  case "$arg" in
    --yes|-y) YES=1 ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

command -v terraform >/dev/null || { echo "Required command not found: terraform" >&2; exit 1; }

echo "ECG-AI - AWS backend destroy"
echo "  This removes the artifacts S3 bucket, Lambda, Function URL, and IAM"
echo "  created by Terraform. The external model bucket and Vercel frontend"
echo "  are left untouched."
echo ""

if [[ "$YES" -ne 1 ]]; then
  read -r -p "Type 'yes' to destroy the backend: " confirm
  if [[ "$confirm" != "yes" ]]; then
    echo "Aborted."
    exit 0
  fi
fi

cd "$INFRA"
if [[ ! -d .terraform ]]; then
  terraform init -input=false -reconfigure
fi

terraform destroy -auto-approve -input=false -refresh=true

cat <<EOF

Destroy succeeded. AWS backend is gone.
Redeploy anytime with:  ./scripts/deploy.sh
EOF
