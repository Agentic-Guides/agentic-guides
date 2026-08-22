#!/usr/bin/env python3
"""全50サイトに _routes.json を配置し再デプロイして Markdown 交渉を確実化"""
import os, shutil, subprocess

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

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

ROUTES = '{\n  "version": 1,\n  "include": ["/*"],\n  "exclude": []\n}\n'
src_mw = os.path.join(BASE, "grant-navigator", "functions", "_middleware.js")
wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(wrangler):
    wrangler = "npx.cmd wrangler"

ok = fail = 0
for slug in SITES:
    d = os.path.join(BASE, slug)
    if not os.path.isdir(d):
        fail += 1; print(f"SKIP {slug}"); continue
    # _routes.json を配置
    open(os.path.join(d, "_routes.json"), "w").write(ROUTES)
    # Markdown入りmiddleware を確実に配置
    funcs = os.path.join(d, "functions")
    os.makedirs(funcs, exist_ok=True)
    if slug != "grant-navigator":
        shutil.copy2(src_mw, os.path.join(funcs, "_middleware.js"))
    r = subprocess.run(
        [wrangler, "pages", "deploy", d, "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=180, env={**os.environ}
    )
    if r.returncode == 0:
        ok += 1
    else:
        fail += 1
        print(f"FAIL {slug}")
print(f"\n=== {ok}/{len(SITES)} 成功, {fail} 失敗 ===")
