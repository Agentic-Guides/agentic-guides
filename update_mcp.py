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
            "hsa-guide", "travel-insurance-guide", "gig-work-guide", "coupon-guide", "subscription-guide"]

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

def deploy_mcp():
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        print("⚠️ CLOUDFLARE_API_TOKEN 未設定")
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
