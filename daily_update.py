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
]

# 日本語サイト用テーマ
GENERIC_TOPICS_JA = [
    "基本事項と最新の動向",
    "申請・利用の手続きの流れ",
    "よくある質問と確認ポイント",
    "費用・負担の考え方",
    "注意点と確認すべき情報",
    "比較・選択のポイント",
    "制度改正の最新状況",
    "初心者が知っておくべき基礎",
]

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

# 日本語サイト固有テーマ（日本語のみ）
SITE_TOPICS_JA = {
    "hojokin-nav": {
        "事業者向け": ["中小企業向け補助金の概要", "事業計画書の作成ポイント", "補助金申請の流れ"],
        "個人向け": ["個人向け給付金の種類", "生活支援制度の申請方法"],
        "自治体": ["自治体の補助金制度", "地域の助成金の確認方法"],
    },
    "kakutei-guide": {
        "確定申告": ["確定申告の提出期限", "確定申告に必要な書類"],
        "節税": ["節税の基本", "経費として認められるもの"],
        "青色申告": ["青色申告のメリット", "複式簿記の基本"],
    },
    "sumai-loan": {
        "住宅ローン": ["住宅ローンの種類", "住宅ローンの選び方"],
        "金利": ["金利タイプの比較", "金利動向の確認方法"],
        "住宅減税": ["住宅ローン減税の概要", "住宅購入時の税制優遇"],
    },
    "fukugyo-master": {
        "副業入門": ["副業の始め方", "副業を選ぶポイント"],
        "在宅ワーク": ["在宅ワークの種類", "リモートワークの始め方"],
        "確定申告": ["副業の確定申告", "副業の税金の考え方"],
    },
    "kaigo-seido": {
        "介護保険": ["介護保険の基礎", "介護保険の加入者"],
        "要介護認定": ["要介護認定の流れ", "認定調査の内容"],
        "介護費用": ["介護費用の考え方", "負担軽減制度"],
    },
    "sozoku-guide": {
        "相続基礎": ["相続人の範囲", "相続分の考え方"],
        "相続税": ["相続税の基礎控除", "相続税の申告手続き"],
        "遺言書": ["遺言書の種類", "遺言書の書き方"],
    },
    "hoken-guide": {
        "生命保険": ["生命保険の種類", "保障内容の考え方"],
        "医療保険": ["医療保険の保障内容", "入院給付金の考え方"],
        "保険の基礎": ["保険料の仕組み", "保険の用語解説"],
    },
    "rogo-shikin": {
        "老後資金": ["老後資金の必要額", "老後資金の準備方法"],
        "年金": ["公的年金の仕組み", "年金の受給要件"],
        "iDeCo": ["iDeCoの仕組み", "iDeCoの節税効果"],
    },
    "nenkin-guide": {
        "年金基礎": ["公的年金の種類", "年金の加入の仕組み"],
        "受給手続き": ["年金の受給手続き", "必要書類の準備"],
        "国民年金": ["国民年金の保険料", "保険料免除制度"],
    },
    "kosodate-shien": {
        "児童手当": ["児童手当の支給額", "児童手当の申請方法"],
        "保育": ["保育園の入園手続き", "保育料の考え方"],
        "教育資金": ["教育資金の必要額", "学資保険の選び方"],
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
        body = f"""<p><em>This article provides general information for reference purposes only and does not constitute professional legal, tax, medical, or financial advice. Rules and programs may change. Always verify current details with official sources or consult a qualified professional.</em></p>
<h2>What should you know about {topic}?</h2>
<p>When researching {topic}, it is helpful to understand the general concepts and current considerations as of {today}. {site_name} provides information to support your research.</p>
<h2>Who may this information be relevant to?</h2>
<p>This topic is relevant to individuals who want to make informed decisions. Requirements and options can vary by situation and location, so it is important to review the details that apply to you.</p>
<h2>How can you research this topic?</h2>
<p>Start by reviewing official sources and understanding the basic options available. Compare relevant details and consider how they apply to your circumstances. Consulting a qualified professional is recommended for specific decisions.</p>
<h2>What are important points to consider?</h2>
<p>There are several factors to keep in mind, including current rules, eligibility, and costs. Because this involves financial or personal decisions, general information should not be the sole basis for action. Always verify with official sources.</p>"""
        return {
            "title": f"{topic}: Overview and Key Points ({today})",
            "description": f"General information about {topic} as of {today}. Learn the key points and how to verify current details.",
            "body": body,
        }
    else:
        # 日本語版：YMYL対策（情報提供のみ・専門的助言ではない）
        body = f"""<p><em>本記事は一般的な情報提供を目的としており、法律・税務・医療・金融等の専門的助言を提供するものではありません。制度や手続きは変更される場合があります。必ず公式サイトや専門家にご確認ください。</em></p>
<h2>{topic}について知っておくべきことは？</h2>
<p>{topic}について調べる際、{today}時点の一般的な概念と確認すべき点を整理しました。{site_name}では、正確な判断に役立つ情報を提供しています。</p>
<h2>この情報は誰に関係する？</h2>
<p>このテーマは、情報に基づいた判断をしたい方に関係します。制度や選択肢は状況や地域によって異なるため、ご自身に当てはまる内容を確認することが大切です。</p>
<h2>このテーマを調べる方法は？</h2>
<p>まず公式の情報源を確認し、利用できる選択肢の基本を理解しましょう。関連する詳細を比較し、ご自身の状況にどう当てはまるかを検討します。具体的な判断には専門家への相談をおすすめします。</p>
<h2>確認すべき注意点は？</h2>
<p>現行のルール、適用条件、費用など、確認すべき点がいくつかあります。金銭や個人に関わる判断の場合、一般的な情報だけを判断の根拠にせず、必ず公式情報で確認してください。</p>"""
        return {
            "title": f"{topic}｜{today}時点の概要と確認ポイント",
            "description": f"{topic}について、{today}時点の概要と確認すべきポイントを解説します。",
            "body": body,
        }


def get_topic(site, category, used_topics):
    """カテゴリに応じた未使用テーマを選択（毎日必ず新記事・言語混入禁止）"""
    slug = site["slug"]
    lang = site.get("lang", "ja")

    if lang == "en":
        site_topics = SITE_TOPICS_EN.get(slug, {})
        generic = GENERIC_TOPICS_EN
    else:
        site_topics = SITE_TOPICS_JA.get(slug, {})
        generic = GENERIC_TOPICS_JA

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
                "wealth-management-guide", "charity-tax-guide", "lease-guide", "financial-literacy-guide", "insurance-policy-guide"}
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
    slug = sys.argv[1] if len(sys.argv) > 1 else "hojokin-nav"
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
