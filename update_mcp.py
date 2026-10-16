#!/usr/bin/env python3
"""MCPサーバーの記事インデックスを再生成してデプロイする。
cronで毎日実行し、新記事をMCP検索に反映する。
"""
import sys, os, json, subprocess

BASE = os.path.expanduser("~/Desktop/agentic-sites")
sys.path.insert(0, BASE)
import site_builder as sb

# 英語サイトの記事を集約（インドネシア語は保留中なので除外）
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

def rebuild_index():
    all_articles = []
    for slug in EN_SITES:
        try:
            articles = sb.load_articles(slug)
            site = sb.get_site(slug, lang="en")
            for a in articles:
                all_articles.append({
                    "site": site["name"],
                    "slug": slug,
                    "title": a["title"],
                    "description": a.get("description", ""),
                    "category": a.get("category", ""),
                    "url": f"https://{site['domain']}/articles/{sb._noext(a['file'])}"
                })
        except Exception as e:
            print(f"  {slug}: {e}")
    # articles_data.js を生成
    js = "export const ARTICLES = " + json.dumps(all_articles, ensure_ascii=False, indent=2) + ";"
    with open(os.path.join(BASE, "mcp", "src", "articles_data.js"), "w", encoding="utf-8") as f:
        f.write(js)
    print(f"✅ MCPインデックス更新: {len(all_articles)}記事")
    return len(all_articles)

def _has_wrangler_oauth():
    """wrangler の OAuth トークンが有効か実測する（環境変数不要）。"""
    cfg = os.path.expanduser("~/.wrangler/config/default.toml")
    if not os.path.exists(cfg):
        return False
    try:
        with open(cfg, "r", encoding="utf-8") as f:
            txt = f.read()
    except Exception:
        return False
    # oauth_token が空でなく、refresh_token もあれば有効とみなす
    import re as _re
    m = _re.search(r'^oauth_token\s*=\s*"([^"]+)"', txt, _re.M)
    r = _re.search(r'^refresh_token\s*=\s*"([^"]+)"', txt, _re.M)
    return bool(m and m.group(1) and r and r.group(1))


def deploy_mcp():
    """MCP サーバーを再デプロイする。
    ★優先順位: 環境変数 CLOUDFLARE_API_TOKEN → wrangler の OAuth（~/.wrangler/config）。
    環境変数が無くても OAuth があればデプロイできる（実測 2026-10-16）。
    """
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    use_oauth = False
    if not token:
        if _has_wrangler_oauth():
            use_oauth = True
            print("ℹ️ CLOUDFLARE_API_TOKEN 未設定 → wrangler の OAuth を使用")
        else:
            print("⚠️ デプロイ不可: CLOUDFLARE_API_TOKEN も wrangler の OAuth も無い")
            print("   → 対処: `npx wrangler login` を実行するか、.env に CLOUDFLARE_API_TOKEN を設定")
            return False

    mcp_dir = os.path.join(BASE, "mcp")
    # wrangler のパスを解決（Windowsでは.cmd、無ければ npx）
    wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
    if not os.path.exists(wrangler):
        wrangler = "npx"
        args = ["--yes", "wrangler", "deploy"]
    else:
        args = ["deploy"]

    env = {**os.environ}
    if token:
        env["CLOUDFLARE_API_TOKEN"] = token
    else:
        # ★OAuth を使うときは、死んだトークンが邪魔になるので外す
        env.pop("CLOUDFLARE_API_TOKEN", None)
        env.pop("CLOUDFLARE_ACCOUNT_ID", None)

    r = subprocess.run(
        [wrangler] + args,
        cwd=mcp_dir, capture_output=True, text=True, timeout=300,
        env=env
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0 and ("Deployed" in out or "Uploaded" in out or "Published" in out):
        print("✅ MCPサーバー再デプロイ成功" + ("（OAuth）" if use_oauth else "（APIトークン）"))
        return True
    print("⚠️ MCPデプロイ失敗: %s" % out[-400:])
    return False
    mcp_dir = os.path.join(BASE, "mcp")
    # wranglerのパスを解決（Windowsでは.cmd）
    wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
    if not os.path.exists(wrangler):
        wrangler = "npx wrangler"
    r = subprocess.run(
        [wrangler, "deploy"],
        cwd=mcp_dir, capture_output=True, text=True, timeout=180,
        env={**os.environ, "CLOUDFLARE_API_TOKEN": token}
    )
    if r.returncode == 0:
        print("✅ MCPサーバー再デプロイ成功")
        return True
    print(f"⚠️ MCPデプロイ失敗: {r.stderr[-300:]}")
    return False

if __name__ == "__main__":
    n = rebuild_index()
    if n > 0:
        deploy_mcp()
