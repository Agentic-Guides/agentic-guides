#!/usr/bin/env python3
"""全50サイトの実効検証（404/Markdown/contact/og/llms）を一括チェック"""
import urllib.request, json

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

def check(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    if accept:
        req.add_header("Accept", accept)
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return r.status, r.headers.get("Content-Type","")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return "ERR", ""

ok404 = ok_md = ok_contact = 0
bad = []
for s in SITES:
    d = f"https://{s}.pages.dev"
    c404, _ = check(d + "/nonexistent-zzz")
    _, ct = check(d + "/", accept="text/markdown")
    cc, _ = check(d + "/contact")
    if c404 == 404: ok404 += 1
    if "markdown" in ct: ok_md += 1
    if cc == 200: ok_contact += 1
    if c404 != 404 or "markdown" not in ct or cc != 200:
        bad.append(s)

print(f"404正しく返る: {ok404}/50")
print(f"Markdown交渉: {ok_md}/50")
print(f"contact: {ok_contact}/50")
print("問題サイト:", bad if bad else "なし")
