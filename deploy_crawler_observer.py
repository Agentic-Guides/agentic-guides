#!/usr/bin/env python3
"""全英語サイトにAIクローラー観測middleware + KVバインディングを一括展開する。
grant-navigatorで動作確認済みのパターンを全サイトに適用する。
"""
import os, sys, json, subprocess, shutil

BASE = os.path.expanduser("~/Desktop/agentic-sites")
sys.path.insert(0, BASE)

# 英語サイト全50
EN_SITES = ["grant-navigator", "tax-filing-guide", "mortgage-guide", "side-hustle-hub", "elder-care-guide",
            "insurance-guide", "credit-score-guide", "student-loan-guide", "retirement-guide", "small-business-guide",
            "investing-guide", "pet-insurance-guide", "estate-planning-guide", "auto-loan-guide", "rental-guide",
            "personal-loan-guide", "banking-guide", "financial-planning-guide", "career-guide", "home-improvement-guide",
            "hsa-guide", "travel-insurance-guide", "gig-work-guide", "coupon-guide", "subscription-guide",
            "crypto-guide", "forex-guide", "real-estate-investing-guide", "dividend-guide", "medical-billing-guide",
            "annuity-guide", "credit-card-rewards-guide", "saving-strategies-guide", "home-equity-guide", "entrepreneur-guide",
            "wealth-management-guide", "charity-tax-guide", "lease-guide", "financial-literacy-guide", "insurance-policy-guide",
            "disability-insurance-guide", "unemployment-benefits-guide", "medicaid-guide", "tax-planning-guide", "emergency-fund-guide",
            "financial-aid-guide", "retirement-income-tax-guide", "home-buying-guide", "insurance-claims-guide", "financial-advisor-guide"]

KV_ID = "f5dd85b9236c4b25b61b4b8131a5d528"
ACCOUNT = "c1af587d36d1b6cb2848fc4e5546923d"
TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")

MIDDLEWARE_SRC = os.path.join(BASE, "crawler-observer", "_middleware.js")

def deploy_middleware(slug):
    """サイトにmiddlewareを配置"""
    site_dir = os.path.join(BASE, slug)
    funcs_dir = os.path.join(site_dir, "functions")
    os.makedirs(funcs_dir, exist_ok=True)
    dst = os.path.join(funcs_dir, "_middleware.js")
    shutil.copy(MIDDLEWARE_SRC, dst)
    return os.path.exists(dst)

def write_wrangler_toml(slug):
    """サイトにwrangler.tomlを置いてKVバインディングを宣言（デプロイ物に反映させる鍵）"""
    site_dir = os.path.join(BASE, slug)
    toml = f'''name = "{slug}"
compatibility_date = "2026-08-01"

[[kv_namespaces]]
binding = "AGENTIC_AI_CRAWLERS"
id = "{KV_ID}"
'''
    with open(os.path.join(site_dir, "wrangler.toml"), "w", encoding="utf-8") as f:
        f.write(toml)
    return os.path.exists(os.path.join(site_dir, "wrangler.toml"))

def set_kv_binding(slug):
    """PagesプロジェクトにKVバインディングを設定"""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/pages/projects/{slug}"
    body = json.dumps({
        "deployment_configs": {
            "production": {
                "kv_namespaces": {
                    "AGENTIC_AI_CRAWLERS": {"namespace_id": KV_ID}
                }
            }
        }
    })
    r = subprocess.run(
        ["curl", "-s", "-X", "PATCH", "-H", f"Authorization: Bearer {TOKEN}",
         "-H", "Content-Type: application/json", url, "-d", body],
        capture_output=True, text=True, timeout=30
    )
    try:
        d = json.loads(r.stdout)
        return d.get("success", False)
    except:
        return False

def deploy_site(slug):
    """サイトをデプロイ（KVバインディング反映）"""
    wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
    if not os.path.exists(wrangler):
        wrangler = "npx wrangler"
    r = subprocess.run(
        [wrangler, "pages", "deploy", os.path.join(BASE, slug),
         "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "CLOUDFLARE_API_TOKEN": TOKEN}
    )
    return r.returncode == 0

if __name__ == "__main__":
    if not TOKEN:
        print("⚠️ CLOUDFLARE_API_TOKEN 未設定")
        sys.exit(1)

    results = []
    for slug in EN_SITES:
        # 1. middleware配置
        mw = deploy_middleware(slug)
        # 2. wrangler.toml生成（KVバインディング反映の鍵）
        wt = write_wrangler_toml(slug)
        # 3. KVバインディング設定
        kv = set_kv_binding(slug)
        # 4. デプロイ
        dep = deploy_site(slug)
        status = "✅" if (mw and wt and kv and dep) else "⚠️"
        results.append(f"{status} {slug}: mw={mw} toml={wt} KV={kv} deploy={dep}")
        print(f"{status} {slug}: mw={mw} toml={wt} KV={kv} deploy={dep}")

    print("\n=== 完了 ===")
    ok = sum(1 for r in results if r.startswith("✅"))
    print(f"成功: {ok}/{len(EN_SITES)}")
