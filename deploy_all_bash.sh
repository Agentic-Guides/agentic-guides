#!/bin/bash
# 全50サイトをターミナル直接wranglerでデプロイ（Functions確実反映）
cd /c/Users/hohoh/Desktop/agentic-sites
export CLOUDFLARE_API_TOKEN=$(grep -oE 'CLOUDFLARE_API_TOKEN=[^ ]+' .env | cut -d= -f2)

SITES=("grant-navigator" "tax-filing-guide" "mortgage-guide" "side-hustle-hub" "elder-care-guide" \
"insurance-guide" "credit-score-guide" "student-loan-guide" "retirement-guide" "small-business-guide" \
"investing-guide" "pet-insurance-guide" "estate-planning-guide" "auto-loan-guide" "rental-guide" \
"personal-loan-guide" "banking-guide" "financial-planning-guide" "career-guide" "home-improvement-guide" \
"hsa-guide" "travel-insurance-guide" "gig-work-guide" "coupon-guide" "subscription-guide" \
"crypto-guide" "forex-guide" "real-estate-investing-guide" "dividend-guide" "medical-billing-guide" \
"annuity-guide" "credit-card-rewards-guide" "saving-strategies-guide" "home-equity-guide" "entrepreneur-guide" \
"wealth-management-guide" "charity-tax-guide" "lease-guide" "financial-literacy-guide" "insurance-policy-guide" \
"disability-insurance-guide" "unemployment-benefits-guide" "medicaid-guide" "tax-planning-guide" "emergency-fund-guide" \
"financial-aid-guide" "retirement-income-tax-guide" "home-buying-guide" "insurance-claims-guide" "financial-advisor-guide")

ok=0; fail=0
for slug in "${SITES[@]}"; do
  cd "/c/Users/hohoh/Desktop/agentic-sites/$slug"
  if npx wrangler pages deploy . --project-name "$slug" --commit-dirty=true --branch=main >/dev/null 2>&1; then
    ok=$((ok+1))
  else
    fail=$((fail+1)); echo "FAIL $slug"
  fi
done
echo "=== $ok/50 成功, $fail 失敗 ==="
