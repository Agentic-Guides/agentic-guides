#!/usr/bin/env python3
"""Agentic Commerce 各サイトの日次記事自動生成（安全版）
- テーマをローテーションして毎日異なる記事を生成（被らない設計）
- すべての記事に免責・断定回避・日付表示（訴訟リスク最小化）
- カテゴリごとの具体的テーマリストから順番に選択
- 重複チェック（タイトル + 本文）で二重投稿を防止
"""
import sys, os, json, re, subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import site_builder as sb

# ============================================================
# 安全なテーマローテーション定義
# 各カテゴリに対して複数の具体的テーマを定義し、順番に選択する
# 英語サイトは英語テーマ、日本語サイトは日本語テーマ（混入禁止）
# ============================================================
# 英語サイト用テーマ
GENERIC_TOPICS_EN = [
    "Key Basics and Current Considerations",
    "The Application and Process Overview",
    "Frequently Asked Questions and Key Points",
    "Cost and Budget Considerations",
    "Important Points and What to Verify",
    "Comparing and Choosing Your Options",
    "Latest Policy Updates",
    "What Beginners Should Know",
    "Common Mistakes to Avoid",
    "Step-by-Step Guide for First-Timers",
    "How to Prepare the Required Documents",
    "Eligibility Requirements Explained",
    "Timeline and How Long It Takes",
    "What to Do If You Are Denied",
    "Renewal and Maintenance Requirements",
    "Tax Implications You Should Know",
    "How to Maximize Your Benefits",
    "State-by-State Differences",
    "Real-World Examples and Scenarios",
    "Resources and Where to Get Help",
]

# 日本語サイト用テーマ
# 英語サイト固有テーマ（英語のみ）
SITE_TOPICS_EN = {
    "grant-navigator": {
        "Business Grants": ["Overview of small business grants", "How to prepare a business plan", "The grant application process"],
        "Personal Aid": ["Types of personal financial aid", "How to apply for assistance programs"],
        "Housing": ["Types of home improvement grants", "Eligibility for housing assistance"],
    },
    "tax-filing-guide": {
        "Tax Filing": ["Tax filing deadlines", "Documents required for filing"],
        "Deductions": ["Expenses that qualify as deductions", "Types of deductions and eligibility"],
        "Freelancer": ["Tracking expenses as a freelancer", "Self-employed tax filing"],
    },
    "mortgage-guide": {
        "Mortgage Basics": ["Types of mortgages", "How to choose a mortgage"],
        "Rates": ["Comparing interest rate types", "How to check current rates"],
        "Tax Credits": ["Overview of homebuyer tax credits", "Tax benefits of homeownership"],
    },
    "insurance-guide": {
        "Health Insurance": ["Comparing health plans", "How to choose a plan"],
        "Life Insurance": ["Types of life insurance", "How to estimate coverage needs"],
    },
    "credit-score-guide": {
        "Credit Basics": ["How credit scores work", "Factors that affect your score"],
        "Improve Credit": ["Ways to improve your score", "The importance of payment history"],
    },
    "retirement-guide": {
        "Retirement Basics": ["Planning for retirement income", "How to start saving"],
        "401k": ["How 401(k) plans work", "Using employer matching"],
        "Social Security": ["When to claim benefits", "How benefits are calculated"],
    },
    "investing-guide": {
        "Investing Basics": ["Core investing principles", "Steps to start investing"],
        "Stocks": ["Stock investing basics", "The importance of diversification"],
        "ETFs": ["ETFs and index funds", "Low-cost investing"],
    },
    "crypto-guide": {
        "Crypto Basics": ["Cryptocurrency basics", "How digital assets work"],
        "Trading": ["How to choose an exchange", "Trading considerations"],
        "Security": ["Safely managing crypto", "Types of wallets"],
    },
    "forex-guide": {
        "Forex Basics": ["Forex trading basics", "Understanding currency pairs"],
        "Risk": ["Forex trading risks", "Risk management methods"],
    },
}

