"""Writes downloads/versions.json with the latest stable release of each project.

"Latest" is what GitHub marks as the latest release: drafts and pre-releases (betas) do not count.
Run by .github/workflows/versions.yml; the website reads the file and shows the numbers.
"""
import json
import os
import pathlib
import urllib.request

REPOS = {"smartlists": "m3m0rex/ha_smartlists", "smartdiscounts": "m3m0rex/ha_smartdiscounts-card"}
OUT = pathlib.Path("downloads/versions.json")


def latest(repo: str) -> dict | None:
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "ha-smartlists.com"})
    token = os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
    except Exception as err:  # no stable release yet, or GitHub not reachable: keep what is there
        print(f"{repo}: {err}")
        return None
    return {"version": str(data.get("tag_name", "")).lstrip("v"), "url": data.get("html_url", ""),
            "published": str(data.get("published_at", ""))[:10]}


old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
new = dict(old)
for key, repo in REPOS.items():
    found = latest(repo)
    if found and found["version"]:
        new[key] = found
OUT.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(new, indent=2))
