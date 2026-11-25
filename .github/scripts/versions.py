"""Writes downloads/versions.json with the latest stable release of each project – SmartLists, SmartDiscounts and
the app SmartLists Go ("smartlists_go", taken from downloads/version.json or downloads/app.json).

"Latest" is what GitHub marks as the latest release: drafts and pre-releases (betas) do not count.
A beta is listed next to it ("beta") while it is newer than the stable release.
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
            "published": str(data.get("published_at", ""))[:10], "published_at": str(data.get("published_at", ""))}


def get(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "ha-smartlists.com"})
    token = os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def newest_beta(repo: str, stable: dict | None) -> dict | None:
    """The most recently published pre-release – only when it came out after the latest stable release."""
    try:
        betas = [r for r in get(f"https://api.github.com/repos/{repo}/releases?per_page=30")
                 if r.get("prerelease") and not r.get("draft") and r.get("published_at")]
    except Exception as err:
        print(f"{repo} (betas): {err}")
        return None
    if not betas:
        return None
    top = max(betas, key=lambda r: r["published_at"])
    if stable and stable.get("published_at", "") >= top["published_at"]:
        return None
    return {"version": str(top.get("tag_name", "")).lstrip("v"), "url": top.get("html_url", ""), "published": top["published_at"][:10]}


old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
new = dict(old)
for key, repo in REPOS.items():
    found = latest(repo)
    beta = newest_beta(repo, found or None)
    entry = dict(new.get(key) or {})
    if found and found["version"]:
        entry.update({k: v for k, v in found.items() if k != "published_at"})
    entry.pop("beta", None)
    if beta and beta["version"]:
        entry["beta"] = beta
    if entry:
        new[key] = entry


def app() -> dict | None:
    """SmartLists Go: the released APK (downloads/version.json) or, before the first release, the version the app
    repository reports (downloads/app.json, android)."""
    def read(name: str) -> dict:
        path = pathlib.Path("downloads") / name
        try:
            return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        except ValueError:
            return {}

    rel, dev = read("version.json"), (read("app.json").get("android") or {})
    if rel.get("version") and str(rel.get("apk", "")).startswith("https://"):
        return {"version": str(rel["version"]), "url": rel["apk"], "published": str(rel.get("released", "")), "released": True}
    if dev.get("version"):
        return {"version": str(dev["version"]), "url": str(dev.get("url") or ""), "published": "", "released": bool(dev.get("published"))}
    return None


if (go := app()) is not None:
    new["smartlists_go"] = go
OUT.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(new, indent=2))
