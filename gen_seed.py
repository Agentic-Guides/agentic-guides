#!/usr/bin/env python3
"""汎用シード記事生成スクリプト
sites_config_en.json の各英語サイトについて、カテゴリ別に5記事を自動生成する。
site_builderのカテゴリ情報から、各ニッチの一般的な質問をFAQ形式で生成する。
"""
import sys, os, json, re

BASE = os.path.expanduser("~/Desktop/agentic-sites")
sys.path.insert(0, BASE)

# ニッチごとの記事生成テンプレート（カテゴリ名をベースに汎用的な記事を生成）
# 各サイトの記事は、そのサイトのカテゴリに基づいて意味のある内容になる

def build_articles(site):
    """サイトのカテゴリから5記事を生成"""
    name = site["name"]
    categories = site["categories"]
    cat_list = list(categories.keys())
    articles = []

    # カテゴリごとに1記事（最大5記事）
    for i, cat in enumerate(cat_list[:5]):
        cat_desc = categories[cat]
        # 汎用タイトル・本文生成
        title = f"{name}: {cat} Guide 2026"
        desc = f"Learn about {cat.lower()} for your {name.lower()}. {cat_desc}."
        body = f"""<h2>What is {cat}?</h2>
<p>{cat} is an important topic for anyone researching {name.lower()}. This article provides general information to help you understand the basics as of 2026. {cat_desc}.</p>
<h2>Who is this relevant to?</h2>
<p>This topic is relevant to individuals and families planning their finances, and to those who want accurate, up-to-date information. Requirements and rules can change, so it is wise to verify current details with official sources.</p>
<h2>How do I get started?</h2>
<p>The process generally involves understanding your needs, gathering relevant information, and comparing available options. The right approach depends on your individual circumstances and goals.</p>
<h2>What should I keep in mind?</h2>
<p>There are several important considerations. Because this involves financial decisions, you should not rely on general information alone. Consult a qualified professional for advice specific to your situation.</p>"""
        articles.append({
            "title": title,
            "description": desc,
            "category": cat,
            "body": body,
        })

    return articles

if __name__ == "__main__":
    # 特定サイトのシード記事を生成して保存
    slug = sys.argv[1] if len(sys.argv) > 1 else ""
    with open(os.path.join(BASE, "sites_config_en.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)
    target = [s for s in cfg["sites"] if s["slug"] == slug] if slug else [s for s in cfg["sites"]]
    for site in target:
        articles = build_articles(site)
        seed_path = os.path.join(BASE, "seeds", site["slug"].replace("-", "_") + "_seed.py")
        # シードファイルを生成
        content = f'''#!/usr/bin/env python3
"""{site["name"]} 初期記事シードデータ（英語）"""

ARTICLES = {json.dumps(articles, ensure_ascii=False, indent=4)}
'''
        with open(seed_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ {site['slug']}: {len(articles)}記事のシード生成")
