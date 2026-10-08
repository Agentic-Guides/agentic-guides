"""未デプロイサイトを【1つの集約プロジェクト】にまとめてデプロイする。

★方式: サブパス集約
  https://<hub>.pages.dev/bird-care-directory/
  https://<hub>.pages.dev/boat-directory/
  ...

★理由（実測）:
  - Cloudflare Pages は 100 プロジェクトが上限（実測で到達済み）
  - 1サイト1プロジェクトでは上限に当たる
  - 1ドメイン集約は SEO 的にも有利（ドメインオーソリティ集中）

★構成:
  _hub/
    index.html          ← 全サイトの一覧ポータル
    <site>/             ← 各サイトの全ファイルをコピー（サブパスで動くようにhrefを調整）
"""
import os, re, shutil, sys, subprocess, json

BASE = os.path.expanduser("~/Desktop/agentic-sites")
HUB = os.path.join(BASE, "_hub")
HUB_NAME = "ai-directory-hub"

# --- 未デプロイ一覧（既存ロジック） ---
deployed = set()
for line in open(os.path.join(BASE, "_pages_real.txt"), encoding="utf-8"):
    p = line.split()
    if len(p) >= 2:
        deployed.add(p[0])

local = []
for d in sorted(os.listdir(BASE)):
    if d.startswith(("_", ".")) or d == "__pycache__":
        continue
    p = os.path.join(BASE, d)
    if os.path.isdir(p) and os.path.exists(os.path.join(p, "index.html")):
        local.append(d)

missing = [d for d in local
           if not any(n == d or n.startswith(d + "-") or d.startswith(n) for n in deployed)]

print("集約対象:", len(missing), "サイト")

if os.path.exists(HUB):
    shutil.rmtree(HUB)
os.makedirs(HUB)

# --- 各サイトをコピーし、リンクをサブパス向けに書き換え ---
copied = []
for name in missing:
    src = os.path.join(BASE, name)
    dst = os.path.join(HUB, name)
    shutil.copytree(src, dst)
    # 絶対パス（href="/..." src="/..."）をサブパス配下に書き換える
    for root, _, files in os.walk(dst):
        for fn in files:
            if not fn.endswith((".html", ".xml", ".txt")):
                continue
            fp = os.path.join(root, fn)
            try:
                s = open(fp, encoding="utf-8").read()
            except Exception:
                continue
            orig = s
            # href="/xxx" → href="/<name>/xxx"（ただし既に /<name>/ の場合は除外）
            s = re.sub(r'(href|src)="/(?!%s/)([^"]*)"' % re.escape(name),
                       lambda m: '%s="/%s/%s"' % (m.group(1), name, m.group(2)), s)
            if s != orig:
                open(fp, "w", encoding="utf-8").write(s)
    copied.append(name)
    print("  +", name)

# --- ポータル index.html ---
cards = "\n".join(
    '<li><a href="/%s/">%s</a></li>' % (n, n.replace("-", " ").title())
    for n in copied)
portal = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Resource Directory Hub</title>
<meta name="description" content="A hub of curated resource directories: hobbies, guides, and niche topics for AI agents and humans.">
<style>
body{font-family:system-ui,-apple-system,sans-serif;max-width:900px;margin:0 auto;padding:32px 20px;background:#fff;color:#111}
h1{font-size:1.6rem;margin:0 0 8px}
p.lead{color:#555;margin:0 0 28px}
ul{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
li a{display:block;padding:12px 14px;border:1px solid #e5e5e5;border-radius:10px;text-decoration:none;color:#111;font-size:.95rem}
li a:hover{border-color:#111;background:#fafafa}
footer{margin-top:40px;color:#888;font-size:.85rem}
</style>
</head>
<body>
<h1>AI Resource Directory Hub</h1>
<p class="lead">Curated directories across hobbies, guides, and niche topics. Built for both people and AI agents.</p>
<ul>
%s
</ul>
<footer><a href="/llms.txt">llms.txt</a> · <a href="/sitemap.xml">sitemap.xml</a> · <a href="/robots.txt">robots.txt</a></footer>
</body>
</html>""" % cards
open(os.path.join(HUB, "index.html"), "w", encoding="utf-8").write(portal)

# --- 集約サイトの llms.txt / sitemap.xml / robots.txt ---
open(os.path.join(HUB, "llms.txt"), "w", encoding="utf-8").write(
    "# AI Resource Directory Hub\n\n"
    "> Curated resource directories across hobbies, guides, and niche topics.\n\n"
    "## Directories\n" + "\n".join("- /%s/ - %s" % (n, n.replace("-", " ")) for n in copied) + "\n")

urls = "\n".join("  <url><loc>https://%s.pages.dev/%s/</loc></url>" % (HUB_NAME, n) for n in copied)
open(os.path.join(HUB, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % urls)

open(os.path.join(HUB, "robots.txt"), "w", encoding="utf-8").write(
    "User-agent: *\nAllow: /\n\nSitemap: https://%s.pages.dev/sitemap.xml\n" % HUB_NAME)

open(os.path.join(HUB, "contentsignals.txt"), "w", encoding="utf-8").write(
    "ai-train=yes, search=yes, ai-input=yes\n")
open(os.path.join(HUB, "_headers"), "w", encoding="utf-8").write(
    "/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: SAMEORIGIN\n")

total_files = sum(len(f) for _, _, f in os.walk(HUB))
print("\nハブ構築完了: %d サイト / %d ファイル" % (len(copied), total_files))
print("場所:", HUB)
