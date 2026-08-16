#!/usr/bin/env python3
"""Agentic Commerce マルチサイト生成基盤
各サイトを sites_config.json の設定に基づいて生成する共通モジュール。
AEO最適化 + JSON-LD + WebMCP + Content Signals を自動付与する。
"""
import json, os, re, subprocess
from datetime import datetime
from urllib.parse import quote

BASE_DIR = os.path.expanduser("~/Desktop/agentic-sites")
CONFIG_PATH = os.path.join(BASE_DIR, "sites_config.json")
CONFIG_PATH_EN = os.path.join(BASE_DIR, "sites_config_en.json")

def load_config(lang="ja"):
    if lang == "en":
        path = CONFIG_PATH_EN
    else:
        path = CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_site(slug, lang="ja"):
    cfg = load_config(lang)
    for site in cfg["sites"]:
        if site["slug"] == slug:
            return site
    raise ValueError(f"サイト '{slug}' が見つかりません")

def site_dir(slug):
    return os.path.join(BASE_DIR, slug)

def _noext(fname):
    return fname[:-5] if fname.endswith(".html") else fname

def load_articles(slug):
    os.makedirs(site_dir(slug), exist_ok=True)
    path = os.path.join(site_dir(slug), "articles.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_articles(slug, articles):
    path = os.path.join(site_dir(slug), "articles.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

def build_article_html(site, a, all_articles=None):
    """記事HTMLを生成（AEO最適化 + JSON-LD Article/FAQPage + 内部リンク）"""
    domain = site["domain"]
    lang = site.get("lang", "ja")
    noext = _noext(a["file"])
    title = a["title"]
    body = a.get("body", "")
    date = a.get("date", datetime.now().strftime("%Y-%m-%d"))

    # 言語別の免責・アフィリエイト開示
    if lang == "en":
        disclaimer = "This site provides information for reference purposes only and does not constitute professional legal, tax, medical, or financial advice. Information may not be current due to policy changes. Always verify with official sources or consult a professional."
        affiliate_note = "This site may contain affiliate links (including Amazon Associates). We may earn a commission from purchases made through these links."
        html_lang = "en"
        # 記事冒頭の免責（FTC・YMYL対策）
        top_notice = '<p><em>This article provides general information for reference purposes only and does not constitute professional legal, tax, medical, or financial advice. Rules and programs may change. Always verify current details with official sources or consult a qualified professional.</em></p>'
    else:
        disclaimer = "当サイトは情報の提供を目的としており、法律・税務・医療・金融等の専門的助言を提供するものではありません。記載内容は公開時点の情報であり、制度変更等により最新でない場合があります。必ず公式サイトや専門家にご確認ください。"
        affiliate_note = "本サイトにはアフィリエイト広告（Amazonアソシエイト等）を含む場合があります。リンク経由の購入により当サイトに収益が発生することがあります。"
        html_lang = "ja"
        top_notice = '<p><em>本記事は一般的な情報提供を目的としており、法律・税務・医療・金融等の専門的助言を提供するものではありません。制度や手続きは変更される場合があります。必ず公式サイトや専門家にご確認ください。</em></p>'

    # 記事冒頭に免責を自動挿入（重複防止）
    if top_notice not in body:
        body = top_notice + "\n" + body

    # 関連記事リンク（内部リンク・トピック深度強化）
    related_html = ""
    if all_articles:
        related = [x for x in all_articles if x["file"] != a["file"]][:3]
        if related:
            if lang == "en":
                related_html = '<div class="related"><h2>Related Articles</h2><ul>'
                for r in related:
                    r_noext = _noext(r["file"])
                    related_html += f'<li><a href="/articles/{r_noext}">{r["title"]}</a></li>'
                related_html += '</ul></div>'
            else:
                related_html = '<div class="related"><h2>関連記事</h2><ul>'
                for r in related:
                    r_noext = _noext(r["file"])
                    related_html += f'<li><a href="/articles/{r_noext}">{r["title"]}</a></li>'
                related_html += '</ul></div>'

    # 著者リンク（著者ページへの内部リンク）
    author_html = ""
    if lang == "en":
        author_html = '<p class="author">By <a href="/author">Agentic Guides Editorial Team</a></p>'
    else:
        author_html = '<p class="author">著者: <a href="/author">Agentic Guides編集部</a></p>'

    body = body + related_html + author_html

    # FAQ構造化データ（記事から「？で終わる見出し」を抽出してFAQにする）
    faq_items = []
    for m in re.finditer(r"<h2>([^<]*[?？][^<]*)</h2>", body):
        q = m.group(1).strip()
        rest = body[m.end():]
        ans_m = re.search(r"<p>([^<]{10,300})</p>", rest)
        if ans_m:
            faq_items.append(f'{{"@type":"Question","name":{json.dumps(q)},"acceptedAnswer":{{"@type":"Answer","text":{json.dumps(ans_m.group(1))}}}}}')
    faq_json = f'{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{",".join(faq_items)}]}}' if faq_items else ""

    # AIエージェント向け JSON-LD 強化: dateModified(最新性)・mainEntityOfPage(出典)・articleSection(カテゴリ)
    today_iso = datetime.now().strftime("%Y-%m-%d")
    category_name = a.get("category", "")
    jsonld = f'''{{"@context":"https://schema.org","@graph":[{{"@type":"Article","headline":{json.dumps(title)},"description":{json.dumps(a.get("description",""))},"url":"https://{domain}/articles/{noext}","datePublished":"{date[:10]}","dateModified":"{today_iso}","mainEntityOfPage":"https://{domain}/articles/{noext}","articleSection":{json.dumps(category_name)},"author":{{"@type":"Person","name":{json.dumps(site["name"])}}},"publisher":{{"@type":"Organization","name":{json.dumps(site["name"])}}}}}]}}'''

    canonical = f"https://{domain}/articles/{noext}"

    # WebMCPコメント（言語対応）
    webmcp_comment = "<!-- WebMCP: make this site's content discoverable and usable by AI agents -->" if lang == "en" else "<!-- WebMCP: エージェントがこのサイトのコンテンツを発見・利用できるようにする -->"

    html = f'''<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} | {site['name']}</title>
<meta name="description" content="{a.get('description','')}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{a.get('description','')}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{site['name']}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{jsonld}</script>
{f'<script type="application/ld+json">{faq_json}</script>' if faq_json else ''}
{webmcp_comment}
<script type="module" src="/.webmcp/bridge.js" data-packs="mcp-server-client"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans JP','Hiragino Sans',sans-serif;font-size:18px;line-height:1.9;background:#f7f4ef;color:#2b2b2b}}
a{{color:#1a6b3c}}
h1{{font-size:26px;margin:20px 0;color:#1a6b3c}}
h2{{font-size:22px;margin:30px 0 15px;color:#1a6b3c;border-bottom:2px solid #1a6b3c;padding-bottom:8px}}
h3{{font-size:20px;margin:20px 0 10px;color:#1a6b3c}}
p{{margin-bottom:16px}}
.article-body{{background:#fff;padding:30px;border-radius:12px;max-width:860px;margin:0 auto;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.date{{color:#666;font-size:14px;margin-bottom:10px}}
table{{width:100%;border-collapse:collapse;margin:15px 0}}
th,td{{border:1px solid #ddd;padding:10px;text-align:left}}
th{{background:#e8f5e9}}
.site-header{{background:#1a6b3c;color:#fff;padding:30px 20px;text-align:center}}
.site-header h1{{color:#fff;font-size:26px}}
.site-header p{{color:#e8f5e9;font-size:15px}}
.site-footer{{background:#123a23;color:#c8e6c9;text-align:center;padding:30px 20px;margin-top:40px;font-size:14px}}
@media(max-width:600px){{body{{font-size:17px}}.article-body{{padding:20px}}}}
</style>
</head>
<body>
<header class="site-header">
<h1>{site['name']}</h1>
<p>{site['description']}</p>
</header>
<main class="article-body">
<p class="date">Published: {date[:10]}</p>
{body}
</main>
<footer class="site-footer">
<p>© 2026 {site['name']} | {disclaimer}</p>
<p style="margin-top:10px;font-size:13px;color:#a5d6a7">{affiliate_note}</p>
</footer>
</body>
</html>'''
    return html

def build_author_page(site, articles):
    """著者ページを生成（著者リンクの受け皿・信頼とリンク獲得）"""
    lang = site.get("lang", "ja")
    domain = site["domain"]
    name = site["name"]
    if lang == "en":
        title = "About the Author | Agentic Guides Editorial Team"
        body = f"""<h1>About the Author</h1>
<p>The <strong>Agentic Guides Editorial Team</strong> researches and publishes practical guides on {name.lower()} topics. Our team focuses on providing accurate, up-to-date, and clearly sourced information to help readers make informed decisions.</p>
<h2>What We Cover</h2>
<p>We publish guides on {name.lower()}, covering the topics readers ask about most. Each article is written to be clear, factual, and useful, with a focus on helping readers understand their options.</p>
<h2>Our Approach</h2>
<p>We prioritize accuracy and transparency. Every article includes a clear disclaimer that it provides general information, not professional advice. We encourage readers to verify details with official sources and consult qualified professionals for their specific situations.</p>
<h2>Published Articles</h2>
<ul>"""
        for a in articles:
            noext = _noext(a["file"])
            body += f'<li><a href="/articles/{noext}">{a["title"]}</a></li>'
        body += "</ul>"
    else:
        title = "著者について | Agentic Guides編集部"
        body = f"""<h1>著者について</h1>
<p><strong>Agentic Guides編集部</strong>は、{name}に関する実用的なガイドを調査・公開しています。正確で最新の情報を、明確な出典とともに提供することを目指しています。</p>
<h2>取り扱うテーマ</h2>
<p>{name}に関する、読者が最もよく尋ねるテーマを扱っています。各記事は明確で事実に基づき、読者が選択肢を理解するのに役立つよう書かれています。</p>
<h2>編集方針</h2>
<p>正確性と透明性を重視しています。すべての記事に「一般的な情報提供であり、専門的助言ではない」という免責を明記しています。詳細は公式情報で確認し、具体的な判断は専門家に相談するよう推奨しています。</p>
<h2>公開記事</h2>
<ul>"""
        for a in articles:
            noext = _noext(a["file"])
            body += f'<li><a href="/articles/{noext}">{a["title"]}</a></li>'
        body += "</ul>"
    return f"""<!DOCTYPE html>
<html lang="{'en' if lang=='en' else 'ja'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://{domain}/author">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Person","name":"Agentic Guides Editorial Team","url":"https://{domain}/author"}}</script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans JP','Hiragino Sans',sans-serif;font-size:18px;line-height:1.9;background:#f7f4ef;color:#2b2b2b}}
a{{color:#1a6b3c}}
h1{{font-size:26px;margin:20px 0;color:#1a6b3c}}
h2{{font-size:22px;margin:30px 0 15px;color:#1a6b3c;border-bottom:2px solid #1a6b3c;padding-bottom:8px}}
p{{margin-bottom:16px}}
ul{{margin:0 0 20px 20px}}
li{{margin-bottom:8px}}
.article-body{{background:#fff;padding:30px;border-radius:12px;max-width:860px;margin:0 auto;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.site-header{{background:#1a6b3c;color:#fff;padding:30px 20px;text-align:center}}
.site-header h1{{color:#fff;font-size:26px}}
.site-footer{{background:#123a23;color:#c8e6c9;text-align:center;padding:30px 20px;margin-top:40px;font-size:14px}}
</style>
</head>
<body>
<header class="site-header"><h1>{site['name']}</h1></header>
<main class="article-body">{body}</main>
<footer class="site-footer"><p>© 2026 {site['name']}</p></footer>
</body>
</html>"""

def build_statistics_page(site, articles):
    """統計ページを生成（リンク獲得のためのオリジナル統計・実データ反映）"""
    lang = site.get("lang", "ja")
    domain = site["domain"]
    name = site["name"]
    n = len(articles)

    # カテゴリ分布を集計
    cats = {}
    for a in articles:
        c = a.get("category", "Uncategorized" if lang == "en" else "未分類")
        cats[c] = cats.get(c, 0) + 1

    # 更新日（最新記事の日付）
    dates = [a.get("date", "") for a in articles if a.get("date")]
    latest = max(dates) if dates else datetime.now().strftime("%Y-%m-%d")

    if lang == "en":
        title = f"Statistics: {name} Coverage & Research"
        # カテゴリ分布テーブル
        cat_rows = "".join(
            f"<tr><td>{c}</td><td>{cnt}</td><td>{round(cnt/n*100)}%</td></tr>"
            for c, cnt in sorted(cats.items(), key=lambda x: -x[1])
        )
        # 記事一覧
        art_list = "".join(
            f'<li><a href="/articles/{_noext(a["file"])}">{a["title"]}</a></li>'
            for a in articles
        )
        body = f"""<h1>Statistics & Research</h1>
<p>This page shares original statistics about our coverage of {name.lower()} topics. We publish this data to help readers and researchers understand the landscape.</p>
<h2>Our Coverage</h2>
<p>As of {datetime.now().strftime('%B %Y')}, we have published <strong>{n} articles</strong> covering the most important {name.lower()} topics. Each article is written to be clear, factual, and useful.</p>
<h2>Coverage by Category</h2>
<table>
<tr><th>Category</th><th>Articles</th><th>Share</th></tr>
{cat_rows}
</table>
<h2>Methodology</h2>
<p>We track the topics readers ask about most and prioritize coverage accordingly. Our articles are reviewed for accuracy and updated as information changes. This page is updated automatically as our coverage grows.</p>
<h2>All Published Articles</h2>
<ul>{art_list}</ul>
<h2>Update History</h2>
<p>Last updated: {latest}</p>
<p><em>This data is provided for general information and reflects our own coverage. It is not professional advice.</em></p>"""
    else:
        title = f"統計: {name}のカバー状況と調査"
        cat_rows = "".join(
            f"<tr><td>{c}</td><td>{cnt}</td><td>{round(cnt/n*100)}%</td></tr>"
            for c, cnt in sorted(cats.items(), key=lambda x: -x[1])
        )
        art_list = "".join(
            f'<li><a href="/articles/{_noext(a["file"])}">{a["title"]}</a></li>'
            for a in articles
        )
        body = f"""<h1>統計と調査</h1>
<p>このページでは、{name}に関する当サイトのカバー状況の統計を公開しています。読者や研究者が状況を理解するのに役立つデータを提供します。</p>
<h2>当サイトのカバー状況</h2>
<p>{datetime.now().strftime('%Y年%m月')}時点で、{name}に関する重要なテーマを<strong>{n}記事</strong>でカバーしています。各記事は明確で事実に基づき、役立つ内容を目指しています。</p>
<h2>カテゴリ別カバー状況</h2>
<table>
<tr><th>カテゴリ</th><th>記事数</th><th>割合</th></tr>
{cat_rows}
</table>
<h2>調査方法</h2>
<p>読者が最もよく尋ねるテーマを追跡し、それに応じてカバーを優先しています。記事は正確性を確認し、情報が変わったら更新しています。このページはカバーが増えるにつれて自動更新されます。</p>
<h2>公開記事一覧</h2>
<ul>{art_list}</ul>
<h2>更新履歴</h2>
<p>最終更新: {latest}</p>
<p><em>このデータは一般的な情報提供のためであり、当サイト自身のカバー状況を反映しています。専門的助言ではありません。</em></p>"""
    return f"""<!DOCTYPE html>
<html lang="{'en' if lang=='en' else 'ja'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://{domain}/statistics">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans JP','Hiragino Sans',sans-serif;font-size:18px;line-height:1.9;background:#f7f4ef;color:#2b2b2b}}
a{{color:#1a6b3c}}
h1{{font-size:26px;margin:20px 0;color:#1a6b3c}}
h2{{font-size:22px;margin:30px 0 15px;color:#1a6b3c;border-bottom:2px solid #1a6b3c;padding-bottom:8px}}
p{{margin-bottom:16px}}
ul{{margin:0 0 20px 20px}}
li{{margin-bottom:8px}}
table{{width:100%;border-collapse:collapse;margin:15px 0}}
th,td{{border:1px solid #ddd;padding:10px;text-align:left}}
th{{background:#e8f5e9}}
.article-body{{background:#fff;padding:30px;border-radius:12px;max-width:860px;margin:0 auto;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.site-header{{background:#1a6b3c;color:#fff;padding:30px 20px;text-align:center}}
.site-header h1{{color:#fff;font-size:26px}}
.site-footer{{background:#123a23;color:#c8e6c9;text-align:center;padding:30px 20px;margin-top:40px;font-size:14px}}
</style>
</head>
<body>
<header class="site-header"><h1>{site['name']}</h1></header>
<main class="article-body">{body}</main>
<footer class="site-footer"><p>© 2026 {site['name']}</p></footer>
</body>
</html>"""

def build_robots(site):
    """AIエージェントがクロールできるよう robots.txt を生成"""
    return f'''User-agent: *
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
'''

def build_legal_pages(site):
    """Privacy Policy / Terms of Service / Cookie Policy を生成（米国向け必須）"""
    lang = site.get("lang", "ja")
    domain = site["domain"]
    name = site["name"]

    if lang == "en":
        privacy = f"""# Privacy Policy

**Last updated:** {datetime.now().strftime("%B %d, %Y")}

{name} ("we", "us", or "our") operates the website at https://{domain}/ (the "Site"). This Privacy Policy explains how we collect, use, and protect information.

## Information We Collect
- **Log data:** When you visit the Site, our servers may automatically log standard information such as your IP address, browser type, and pages visited.
- **Cookies:** We may use cookies to improve your experience and analyze traffic.
- **Affiliate data:** We participate in affiliate programs (including Amazon Associates). When you click an affiliate link, the affiliate network may set cookies to track the referral.

## How We Use Information
We use information to operate the Site, understand usage, and improve content. We do not sell personal information.

## Third-Party Services
We may use analytics and advertising services (such as Google AdSense) that collect data subject to their own privacy policies.

## Your Rights
Depending on your location (e.g., California under CCPA), you may have rights to access, correct, or delete your personal information.

## Contact
For privacy questions, contact us through the Site.

*This policy is provided for general information and does not constitute legal advice.*
"""
        terms = f"""# Terms of Service

**Last updated:** {datetime.now().strftime("%B %d, %Y")}

## Acceptance of Terms
By accessing https://{domain}/ (the "Site"), you agree to these Terms of Service.

## Informational Content Only
The content on this Site is provided for general informational purposes only. It does not constitute professional legal, tax, medical, financial, or other professional advice. You should not rely on this information as a substitute for consultation with qualified professionals.

## No Professional Relationship
Your use of this Site does not create a professional-client relationship between you and {name}.

## Affiliate Disclosure
This Site may contain affiliate links. We may earn a commission from purchases made through these links at no additional cost to you.

## Limitation of Liability
To the fullest extent permitted by law, {name} shall not be liable for any damages arising from your use of, or reliance on, the content on this Site.

## Changes
We may update these Terms at any time. Continued use of the Site constitutes acceptance of the updated Terms.

*These Terms are provided for general information and do not constitute legal advice.*
"""
        cookie = f"""# Cookie Policy

**Last updated:** {datetime.now().strftime("%B %d, %Y")}

## What Are Cookies?
Cookies are small text files stored on your device when you visit a website.

## How We Use Cookies
- **Essential cookies:** Required for the Site to function.
- **Analytics cookies:** Help us understand how visitors use the Site.
- **Advertising cookies:** Used by third-party ad networks (e.g., Google AdSense) to serve relevant ads.

## Managing Cookies
You can control or delete cookies through your browser settings. Disabling cookies may affect Site functionality.

## Third-Party Cookies
We use third-party services (Google AdSense, affiliate networks) that may set their own cookies. Please review their privacy policies.

*This policy is provided for general information and does not constitute legal advice.*
"""
    else:
        privacy = f"""# プライバシーポリシー

**最終更新日:** {datetime.now().strftime("%Y年%m月%d日")}

{name}（以下「当サイト」）は、https://{domain}/（以下「本サイト」）における個人情報の取り扱いについて、以下のとおり定めます。

## 収集する情報
- **ログデータ:** 本サイト訪問時に、IPアドレス・ブラウザ種別・閲覧ページなどの標準的な情報を自動記録する場合があります。
- **Cookie:** 利便性向上とアクセス解析のため、Cookieを使用する場合があります。
- **アフィリエイト:** 当サイトはアフィリエイトプログラム（Amazonアソシエイト等）に参加しており、リンク経由の購入時にアフィリエイトネットワークがCookieを設定する場合があります。

## 情報の利用目的
本サイトの運営・改善、利用状況の把握に利用します。個人情報を第三者に販売することはありません。

## 第三者サービス
アクセス解析・広告配信（Google AdSense等）のため、第三者のサービスを利用する場合があります。各サービスのプライバシーポリシーに従います。

## お問い合わせ
プライバシーに関するお問い合わせは、本サイトを通じてご連絡ください。

*本ポリシーは一般的な情報提供を目的としており、法的助言を提供するものではありません。*
"""
        terms = f"""# 利用規約

**最終更新日:** {datetime.now().strftime("%Y年%m月%d日")}

## 規約への同意
https://{domain}/（以下「本サイト」）を利用することで、本利用規約に同意したものとみなされます。

## 情報提供のみを目的とする
本サイトの内容は、一般的な情報提供のみを目的としています。法律・税務・医療・金融等の専門的助言を提供するものではありません。専門的な判断が必要な場合は、必ず資格を持つ専門家にご相談ください。

## 専門家との関係
本サイトの利用によって、当サイトと利用者との間に専門家・依頼者関係は成立しません。

## アフィリエイト開示
本サイトにはアフィリエイト広告が含まれる場合があります。リンク経由の購入により、当サイトに収益が発生することがあります。

## 免責事項
法律で許容される範囲で、当サイトは、本サイトの内容の利用・依存によって生じたいかなる損害についても責任を負いません。

## 規約の変更
本規約は予告なく変更される場合があります。変更後の利用は、変更後の規約に同意したものとみなされます。

*本規約は一般的な情報提供を目的としており、法的助言を提供するものではありません。*
"""
        cookie = f"""# Cookieポリシー

**最終更新日:** {datetime.now().strftime("%Y年%m月%d日")}

## Cookieとは
Cookieは、ウェブサイト訪問時に端末に保存される小さなテキストファイルです。

## Cookieの利用目的
- **必須Cookie:** 本サイトの機能に必要なもの
- **解析Cookie:** 訪問状況の把握・改善のため
- **広告Cookie:** 第三者広告ネットワーク（Google AdSense等）が関連広告を配信するため

## Cookieの管理
ブラウザの設定からCookieを制御・削除できます。無効化すると本サイトの機能に影響が出る場合があります。

## 第三者Cookie
当サイトは第三者サービス（Google AdSense、アフィリエイトネットワーク等）を利用しており、各サービスが独自のCookieを設定する場合があります。

*本ポリシーは一般的な情報提供を目的としており、法的助言を提供するものではありません。*
"""

    return {
        "privacy": privacy,
        "terms": terms,
        "cookie": cookie,
    }

def build_content_signals(site):
    """Content Signals（AI学習・利用の許可を明示）"""
    return f'''# Content Signals: AIエージェントにコンテンツ利用を明示
# 学習より、検索・参照・引用を許可する（エージェントが読めるように）
https://{site['domain']}/ : allow-agent-access
'''

def build_sitemap(site, articles):
    urls = f'<url><loc>https://{site["domain"]}/</loc><lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
    for a in articles:
        noext = _noext(a["file"])
        enc = quote(noext, safe="")
        urls += f'<url><loc>https://{site["domain"]}/articles/{enc}</loc><lastmod>{a.get("date","")[:10]}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n'
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>'''

def write_site_files(slug, articles, lang="ja"):
    """サイトの全ファイルを書き出す（index, 記事, robots, sitemap, Content Signals, 法的ページ）"""
    site = get_site(slug, lang=lang)
    d = site_dir(slug)
    os.makedirs(os.path.join(d, "articles"), exist_ok=True)

    # 記事HTML
    for a in articles:
        html = build_article_html(site, a, all_articles=articles)
        filepath = os.path.join(d, "articles", a["file"])
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

    # 著者ページ（author.html）
    author_html = build_author_page(site, articles)
    with open(os.path.join(d, "author.html"), "w", encoding="utf-8") as f:
        f.write(author_html)

    # 統計ページ（statistics.html）
    stats_html = build_statistics_page(site, articles)
    with open(os.path.join(d, "statistics.html"), "w", encoding="utf-8") as f:
        f.write(stats_html)

    # 記事一覧(index.html)
    index_html = build_index_html(site, articles)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # robots.txt
    with open(os.path.join(d, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(build_robots(site))

    # Content Signals
    with open(os.path.join(d, "contentsignals.txt"), "w", encoding="utf-8") as f:
        f.write(build_content_signals(site))

    # 法的ページ（Privacy Policy / Terms / Cookie）
    legal = build_legal_pages(site)
    legal_files = {
        "privacy.html": legal["privacy"],
        "terms.html": legal["terms"],
        "cookie.html": legal["cookie"],
    }
    for fname, content in legal_files.items():
        with open(os.path.join(d, fname), "w", encoding="utf-8") as f:
            f.write(content)

    # sitemap.xml
    with open(os.path.join(d, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap(site, articles))

    return len(articles)

def build_index_html(site, articles):
    """記事一覧ページ（AEO最適化）"""
    cards = ""
    for a in sorted(articles, key=lambda x: x.get("date",""), reverse=True):
        noext = _noext(a["file"])
        cards += f'<a href="articles/{noext}" class="card"><h2>{a["title"]}</h2><p>{a.get("description","")}</p></a>\n'
    lang = site.get("lang", "ja")
    html_lang = "en" if lang == "en" else "ja"
    footer_note = "This site provides general information for reference purposes only and does not constitute professional advice. Always verify with official sources." if lang == "en" else "情報は参考程度にご利用ください。詳細は公式サイト・専門家にご確認ください。"
    webmcp_comment = "<!-- WebMCP: make this site's content discoverable and usable by AI agents -->" if lang == "en" else "<!-- WebMCP: エージェントがこのサイトのコンテンツを発見・利用できるようにする -->"
    return f'''<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{site['name']} | {site['description']}</title>
<meta name="description" content="{site['description']}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://{site['domain']}/">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":{json.dumps(site['name'])},"url":"https://{site['domain']}/","description":{json.dumps(site['description'])}}}</script>
{webmcp_comment}
<script type="module" src="/.webmcp/bridge.js" data-packs="mcp-server-client"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans JP',sans-serif;font-size:18px;line-height:1.9;background:#f7f4ef;color:#2b2b2b}}
a{{color:#1a6b3c;text-decoration:none}}
.site-header{{background:#1a6b3c;color:#fff;padding:50px 20px;text-align:center}}
.site-header h1{{color:#fff;font-size:30px}}
.site-header p{{color:#e8f5e9;margin-top:8px;font-size:16px;max-width:720px;margin-left:auto;margin-right:auto}}
.cards{{max-width:860px;margin:30px auto;padding:0 20px}}
.card{{display:block;background:#fff;border-radius:12px;padding:20px;margin-bottom:15px;box-shadow:0 2px 8px rgba(0,0,0,.08);border-left:5px solid #1a6b3c}}
.card h2{{font-size:19px;color:#1a6b3c;margin-bottom:6px}}
.card p{{font-size:15px;color:#666}}
.site-footer{{background:#123a23;color:#c8e6c9;text-align:center;padding:30px 20px;margin-top:40px;font-size:14px}}
</style>
</head>
<body>
<header class="site-header">
<h1>{site['name']}</h1>
<p>{site['description']}</p>
</header>
<main class="cards">
{cards}
</main>
<footer class="site-footer">
<p>© 2026 {site['name']} | {footer_note}</p>
</footer>
</body>
</html>'''