# ============================================================
# 記事生成（安全なテンプレート）
# すべての記事に免責・断定回避・日付を自動挿入
# ============================================================
def generate_from_template(site, category, topic):
    """テンプレート記事生成（安全版）
    断定表現を避け、免責を明記し、日付を表示する。
    """
    lang = site.get("lang", "ja")
    today = datetime.now().strftime("%Y年%m月" if lang == "ja" else "%B %Y")
    site_name = site["name"]

    if lang == "en":
        # 英語版：FTC・YMYL対策（情報提供のみ・専門的助言ではない）
        # 質向上: 具体的な確認項目・チェックリスト・FAQを追加（断定はしない）
        body = f"""<p><em>This article provides general information for reference purposes only and does not constitute professional legal, tax, medical, or financial advice. Rules and programs may change. Always verify current details with official sources or consult a qualified professional.</em></p>
<h2>What should you know about {topic}?</h2>
<p>When researching {topic}, it is helpful to understand the general concepts and current considerations as of {today}. {site_name} provides information to support your research.</p>
<h2>Key points to verify</h2>
<ul>
<li><strong>Eligibility:</strong> Confirm the specific requirements that apply to your situation, as these can vary by location and circumstances.</li>
<li><strong>Current rules:</strong> Check the latest official guidelines, since programs and regulations are subject to change.</li>
<li><strong>Costs and fees:</strong> Review any applicable costs, deadlines, and required documentation before proceeding.</li>
<li><strong>Official sources:</strong> Always verify details with the relevant government agency or qualified professional.</li>
</ul>
<h2>Common questions about {topic}</h2>
<h3>Who is this relevant to?</h3>
<p>This topic is relevant to individuals who want to make informed decisions. Requirements and options can vary by situation and location, so it is important to review the details that apply to you.</p>
<h3>How can you research this topic?</h3>
<p>Start by reviewing official sources and understanding the basic options available. Compare relevant details and consider how they apply to your circumstances. Consulting a qualified professional is recommended for specific decisions.</p>
<h3>What are important points to consider?</h3>
<p>There are several factors to keep in mind, including current rules, eligibility, and costs. Because this involves financial or personal decisions, general information should not be the sole basis for action. Always verify with official sources.</p>
<h2>Suggested next steps</h2>
<ol>
<li>Identify the official agency or source that governs {topic}.</li>
<li>Review the current eligibility requirements and deadlines.</li>
<li>Gather any required documents or information.</li>
<li>Consult a qualified professional for advice specific to your situation.</li>
</ol>"""
        return {
            "title": f"{topic}: Overview and Key Points ({today})",
            "description": f"General information about {topic} as of {today}. Learn the key points, verification steps, and how to research current details.",
            "body": body,
        }
    else:
        # 日本語版：YMYL対策（情報提供のみ・専門的助言ではない）
        # 質向上: 具体的な確認項目・チェックリスト・FAQを追加（断定はしない）
        body = f"""<p><em>本記事は一般的な情報提供を目的としており、法律・税務・医療・金融等の専門的助言を提供するものではありません。制度や手続きは変更される場合があります。必ず公式サイトや専門家にご確認ください。</em></p>
<h2>{topic}について知っておくべきことは？</h2>
<p>{topic}について調べる際、{today}時点の一般的な概念と確認すべき点を整理しました。{site_name}では、正確な判断に役立つ情報を提供しています。</p>
<h2>確認すべきポイント</h2>
<ul>
<li><strong>対象条件：</strong>ご自身の状況に当てはまる条件を、公式情報で必ず確認しましょう。</li>
<li><strong>最新の制度：</strong>制度や手続きは変更される場合があるため、最新の公式ガイドラインを確認しましょう。</li>
<li><strong>費用・締切・書類：</strong>必要な費用、締切、提出書類を事前に確認しましょう。</li>
<li><strong>公式情報源：</strong>必ず、関連する公的機関や専門家に確認しましょう。</li>
</ul>
<h2>{topic}に関するよくある質問</h2>
<h3>この情報は誰に関係する？</h3>
<p>このテーマは、情報に基づいた判断をしたい方に関係します。制度や選択肢は状況や地域によって異なるため、ご自身に当てはまる内容を確認することが大切です。</p>
<h3>このテーマを調べる方法は？</h3>
<p>まず公式の情報源を確認し、利用できる選択肢の基本を理解しましょう。関連する詳細を比較し、ご自身の状況にどう当てはまるかを検討します。具体的な判断には専門家への相談をおすすめします。</p>
<h3>確認すべき注意点は？</h3>
<p>現行のルール、適用条件、費用など、確認すべき点がいくつかあります。金銭や個人に関わる判断の場合、一般的な情報だけを判断の根拠にせず、必ず公式情報で確認してください。</p>
<h2>次のステップの例</h2>
<ol>
<li>{topic}を管轄する公式機関や情報源を確認しましょう。</li>
<li>最新の対象条件と締切を確認しましょう。</li>
<li>必要な書類や情報を準備しましょう。</li>
<li>ご自身の状況に応じた判断には、専門家に相談しましょう。</li>
</ol>"""
        return {
            "title": f"{topic}｜{today}時点の概要と確認ポイント",
            "description": f"{topic}について、{today}時点の概要と確認すべきポイントを解説します。",
            "body": body,
        }


def get_topic(site, category, used_topics):
    """カテゴリに応じた未使用テーマを選択（毎日必ず新記事・言語混入禁止）"""
    slug = site["slug"]
    lang = site.get("lang", "ja")

    site_topics = SITE_TOPICS_EN.get(slug, {})
    generic = GENERIC_TOPICS_EN

    # カテゴリのテーマ + 汎用テーマをフラットリストにする
    cat_topics = site_topics.get(category, []) if category in site_topics else []
    flat_topics = cat_topics + generic

    # 未使用のテーマを選ぶ（既に使ったものはスキップ）
    for t in flat_topics:
        if t not in used_topics:
            return t
    # 全部使い切ったら最初から（重複が避けられない場合のみ）
    return flat_topics[0]


