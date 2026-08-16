import re, os

# cronの60サイト
src = open(r'C:/Users/hohoh/AppData/Local/hermes/scripts/agentic_daily_all.py', encoding='utf-8').read()
m = re.search(r'SITES = \[(.*?)\]', src, re.DOTALL)
cron_sites = set(re.findall(r'"([a-z0-9-]+)"', m.group(1)))

# 日本語記事サイト
jp10 = {'hojokin-nav','kakutei-guide','sumai-loan','fukugyo-master','kaigo-seido',
        'sozoku-guide','hoken-guide','rogo-shikin','nenkin-guide','kosodate-shien'}

# cron内の日本語
cron_jp = [s for s in cron_sites if s in jp10]
# cron内の英語 = cron - 日本語
cron_en = cron_sites - set(cron_jp)

os.chdir(r'C:/Users/hohoh/Desktop/agentic-sites')
r = os.popen('npx wrangler pages project list 2>&1').read()
cf_sites = set(re.findall(r'│ ([a-z0-9-]+) +│', r))
cf_dir = {s for s in cf_sites if 'directory' in s}

print("=== 全体の内訳（77の検証） ===")
print("記事サイト cron対象:", len(cron_sites), "=", len(cron_en), "英語 +", len(cron_jp), "日本語")
print("ディレクトリ:", len(cf_dir))
print("合計:", len(cron_sites) + len(cf_dir))
print()
print("英語記事50:", sorted(cron_en))
