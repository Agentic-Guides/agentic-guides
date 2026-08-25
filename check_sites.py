#!/usr/bin/env python3
"""agentic-sites 内の全サイトの稼働状態を一括チェック（HTTP 200 か否か）"""
import os, subprocess, concurrent.futures

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

dirs = sorted([d for d in os.listdir(BASE) if os.path.isdir(d) and not d.startswith('.') 
               and not d.startswith('__') and (d.endswith('-guide') or d.endswith('-directory') or '-' in d)])
# 候補: 全ディレクトリ

def check(slug):
    url = f"https://{slug}.pages.dev/"
    try:
        r = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","--max-time","6",url],
                          capture_output=True, text=True, timeout=10)
        code = r.stdout.strip()
        return (slug, code)
    except Exception:
        return (slug, "ERR")

# 対象ディレクトリを絞る（agentic-sites はローカルのサイト群）
dirs = [d for d in os.listdir(BASE) if os.path.isdir(d) and not d.startswith('.') and not d.startswith('__')]
# 実行ディレクトリ等を除外
skip = {'mcp','crawler-observer','functions','__pycache__'}
dirs = [d for d in dirs if d not in skip]

print(f"チェック対象: {len(dirs)} サイト")
results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(check, d): d for d in dirs}
    for f in concurrent.futures.as_completed(futs):
        slug = futs[f]
        try:
            slug, code = f.result()
            results[slug] = code
        except Exception:
            results[slug] = "ERR"

alive = sorted([s for s,c in results.items() if c=="200"])
dead = sorted([s for s,c in results.items() if c!="200"])
print(f"\n稼働中(200): {len(alive)}")
print(f"休眠/未デプロイ: {len(dead)}")
print("\n=== 稼働中 ===")
print(", ".join(alive))
print("\n=== 休眠/未デプロイ ===")
print(", ".join(dead))
