#!/usr/bin/env python3
"""curl方式で全50サイトのMarkdown交渉を一括検証（ヘッダー正確）"""
import subprocess

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

ok = 0
bad = []
for s in SITES:
    url = f"https://{s}.pages.dev/"
    r = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{content_type}", url,
         "-H", "Accept: text/markdown", "-H", "Cache-Control: no-cache"],
        capture_output=True, text=True, timeout=20
    )
    ct = r.stdout
    if "markdown" in ct:
        ok += 1
    else:
        bad.append(s)

print(f"Markdown交渉: {ok}/50")
print("NG:", bad if bad else "なし")