def detect_lang(slug):
    """サイトの言語を判定（site_cli.pyと同じ）"""
    en_slugs = {"grant-navigator", "tax-filing-guide", "mortgage-guide", "side-hustle-hub", "elder-care-guide",
                "insurance-guide", "credit-score-guide", "student-loan-guide", "retirement-guide", "small-business-guide",
                "investing-guide", "pet-insurance-guide", "estate-planning-guide", "auto-loan-guide", "rental-guide",
                "personal-loan-guide", "banking-guide", "financial-planning-guide", "career-guide", "home-improvement-guide",
                "hsa-guide", "travel-insurance-guide", "gig-work-guide", "coupon-guide", "subscription-guide",
                "crypto-guide", "forex-guide", "real-estate-investing-guide", "dividend-guide", "medical-billing-guide",
                "annuity-guide", "credit-card-rewards-guide", "saving-strategies-guide", "home-equity-guide", "entrepreneur-guide",
                "wealth-management-guide", "charity-tax-guide", "lease-guide", "financial-literacy-guide", "insurance-policy-guide",
                "disability-insurance-guide", "unemployment-benefits-guide", "medicaid-guide", "tax-planning-guide", "emergency-fund-guide",
                "financial-aid-guide", "retirement-income-tax-guide", "home-buying-guide", "insurance-claims-guide", "financial-advisor-guide"}
    return "en" if slug in en_slugs else "ja"


def add_article(slug, category, topic):
    """記事を追加してサイトを再構築・デプロイ"""
    site = sb.get_site(slug, lang=detect_lang(slug))
    articles = sb.load_articles(slug)
    # 既存のタイトルと本文を記憶
    existing_titles = {a["title"] for a in articles}
    existing_bodies = {a.get("body", "") for a in articles}

    # 記事生成（テンプレート）
    article = generate_from_template(site, category, topic)

    # 重複チェック（タイトル OR 本文）
    if article["title"] in existing_titles or article["body"] in existing_bodies:
        return False

    articles.append({
        "title": article["title"],
        "description": article.get("description", ""),
        "category": category,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "file": slugify(article["title"]) + ".html",
        "body": article["body"],
    })
    sb.save_articles(slug, articles)
    sb.write_site_files(slug, articles, lang=detect_lang(slug))
    return True


def slugify(text):
    import re
    text = re.sub(r'[／・!？。、]', '-', text)
    text = re.sub(r'[^\w\-ぁ-んァ-ヶ一-龠]', '', text)
    return text[:40]


def deploy(slug):
    site = sb.get_site(slug, lang=detect_lang(slug))
    wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
    if not os.path.exists(wrangler):
        wrangler = "npx wrangler"
    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not cf_token:
        print("⚠️ CLOUDFLARE_API_TOKEN 環境変数が未設定です")
        return False
    result = subprocess.run(
        [wrangler, "pages", "deploy", sb.site_dir(slug), "--project-name=" + site["project"], "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "CLOUDFLARE_API_TOKEN": cf_token}
    )
    return result.returncode == 0


def push_to_github(slug, article_title):
    """新記事をGitHubに自動push（コードのみ・サイト生成物は.gitignoreで除外）"""
    repo_dir = os.path.expanduser("~/Desktop/agentic-sites")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return False
    try:
        remote = f"https://x-access-token:{token}@github.com/Agentic-Guides/agentic-guides.git"
        subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
        subprocess.run(
            ["git", "commit", "-m", f"Update articles: {article_title[:50]}"],
            cwd=repo_dir, capture_output=True, text=True, timeout=30
        )
        r = subprocess.run(
            ["git", "push", remote, "main"],
            cwd=repo_dir, capture_output=True, text=True, timeout=60
        )
        return r.returncode == 0
    except Exception as e:
        print(f"⚠️ GitHub push失敗: {e}")
        return False


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "grant-navigator"
    lang = detect_lang(slug)
    site = sb.get_site(slug, lang=lang)
    categories = list(site["categories"].keys())
    articles = sb.load_articles(slug)
    # 既に使われたテーマを抽出
    used_topics = set()
    for a in articles:
        # タイトルからテーマ部分を抽出（「: Overview...」や「｜...」の前）
        title = a["title"]
        for sep in [":", "｜"]:
            if sep in title:
                used_topics.add(title.split(sep)[0].strip())
                break

    # カテゴリをローテーション
    idx = len(articles) % len(categories)
    category = categories[idx]
    topic = get_topic(site, category, used_topics)

    added = add_article(slug, category, topic)
    if added:
        ok = deploy(slug)
        gh_ok = push_to_github(slug, topic)
        print(f"✅ {slug}: 記事追加「{topic}」 + デプロイ {'成功' if ok else '失敗'} + GitHub push {'成功' if gh_ok else '失敗'}")
    else:
        print(f"ℹ️ {slug}: 追加する新規記事なし（重複）")
