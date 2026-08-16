import re, os, subprocess

# cronの60サイトを抽出
src = open(r'C:/Users/hohoh/AppData/Local/hermes/scripts/agentic_daily_all.py', encoding='utf-8').read()
m = re.search(r'SITES = \[(.*?)\]', src, re.DOTALL)
cron_sites = set(re.findall(r'"([a-z0-9-]+)"', m.group(1)))

# Cloudflareの一覧
os.chdir(r'C:/Users/hohoh/Desktop/agentic-sites')
r = os.popen('npx wrangler pages project list 2>&1').read()
cf_sites = set(re.findall(r'│ ([a-z0-9-]+) +│', r))

# 日本語記事サイト
jp10 = {'hojokin-nav','kakutei-guide','sumai-loan','fukugyo-master','kaigo-seido',
        'sozoku-guide','hoken-guide','rogo-shikin','nenkin-guide','kosodate-shien'}

# cron内の英語guide
cron_en = {s for s in cron_sites if s.endswith('-guide') and s not in jp10}
# Cloudflare上の英語guide
cf_en = {s for s in cf_sites if s.endswith('-guide') and s not in jp10}
# ディレクトリ
cf_dir = {s for s in cf_sites if 'directory' in s}

print("=== 検証結果 ===")
print("cron登録:", len(cron_sites), "| 内訳: 英guide", len(cron_en), "+ 日本語", len([s for s in cron_sites if s in jp10]))
print("Cloudflare: 英guide", len(cf_en), "+ 日本語guide系", len([s for s in cf_sites if s in jp10]), "+ ディレクトリ", len(cf_dir))
print()
print("cronに漏れてる英語guide:", cf_en - cron_en if (cf_en - cron_en) else "なし")
print("cronに余分な英語guide:", cron_en - cf_en if (cron_en - cf_en) else "なし")
print("cronの日本語内訳:", sorted([s for s in cron_sites if s in jp10]))
