"""Cloudflare Pages のプロジェクト一覧を実測して、実際にデプロイ済みのサイトを確定する。

★トークンは出力しない。
"""
import json, os, re, subprocess, urllib.request, urllib.error

env = dict(os.environ)
env.pop("CLOUDFLARE_API_TOKEN", None)
subprocess.run(["npx", "wrangler", "whoami"], env=env, capture_output=True, shell=True)

P = os.path.expanduser("~/.wrangler/config/default.toml")
tok = re.search(r'oauth_token\s*=\s*"([^"]+)"', open(P, encoding="utf-8").read()).group(1)
ACC = "c1af587d36d1b6cb2848fc4e5546923d"


def api(path):
    h = {"Authorization": "Bearer " + tok, "Content-Type": "application/json",
         "User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request("https://api.cloudflare.com/client/v4" + path, headers=h)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}
    except Exception as ex:
        return 0, {"_err": str(ex)}


print("=== Cloudflare Pages プロジェクト一覧 ===")
st, r = api("/accounts/%s/pages/projects?per_page=100" % ACC)
if r.get("success"):
    projs = r["result"]
    print("  プロジェクト数:", len(projs))
    for p in projs[:40]:
        sub = p.get("subdomain", "")
        dom = p.get("domains", [])
        print("  %-32s %s  domains=%s" % (p.get("name"), sub, dom[:2]))
else:
    print("  ", st, json.dumps(r)[:250])

print("\n=== 総数（ページング）===")
total = []
for page in range(1, 6):
    st, r = api("/accounts/%s/pages/projects?per_page=100&page=%d" % (ACC, page))
    res = r.get("result") or []
    if not res:
        break
    total.extend(res)
    if len(res) < 100:
        break
print("  合計:", len(total))
subs = sorted(p.get("subdomain", "") for p in total)
print("\n=== サブドメイン一覧（先頭40）===")
for s in subs[:40]:
    print("  ", s)
print("\n=== 一覧をファイルに保存 ===")
out = os.path.expanduser("~/Desktop/agentic-sites/_pages_projects.json")
json.dump([{"name": p.get("name"), "subdomain": p.get("subdomain"),
            "domains": p.get("domains"), "created": p.get("created_on"),
            "latest": (p.get("latest_deployment") or {}).get("created_on")}
           for p in total], open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("  saved:", out)
