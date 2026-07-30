#!/usr/bin/env bash
# One-command portfolio deploy. Idempotent: safe to re-run after partial failure.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA="$ROOT/infra"
FRONTEND="$ROOT/frontend"
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

for cmd in terraform aws npm python; do
  command -v "$cmd" >/dev/null || { echo "Required command not found: $cmd" >&2; exit 1; }
done
[[ -f "$MODEL_LOCAL" ]] || { echo "Model file not found: $MODEL_LOCAL" >&2; exit 1; }

AWS_REGION="${AWS_REGION:-$(tfvar_or_default aws_region sa-east-1)}"
MODEL_BUCKET="${MODEL_BUCKET:-$(tfvar_or_default model_bucket_name ecg-ai-models-mlavinc)}"
MODEL_KEY="${MODEL_KEY:-$(tfvar_or_default model_key random_forest_final.joblib)}"

echo "ECG AI - portfolio deploy"
echo "  region : $AWS_REGION"
echo "  model  : s3://${MODEL_BUCKET}/${MODEL_KEY}"

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

CF_URL="$(tf_output cloudfront_domain_name)"
DIST_ID="$(tf_output cloudfront_distribution_id)"
FRONTEND_BUCKET="$(tf_output frontend_bucket_name)"
HEALTH_URL="${CF_URL}/api/health"

step "Waiting for CloudFront distribution ${DIST_ID} to deploy"
if ! aws cloudfront wait distribution-deployed --id "$DIST_ID"; then
  echo "  Warning: wait timed out or failed; continuing with sync/health checks."
fi

step "Building frontend (npm run build)"
(
  cd "$FRONTEND"
  [[ -d node_modules ]] || npm install
  npm run build
)

step "Syncing frontend to s3://${FRONTEND_BUCKET}"
aws s3 sync "$FRONTEND/dist/" "s3://${FRONTEND_BUCKET}/" --delete --region "$AWS_REGION"

step "Invalidating CloudFront cache"
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*" --region "$AWS_REGION" >/dev/null

step "Post-deploy health check: ${HEALTH_URL}"
ok=0
for i in $(seq 1 18); do
  if body="$(curl -fsS --max-time 45 "$HEALTH_URL" 2>/dev/null)" && echo "$body" | grep -q '"status"[[:space:]]*:[[:space:]]*"ok"'; then
    echo "  Attempt $i/18: OK ($body)"
    ok=1
    break
  fi
  echo "  Attempt $i/18: not ready yet"
  sleep 10
done

if [[ "$ok" -ne 1 ]]; then
  echo "Health check failed after 18 attempts. Try manually: $HEALTH_URL" >&2
  exit 1
fi

cat <<EOF

Deploy succeeded.

  App (CloudFront) : ${CF_URL}
  API health       : ${HEALTH_URL}
  API metrics      : ${CF_URL}/api/metrics
  API predict      : ${CF_URL}/api/predict

Tear down when finished:  ./scripts/destroy.sh
EOF
