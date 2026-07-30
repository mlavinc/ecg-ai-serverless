#!/usr/bin/env bash
# Deploy the AWS inference backend. Frontend is hosted on Vercel separately.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA="$ROOT/infra"
MODEL_LOCAL="$ROOT/data/models/random_forest_final.joblib"
LAMBDA_ZIP="$ROOT/lambda.zip"

step() { printf '\n==> %s\n' "$*"; }

tf() {
  (cd "$INFRA" && terraform "$@")
}

tf_output() {
  local value
  value="$(cd "$INFRA" && terraform output -raw "$1")"
  if [[ -z "$value" ]]; then
    echo "Missing Terraform output '$1'. Did terraform apply succeed?" >&2
    exit 1
  fi
  printf '%s' "$value"
}

tfvar_or_default() {
  local name="$1" default="$2" file="$INFRA/terraform.tfvars"
  local env_name="TF_VAR_${name}"
  if [[ -n "${!env_name:-}" ]]; then
    printf '%s' "${!env_name}"
    return
  fi
  if [[ -f "$file" ]]; then
    local value
    value="$(sed -nE "s/^[[:space:]]*${name}[[:space:]]*=[[:space:]]*\"([^\"]+)\".*/\1/p" "$file" | head -n1 || true)"
    if [[ -n "$value" ]]; then
      printf '%s' "$value"
      return
    fi
  fi
  printf '%s' "$default"
}

for cmd in terraform aws python; do
  command -v "$cmd" >/dev/null || { echo "Required command not found: $cmd" >&2; exit 1; }
done
[[ -f "$MODEL_LOCAL" ]] || { echo "Model file not found: $MODEL_LOCAL" >&2; exit 1; }

AWS_REGION="${AWS_REGION:-$(tfvar_or_default aws_region sa-east-1)}"
MODEL_BUCKET="${MODEL_BUCKET:-$(tfvar_or_default model_bucket_name ecg-ai-models-mlavinc)}"
MODEL_KEY="${MODEL_KEY:-$(tfvar_or_default model_key random_forest_final.joblib)}"

echo "ECG-AI - AWS backend deploy"
echo "  region : $AWS_REGION"
echo "  model  : s3://${MODEL_BUCKET}/${MODEL_KEY}"
echo "  frontend: Vercel (set VITE_API_URL to the Function URL below)"

step "Building Lambda package (scripts/build_package.py)"
(cd "$ROOT" && python scripts/build_package.py)
[[ -f "$LAMBDA_ZIP" ]] || { echo "Expected artifact missing: $LAMBDA_ZIP" >&2; exit 1; }

step "Ensuring trained model is in S3"
if ! aws s3api head-bucket --bucket "$MODEL_BUCKET" --region "$AWS_REGION" >/dev/null 2>&1; then
  echo "Model bucket s3://${MODEL_BUCKET} does not exist or is not accessible." >&2
  echo "Create it once outside Terraform, then re-run." >&2
  exit 1
fi
if aws s3api head-object --bucket "$MODEL_BUCKET" --key "$MODEL_KEY" --region "$AWS_REGION" >/dev/null 2>&1; then
  echo "  Model already present (skipping upload)."
else
  echo "  Uploading $MODEL_LOCAL ..."
  aws s3 cp "$MODEL_LOCAL" "s3://${MODEL_BUCKET}/${MODEL_KEY}" --region "$AWS_REGION"
fi

step "terraform init"
tf init -input=false -reconfigure

step "terraform apply"
tf apply -auto-approve -input=false -refresh=true

FUNCTION_URL="$(tf_output lambda_function_url)"
FUNCTION_URL="${FUNCTION_URL%/}"
HEALTH_URL="${FUNCTION_URL}/health"

step "Post-deploy health check: ${HEALTH_URL}"
ok=0
for i in $(seq 1 12); do
  if body="$(curl -fsS --max-time 45 "$HEALTH_URL" 2>/dev/null)" && echo "$body" | grep -q '"status"[[:space:]]*:[[:space:]]*"ok"'; then
    echo "  Attempt $i/12: OK ($body)"
    ok=1
    break
  fi
  echo "  Attempt $i/12: not ready yet"
  sleep 8
done

if [[ "$ok" -ne 1 ]]; then
  echo "Health check failed after 12 attempts. Try manually: $HEALTH_URL" >&2
  exit 1
fi

cat <<EOF

Deploy succeeded.

  Lambda Function URL : ${FUNCTION_URL}/
  API health          : ${HEALTH_URL}
  API metrics         : ${FUNCTION_URL}/metrics
  API predict         : ${FUNCTION_URL}/predict

  Vercel env          : VITE_API_URL=${FUNCTION_URL}

Tear down when finished:  ./scripts/destroy.sh
EOF
