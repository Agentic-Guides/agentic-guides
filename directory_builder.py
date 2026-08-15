#!/usr/bin/env python3
"""ディレクトリサイトビルダー（リンク集・著作権リスク0）
既存の外部サイトへのリンク集を、AIエージェントが探せる形（WebMCP/MCP/robots/構造化データ）で生成する。
内容は複製せず、リンクと要約だけ。訴訟リスク0。
"""
import os, json, re
from datetime import datetime

BASE = os.path.expanduser("~/Desktop/agentic-sites")

def _noext(f):
    return os.path.splitext(f)[0]

def build_directory(site, categories):
    """ディレクトリサイトを生成
    site: {name, slug, domain, description, kicker}
    categories: {カテゴリ名: [ {title, url, desc}, ... ]}
    """
    d = os.path.join(BASE, site["slug"])
    os.makedirs(os.path.join(d, "categories"), exist_ok=True)

    # カテゴリごとのページ
    for cat, links in categories.items():
        slug_cat = re.sub(r'[^a-z0-9]+', '-', cat.lower()).strip('-')
        html = _build_category_page(site, cat, links)
        with open(os.path.join(d, "categories", f"{slug_cat}.html"), "w", encoding="utf-8") as f:
            f.write(html)

    # インデックスページ
    index_html = _build_index(site, categories)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # robots.txt（AIエージェント許可）
    with open(os.path.join(d, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(_build_robots(site))

    # Content Signals
    with open(os.path.join(d, "contentsignals.txt"), "w", encoding="utf-8") as f:
        f.write("allow-agent-access: true\n")

    # sitemap
    with open(os.path.join(d, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(_build_sitemap(site, categories))

    # 法的ページ
    for name, content in _build_legal(site).items():
        with open(os.path.join(d, f"{name}.html"), "w", encoding="utf-8") as f:
            f.write(content)

    return True

def _build_index(site, categories):
    cards = ""
    for cat, links in categories.items():
        slug_cat = re.sub(r'[^a-z0-9]+', '-', cat.lower()).strip('-')
        cards += f'<div class="card"><h2><a href="/categories/{slug_cat}">{cat}</a></h2><p>{len(links)} resources</p></div>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{site['name']} | {site['kicker']}</title>
<meta name="description" content="{site['description']}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://{site['domain']}/">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"CollectionPage","name":site['name'],"description":site['description']})}</script>
<!-- WebMCP: make this site's content discoverable and usable by AI agents -->
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans JP','Hiragino Sans',sans-serif;font-size:18px;line-height:1.9;background:#f7f4ef;color:#2b2b2b}}
a{{color:#1a6b3c}}
h1{{font-size:28px;margin:20px 0;color:#1a6b3c}}
h2{{font-size:22px;margin:20px 0 10px;color:#1a6b3c}}
p{{margin-bottom:16px}}
.card{{background:#fff;padding:20px;border-radius:12px;max-width:860px;margin:0 auto 15px;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.site-header{{background:#1a6b3c;color:#fff;padding:30px 20px;text-align:center}}
.site-header h1{{color:#fff;font-size:28px}}
.site-header p{{color:#e8f5e9;font-size:15px}}
.site-footer{{background:#123a23;color:#c8e6c9;text-align:center;padding:30px 20px;margin-top:40px;font-size:14px}}
</style>
</head>
<body>
<header class="site-header"><h1>{site['name']}</h1><p>{site['description']}</p></header>
<main style="max-width:900px;margin:0 auto;padding:20px">
{cards}
</main>
<footer class="site-footer"><p>© 2026 {site['name']} | This directory provides links to external resources for reference purposes only. We do not endorse or guarantee any listed resource.</p></footer>
</body>
</html>"""

def _build_category_page(site, cat, links):
    items = ""
    for l in links:
        items += f'<div class="item"><h3><a href="{l["url"]}" rel="nofollow noopener">{l["title"]}</a></h3><p>{l["desc"]}</p></div>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{cat} | {site['name']}</title>
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://{site['domain']}/categories/{re.sub(r'[^a-z0-9]+','-',cat.lower()).strip('-')}">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"ItemList","name":cat,"numberOfItems":len(links)})}</script>
<!-- WebMCP: make this site's content discoverable and usable by AI agents -->
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans JP','Hiragino Sans',sans-serif;font-size:18px;line-height:1.9;background:#f7f4ef;color:#2b2b2b}}
a{{color:#1a6b3c}}
h1{{font-size:26px;margin:20px 0;color:#1a6b3c}}
h2{{font-size:22px;margin:20px 0 10px;color:#1a6b3c}}
p{{margin-bottom:16px}}
.item{{background:#fff;padding:20px;border-radius:12px;max-width:860px;margin:0 auto 15px;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.site-header{{background:#1a6b3c;color:#fff;padding:30px 20px;text-align:center}}
.site-header h1{{color:#fff;font-size:26px}}
.site-footer{{background:#123a23;color:#c8e6c9;text-align:center;padding:30px 20px;margin-top:40px;font-size:14px}}
</style>
</head>
<body>
<header class="site-header"><h1>{site['name']}</h1></header>
<main style="max-width:900px;margin:0 auto;padding:20px">
<h1>{cat}</h1>
<p>Below are curated resources for {cat.lower()}. Each link points to an external site for reference.</p>
{items}
</main>
<footer class="site-footer"><p>© 2026 {site['name']} | This directory provides links to external resources for reference purposes only.</p></footer>
</body>
</html>"""

def _build_robots(site):
    return f"""User-agent: *
Allow: /

# AIエージェントを許可
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: CCBot
Allow: /

Sitemap: https://{site['domain']}/sitemap.xml
"""

def _build_sitemap(site, categories):
    urls = [f'<url><loc>https://{site["domain"]}/</loc></url>']
    for cat in categories:
        slug_cat = re.sub(r'[^a-z0-9]+', '-', cat.lower()).strip('-')
        urls.append(f'<url><loc>https://{site["domain"]}/categories/{slug_cat}</loc></url>')
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>"""

def _build_legal(site):
    return {
        "privacy": f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Privacy Policy | {site['name']}</title></head><body><h1>Privacy Policy</h1><p>This directory site does not collect personal information. It provides links to external resources for reference purposes only.</p></body></html>""",
        "terms": f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Terms | {site['name']}</title></head><body><h1>Terms of Service</h1><p>This site provides links to external resources for reference purposes only. We do not endorse or guarantee any listed resource. Users should verify information with official sources.</p></body></html>""",
        "cookie": f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Cookie Policy | {site['name']}</title></head><body><h1>Cookie Policy</h1><p>This site does not use tracking cookies.</p></body></html>""",
    }
