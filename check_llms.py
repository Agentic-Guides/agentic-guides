import subprocess, re

# 管理対象サイト
sites = [
    # 英語記事50
    "grant-navigator","tax-filing-guide","mortgage-guide","side-hustle-hub","elder-care-guide",
    "insurance-guide","credit-score-guide","student-loan-guide","retirement-guide","small-business-guide",
    "investing-guide","pet-insurance-guide","estate-planning-guide","auto-loan-guide","rental-guide",
    "personal-loan-guide","banking-guide","financial-planning-guide","career-guide","home-improvement-guide",
    "hsa-guide","travel-insurance-guide","gig-work-guide","coupon-guide","subscription-guide",
    "crypto-guide","forex-guide","real-estate-investing-guide","dividend-guide","medical-billing-guide",
    "annuity-guide","credit-card-rewards-guide","saving-strategies-guide","home-equity-guide","entrepreneur-guide",
    "wealth-management-guide","charity-tax-guide","lease-guide","financial-literacy-guide","insurance-policy-guide",
    "disability-insurance-guide","unemployment-benefits-guide","medicaid-guide","tax-planning-guide","emergency-fund-guide",
    "financial-aid-guide","retirement-income-tax-guide","home-buying-guide","insurance-claims-guide","financial-advisor-guide",
    # ディレクトリ27
    "ai-tools-directory","appliance-directory","baby-directory","baking-directory","basketball-directory",
    "beach-directory","beekeeping-directory","camping-directory","cat-care-directory","coffee-directory",
    "cooking-directory","diy-home-directory","dog-care-directory","fitness-directory","gardening-directory",
    "guitar-directory","hiking-directory","interior-design-directory","knitting-directory","meditation-directory",
    "nutrition-directory","photography-directory","running-directory","sewing-directory","travel-directory",
    "woodworking-directory","yoga-directory",
]

# デプロイ済みドメインのマッピング（suffix付き）
domain_map = {
    "ai-tools-directory":"ai-tools-directory-6ny",
    "insurance-guide":"insurance-guide-x35",
    "small-business-guide":"small-business-guide-bgu",
    "career-guide":"career-guide-dbn",
    "subscription-guide":"subscription-guide-c84",
    "crypto-guide":"crypto-guide-aor",
    "dividend-guide":"dividend-guide-aip",
    "home-buying-guide":"home-buying-guide-728",
}

ok, fail = [], []
for slug in sites:
    domain = domain_map.get(slug, slug) + ".pages.dev"
    try:
        r = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","--max-time","10", f"https://{domain}/llms.txt"],
                          capture_output=True, text=True, timeout=15)
        code = r.stdout.strip()
        if code == "200":
            ok.append(slug)
        else:
            fail.append((slug, domain, code))
    except Exception as e:
        fail.append((slug, domain, str(e)))

print(f"OK: {len(ok)}")
print(f"FAIL: {len(fail)}")
for slug, domain, code in fail:
    print(f"  ❌ {slug} ({domain}) → {code}")
