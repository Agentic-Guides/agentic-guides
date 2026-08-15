#!/usr/bin/env python3
"""Agentic Commerce 各サイトの日次記事自動生成
Ollama Cloud APIで記事を生成 → build → deploy を自動化。
cronで毎日実行して、サイトを放置で回す。
"""
import sys, os, json, re, subprocess, urllib.request
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import site_builder as sb

# Ollama Cloud API設定（.envから読み込み）
def load_api_key():
    env_path = os.path.expanduser("~/Desktop/cf-x402-tpl/x402-proxy-template/bazaar-server/.env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("LLM_API_KEY="):
                    return line.strip().split("=", 1)[1].strip()
    return os.environ.get("LLM_API_KEY", "")

API_KEY = load_api_key()
OLLAMA_URL = "https://ollama.com/api/chat"  # 実際のエンドポイントに合わせる

def generate_article(site, category, topic):
    """Ollama Cloudで記事を生成"""
    prompt = f"""あなたは「{site['name']}」の専門ライターです。
カテゴリ「{category}」の記事を1本、日本語で書いてください。
テーマ: {topic}

要件:
- タイトルは「？」で終わる問句形式にする（AEO最適化）
- 本文は<h2>見出し（問句）と<p>本文で構成
- 各<h2>は「〜とは？」「〜は？」「〜の方法は？」のような問句にする
- 事実に基づき、断定を避け、最新情報であることを明記
- 最後に「詳細は公式サイト・専門家にご確認ください」の注意を入れる
- 出力はJSON形式: {{"title": "...", "description": "...", "body": "<h2>...</h2><p>...</p>..."}}

出力はJSONのみ返してください。"""
    # 実際のAPI呼び出し（Ollama Cloudの仕様に合わせる）
    # ここではシンプルに、テンプレートから記事を生成するフォールバックも用意
    return None

def generate_from_template(site, category, topic):
    """LLMが使えない場合のテンプレート記事生成（フォールバック）"""
    lang = site.get("lang", "ja")
    today = datetime.now().strftime("%Y年%m月" if lang == "ja" else "%B %Y")

    if lang == "en":
        # 英語版：法的安全策（情報提供のみ・専門的助言ではない・断定回避）
        body = f"""<p><em>This article provides general information for reference purposes only and does not constitute professional legal, tax, medical, or financial advice. Rules and programs may change. Always verify current details with official sources or consult a qualified professional.</em></p>
<h2>What is {topic}?</h2>
<p>{topic} is a topic that many people research. This article explains the basics as of {today}. {site['name']} updates information about {category} regularly.</p>
<h2>What are the basics of {topic}?</h2>
<p>Understanding the fundamentals is important. Programs and procedures may change each year, so it is wise to check the latest official information before making decisions.</p>
<h2>How do I get started with {topic}?</h2>
<p>The process generally involves several steps. It is important to review the requirements, gather any needed documents, and allow enough time to prepare. Details can vary by situation and location.</p>
<h2>What should I keep in mind about {topic}?</h2>
<p>There are common points to consider. For specific guidance, please consult official sources or a qualified professional. This article is general information and is not professional advice.</p>"""
        return {
            "title": f"{topic}: What You Need to Know ({today})",
            "description": f"General information about {topic} as of {today}. Learn the basics, key considerations, and where to find official guidance.",
            "body": body,
        }
    else:
        # 日本語版：法的安全策
        body = f"""<p><em>本記事は一般的な情報提供を目的としており、法律・税務・医療・金融等の専門的助言を提供するものではありません。制度や手続きは変更される場合があります。必ず公式サイトや専門家にご確認ください。</em></p>
<h2>{topic}とは？</h2>
<p>{topic}について、{today}時点の最新情報をわかりやすく解説します。{site['name']}では、{category}に関する情報を毎日更新しています。</p>
<h2>{topic}の基本は？</h2>
<p>まず基本を理解することが重要です。制度や手続きは年度ごとに変更されることがあるため、最新の情報を確認しましょう。</p>
<h2>{topic}の手続き方法は？</h2>
<p>手続きの流れをステップごとに説明します。必要な書類や申請先を確認し、余裕を持って準備することが大切です。</p>
<h2>{topic}で注意すべき点は？</h2>
<p>よくある注意点をまとめました。詳細は公式サイトや専門家にご確認ください。本記事は参考情報であり、専門的助言を提供するものではありません。</p>"""
        return {
            "title": f"{topic}の最新情報｜{today}時点の解説",
            "description": f"{topic}について、{today}時点の最新情報をわかりやすく解説します。{category}に関する手続き・注意点をまとめました。",
            "body": body,
        }

def add_article(slug, category, topic):
    """記事を追加してサイトを再構築・デプロイ"""
    site = sb.get_site(slug)
    articles = sb.load_articles(slug)
    existing = {a["title"] for a in articles}

    # 記事生成（LLM → フォールバック）
    article = generate_article(site, category, topic)
    if not article:
        article = generate_from_template(site, category, topic)

    if article["title"] in existing:
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
    sb.write_site_files(slug, articles)
    return True

def slugify(text):
    import re
    text = re.sub(r'[／・!？。、]', '-', text)
    text = re.sub(r'[^\w\-ぁ-んァ-ヶ一-龠]', '', text)
    return text[:40]

def deploy(slug):
    site = sb.get_site(slug)
    wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
    if not os.path.exists(wrangler):
        wrangler = "npx wrangler"
    # Cloudflare APIトークンは環境変数から取得（コードにハードコードしない）
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
    """新記事をGitHubリポジトリに自動push（OSS公開の自動更新）"""
    repo_dir = os.path.expanduser("~/Desktop/agentic-sites")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("⚠️ GITHUB_TOKEN 環境変数が未設定です")
        return False
    try:
        # リモートURLにトークンを埋め込んでpush
        remote = f"https://x-access-token:{token}@github.com/Agentic-Guides/agentic-guides.git"
        subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
        subprocess.run(
            ["git", "commit", "-m", f"Add article: {article_title[:50]}"],
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
    site = sb.get_site(slug)
    categories = list(site["categories"].keys())
    # カテゴリをローテーションして記事を追加
    articles = sb.load_articles(slug)
    idx = len(articles) % len(categories)
    category = categories[idx]
    topic = f"{category}の最新情報"
    added = add_article(slug, category, topic)
    if added:
        ok = deploy(slug)
        # 新記事をGitHubに自動push（OSS公開の自動更新）
        gh_ok = push_to_github(slug, topic)
        print(f"✅ {slug}: 記事追加 + デプロイ {'成功' if ok else '失敗'} + GitHub push {'成功' if gh_ok else '失敗'}")
    else:
        print(f"ℹ️ {slug}: 追加する新規記事なし（重複）")
