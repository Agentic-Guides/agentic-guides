import urllib.request, re, json

url = "https://grant-navigator.pages.dev/"
html = urllib.request.urlopen(url, timeout=20).read().decode("utf-8", "ignore")
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
print("デプロイ済みJSON-LD blocks:", len(blocks))
for i, b in enumerate(blocks):
    try:
        json.loads(b)
        print(f"block{i}: VALID")
    except Exception as e:
        print(f"block{i}: INVALID -> {e}")
        print("  内容:", repr(b[:100]))
# 404も確認
try:
    r = urllib.request.urlopen("https://grant-navigator.pages.dev/nonexistent-xyz", timeout=20)
    print("404 check: status", r.status)
except urllib.error.HTTPError as e:
    print("404 check: status", e.code)
