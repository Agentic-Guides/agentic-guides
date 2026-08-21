#!/usr/bin/env python3
"""全英語ガイドサイトにMarkdown交渉付き _middleware.js を配置し再デプロイする"""
import os, sys, subprocess, shutil

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

# 記事サイト（英語50）のslug
SITES = ["grant-navigator","tax-filing-guide","mortgage-guide","side-hustle-hub","elder-care-guide",
         "insurance-guide","credit-score-guide","student-loan-guide","retirement-guide","small-business-guide",
         "investing-guide","pet-insurance-guide","estate-planning-guide","auto-loan-guide","rental-guide",
         "personal-loan-guide","banking-guide","financial-planning-guide","career-guide","home-improvement-guide",
         "hsa-guide","travel-insurance-guide","gig-work-guide","coupon-guide","subscription-guide",
         "crypto-guide","forex-guide","real-estate-investing-guide","dividend-guide","medical-billing-guide",
         "annuity-guide","credit-card-rewards-guide","saving-strategies-guide","home-equity-guide","entrepreneur-guide",
         "wealth-management-guide","charity-tax-guide","lease-guide","financial-literacy-guide","insurance-policy-guide",
         "disability-insurance-guide","unemployment-benefits-guide","medicaid-guide","tax-planning-guide","emergency-fund-guide",
         "financial-aid-guide","retirement-income-tax-guide","home-buying-guide","insurance-claims-guide","financial-advisor-guide"]

# 修正済みmiddleware（grant-navigatorからコピー）
src_mw = os.path.join(BASE, "grant-navigator", "functions", "_middleware.js")

wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(wrangler):
    wrangler = "npx.cmd wrangler"

ok = 0
fail = 0
for slug in SITES:
    d = os.path.join(BASE, slug)
    if not os.path.isdir(d):
        fail += 1
        print(f"SKIP {slug} (no dir)")
        continue
    # functions/_middleware.js を配置（grant-navigator以外はコピー）
    funcs = os.path.join(d, "functions")
    os.makedirs(funcs, exist_ok=True)
    dest = os.path.join(funcs, "_middleware.js")
    if slug != "grant-navigator":
        try:
            shutil.copy2(src_mw, dest)
        except Exception as e:
            fail += 1
            print(f"❌ copy {slug}: {e}")
            continue
    # デプロイ
    r = subprocess.run(
        [wrangler, "pages", "deploy", d, "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=180, env={**os.environ}
    )
    if r.returncode == 0:
        ok += 1
        print(f"✅ {slug}")
    else:
        fail += 1
        print(f"❌ deploy {slug}: {r.stderr[-120:]}")

print(f"\n=== 完了: {ok}/{len(SITES)} 成功, {fail} 失敗 ===")
