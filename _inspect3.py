content = open(r"C:\Users\hohoh\Desktop\agentic-sites\site_builder.py", encoding="utf-8").read()
# 115行目（記事用 jsonld）を確認
lines = content.split("\n")
line = lines[114]  # 0-indexed 115行目
idx = line.find("jsonld = f")
print("記事jsonld:", line[:120])
# @graphの構造を確認
print("schema.org有無:", "schema.org" in line, "| @graph有無:", "@graph" in line)
