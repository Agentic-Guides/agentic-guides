#!/usr/bin/env python3
"""パイロットサイト構築・デプロイCLI
使い方:
  python site_cli.py build <slug>        # サイトファイル生成
  python site_cli.py deploy <slug>       # Cloudflare Pagesにデプロイ
  python site_cli.py seed <slug>         # シード記事を読み込む
  python site_cli.py all <slug>          # seed + build + deploy
"""
import sys, os, importlib, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import site_builder as sb

def seed_articles(slug, seed_module):
    """シードデータから記事を読み込む"""
    articles = sb.load_articles(slug)
    existing = {a["title"] for a in articles}
    for a in seed_module.ARTICLES:
        if a["title"] not in existing:
            articles.append({
                "title": a["title"],
                "description": a.get("description", ""),
                "category": a.get("category", ""),
                "date": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
                "file": slugify(a["title"]) + ".html",
                "body": a["body"],
            })
    sb.save_articles(slug, articles)
    return len(articles)

def slugify(text):
    """タイトルをファイル名用に変換（日本語はそのまま、URLエンコードはsitemapで）"""
    import re
    text = re.sub(r'[／・!？。、]', '-', text)
    text = re.sub(r'[^\w\-ぁ-んァ-ヶ一-龠]', '', text)
    return text[:40]

def deploy(slug):
    site = sb.get_site(slug, lang=detect_lang(slug))
    wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
    if not os.path.exists(wrangler):
        wrangler = "npx wrangler"
    # Cloudflare APIトークンは環境変数から取得（コードにハードコードしない）
    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not cf_token:
        print("⚠️ CLOUDFLARE_API_TOKEN 環境変数が未設定です")
        return
    result = subprocess.run(
        [wrangler, "pages", "deploy", sb.site_dir(slug), "--project-name=" + site["project"], "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "CLOUDFLARE_API_TOKEN": cf_token}
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"⚠️ デプロイ失敗: {result.stderr}")

def detect_lang(slug):
    """サイトの言語を判定"""
    en_slugs = {"grant-navigator", "tax-filing-guide", "mortgage-guide", "side-hustle-hub", "elder-care-guide"}
    id_slugs = {"panduan-bantuan", "panduan-pajak", "panduan-kpr", "panduan-sampingan", "panduan-lansia"}
    if slug in en_slugs:
        return "en"
    if slug in id_slugs:
        return "id"
    return "ja"

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    slug = sys.argv[2] if len(sys.argv) > 2 else "hojokin-nav"

    if cmd in ("seed", "all"):
        # シードを動的に読み込み
        seed_map = {
            "hojokin-nav": "hojokin_nav_seed",
            "kakutei-guide": "kakutei_guide_seed",
            "sumai-loan": "sumai_loan_seed",
            "fukugyo-master": "fukugyo_master_seed",
            "kaigo-seido": "kaigo_seido_seed",
            "grant-navigator": "grant_navigator_seed",
            "tax-filing-guide": "tax_filing_guide_seed",
            "mortgage-guide": "mortgage_guide_seed",
            "side-hustle-hub": "side_hustle_hub_seed",
            "elder-care-guide": "elder_care_guide_seed",
            "panduan-bantuan": "panduan_bantuan_seed",
            "panduan-pajak": "panduan_pajak_seed",
            "panduan-kpr": "panduan_kpr_seed",
            "panduan-sampingan": "panduan_sampingan_seed",
            "panduan-lansia": "panduan_lansia_seed",
        }
        modname = seed_map.get(slug)
        if modname:
            mod = importlib.import_module("seeds." + modname)
            n = seed_articles(slug, mod)
            print(f"✅ {slug}: シード {n} 記事読み込み")
        else:
            print(f"⚠️ {slug}: シードモジュール未定義")

    if cmd in ("build", "all"):
        lang = detect_lang(slug)
        articles = sb.load_articles(slug)
        n = sb.write_site_files(slug, articles, lang=lang)
        print(f"✅ {slug}: サイト生成完了（{n}記事）")

    if cmd == "deploy":
        deploy(slug)
