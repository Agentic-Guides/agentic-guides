#!/usr/bin/env python3
"""全サイト（英語50+日本語10）を再ビルド・再デプロイ。統計ページ実データ反映。"""
import os, sys, subprocess

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

EN = ["grant-navigator","tax-filing-guide","mortgage-guide","side-hustle-hub","elder-care-guide",
      "insurance-guide","credit-score-guide","student-loan-guide","retirement-guide","small-business-guide",
      "investing-guide","pet-insurance-guide","estate-planning-guide","auto-loan-guide","rental-guide",
      "personal-loan-guide","banking-guide","financial-planning-guide","career-guide","home-improvement-guide",
      "hsa-guide","travel-insurance-guide","gig-work-guide","coupon-guide","subscription-guide",
      "crypto-guide","forex-guide","real-estate-investing-guide","dividend-guide","medical-billing-guide",
      "annuity-guide","credit-card-rewards-guide","saving-strategies-guide","home-equity-guide","entrepreneur-guide",
      "wealth-management-guide","charity-tax-guide","lease-guide","financial-literacy-guide","insurance-policy-guide",
      "disability-insurance-guide","unemployment-benefits-guide","medicaid-guide","tax-planning-guide","emergency-fund-guide",
      "financial-aid-guide","retirement-income-tax-guide","home-buying-guide","insurance-claims-guide","financial-advisor-guide"]
ALL = EN

wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(wrangler):
    wrangler = "npx wrangler"

ok = 0
fail = 0
for slug in ALL:
    # 再ビルド
    r = subprocess.run(["python", "site_cli.py", "build", slug],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        fail += 1
        print(f"❌ build {slug}")
        continue
    # 再デプロイ
    r = subprocess.run(
        [wrangler, "pages", "deploy", os.path.join(BASE, slug),
         "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=120,
        env={**os.environ}
    )
    if r.returncode == 0:
        ok += 1
        print(f"✅ {slug}")
    else:
        fail += 1
        print(f"❌ deploy {slug}: {r.stderr[-150:]}")

print(f"\n=== 完了: {ok}/{len(ALL)} 成功, {fail} 失敗 ===")
