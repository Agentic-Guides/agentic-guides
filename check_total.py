import re, os

# cronの記事サイト（全英語）
src = open(r'C:/Users/hohoh/AppData/Local/hermes/scripts/agentic_daily_all.py', encoding='utf-8').read()
m = re.search(r'SITES = \[(.*?)\]', src, re.DOTALL)
cron_sites = set(re.findall(r'"([a-z0-9-]+)"', m.group(1)))

os.chdir(r'C:/Users/hohoh/Desktop/agentic-sites')
r = os.popen('npx wrangler pages project list 2>&1').read()
cf_sites = set(re.findall(r'│ ([a-z0-9-]+) +│', r))
cf_dir = {s for s in cf_sites if 'directory' in s}

print("=== 全体の内訳 ===")
print("記事サイト cron対象:", len(cron_sites), "(全英語)")
print("ディレクトリ:", len(cf_dir))
print("合計:", len(cron_sites) + len(cf_dir))
print()
print("記事サイト:", sorted(cron_sites))
