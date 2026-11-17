#!/usr/bin/env python3
"""Baut Impressum und Datenschutzerklärung (deutsch und englisch) im Aussehen der Startseite.

    python3 build_legal.py

Das Aussehen (der <style>-Block) wird aus index.html übernommen, damit beide Seiten zur Startseite passen.
Geschrieben werden: impressum/, datenschutz/, en/legal-notice/, en/privacy/ (jeweils index.html).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "Julian Schmidt"
ADDRESS = ["c/o Online-Impressum 13167", "Europaring 90", "53757 Sankt Augustin"]
MAIL = "m3m0rex@mail.online-impressum.de"
SECOND = "https://mein.online-impressum.de/m3m0rex/#zweiterkontaktweg"
GITHUB_PRIVACY = "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"

EXTRA = """<style>
  .legal { max-width: 760px; margin: 0 auto; padding: 36px 20px 24px; }
  .legal h1 { font-size: 30px; margin: 0 0 6px; }
  .legal .lead { color: var(--muted); margin: 0 0 26px; }
  .legal h2 { font-size: 18px; margin: 30px 0 8px; }
  .legal p, .legal li { line-height: 1.6; font-size: 15.5px; }
  .legal ul { padding-left: 22px; margin: 8px 0; }
  .legal a { color: var(--link); }
  .legal .box { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; margin: 14px 0; box-shadow: 0 2px 10px var(--shadow); line-height: 1.6; }
  .legal .short { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 16px 0 6px; }
  .legal .short div { background: var(--soft); color: var(--soft-ink); border-radius: 12px; padding: 12px 14px; font-size: 14px; }
  .legal .short b { display: block; margin-bottom: 2px; }
  .legal .back { display: inline-block; margin-bottom: 18px; text-decoration: none; font-size: 14.5px; }
  nav .brand { text-decoration: none; color: inherit; }
  nav .langs a { color: inherit; text-decoration: none; font-weight: 600; font-size: 13.5px; opacity: .75; margin-left: 10px; }
  nav .langs a[aria-current] { opacity: 1; text-decoration: underline; }
  footer .legal-links { margin-top: 10px; } footer .legal-links a { margin: 0 8px; }
</style>"""

WHO = f"{NAME}<br>" + "<br>".join(ADDRESS)

PAGES = {
    "de": {
        "home": "Zurück zur Startseite", "imprint": "Impressum", "privacy": "Datenschutz",
        "tagline": "SmartLists — Einkaufslisten, To-dos und Notizen mit Home Assistant.",
        "unofficial": "Kein offizielles Produkt von Home Assistant oder der Open Home Foundation.",
        "imprint_path": "impressum", "privacy_path": "datenschutz",
        "imprint_body": f"""<h1>Impressum</h1><p class="lead">Angaben gemäß § 5 DDG</p>
<div class="box">m3m0rex — {WHO}</div>
<h2>Kontakt</h2>
<p>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a><br><a href="{SECOND}">Zweiter Kontaktweg</a></p>
<p>Briefe bitte genau so adressieren wie oben angegeben; die Zeile „c/o Online-Impressum 13167“ muss enthalten sein, sonst lässt sich der Brief nicht zuordnen.</p>
<h2>Zuständige Aufsichtsbehörde</h2>
<p>Landesanstalt für Medien Nordrhein-Westfalen · Sitz: Deutschland</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Ich bin nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Hinweis</h2>
<p>SmartLists, SmartDiscounts und SmartLists Go sind private, unentgeltliche Projekte und stehen in keiner Verbindung zu Home Assistant oder der Open Home Foundation.</p>""",
        "privacy_body": f"""<h1>Datenschutzerklärung</h1><p class="lead">Stand: November 2026</p>
<div class="short"><div><b>Keine Cookies</b>Diese Webseite setzt keine Cookies.</div><div><b>Kein Tracking</b>Keine Statistik, keine Werbung, keine eingebundenen Dienste.</div><div><b>Kein Konto</b>Kein Formular, keine Anmeldung, kein Newsletter.</div></div>
<h2>1. Verantwortlicher</h2>
<div class="box">{WHO}<br>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></div>
<h2>2. Aufruf dieser Webseite</h2>
<p>Diese Webseite wird bei GitHub Pages bereitgestellt, einem Dienst der GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA. Beim Aufruf verarbeitet GitHub technisch notwendige Daten, um die Seite auszuliefern und den Dienst abzusichern, insbesondere:</p>
<ul><li>IP-Adresse</li><li>Datum und Uhrzeit des Zugriffs</li><li>aufgerufene Seite und zuvor besuchte Seite</li><li>Browser und Betriebssystem</li></ul>
<p>Ich selbst habe keinen Zugriff auf diese Protokolle und werte sie nicht aus. Rechtsgrundlage ist Art. 6 Abs. 1 Buchst. f DSGVO; das berechtigte Interesse liegt im sicheren und zuverlässigen Betrieb der Webseite.</p>
<p>Dabei können Daten in die USA übermittelt werden. GitHub ist nach eigenen Angaben nach dem EU-US Data Privacy Framework zertifiziert. Einzelheiten stehen in der <a href="{GITHUB_PRIVACY}">Datenschutzerklärung von GitHub</a>.</p>
<h2>3. Speicherung im Browser</h2>
<p>Die Webseite merkt sich die gewählte Sprache im lokalen Speicher deines Browsers. Dieser Wert bleibt auf deinem Gerät, wird nicht an mich übertragen und lässt sich über die Browser-Einstellungen löschen. Eine Einwilligung ist dafür nicht erforderlich, weil die Speicherung für die gewünschte Funktion nötig ist (§ 25 Abs. 2 Nr. 2 TDDDG).</p>
<h2>4. Vorführung der Karten</h2>
<p>Die Karten auf dieser Webseite laufen vollständig in deinem Browser und arbeiten mit Beispieldaten. Es werden keine Eingaben übertragen.</p>
<h2>5. Links zu anderen Webseiten</h2>
<p>Diese Webseite verweist unter anderem auf GitHub und auf my.home-assistant.io. Erst wenn du einen solchen Link anklickst, werden Daten an den jeweiligen Anbieter übertragen. Dort gelten dessen Datenschutzbestimmungen.</p>
<h2>6. SmartLists und SmartDiscounts in Home Assistant</h2>
<p>Die Integration SmartLists und die Karte SmartDiscounts laufen ausschließlich in deinem eigenen Home Assistant. Ich erhalte davon keine Daten. Das Nachschlagen von Produkten im Internet ist ausgeschaltet, bis du es selbst einschaltest und einen Dienst auswählst.</p>
<h2>7. App SmartLists Go</h2>
<p>Die App speichert Listen, Notizen und Einstellungen auf deinem Gerät. Verbindest du sie mit Home Assistant, tauscht sie Daten nur mit den Adressen aus, die du einträgst. Es gibt kein Konto bei mir, keine Auswertung der Nutzung und keine Werbung. Fehlerberichte sendet die App nicht von selbst; du kannst einen Bericht erstellen, prüfen und selbst absenden.</p>
<p>Meldest du dich über die Anmeldeseite deines Home Assistant an, ruft dein Home Assistant dabei einmal die Seite ha-smartlists.com/app/ ab, um die App zu erkennen. Dabei fällt beim Anbieter dieser Webseite dasselbe an wie bei jedem Seitenaufruf (Abschnitt 2), also die IP-Adresse deines Home Assistant. Die Seite selbst setzt keine Cookies, enthält keine Skripte und speichert nichts. Zugangsdaten oder Inhalte deiner Listen werden dabei nicht übertragen.</p>
<p>Das Nachschlagen von Strichcodes im Internet ist ausgeschaltet. Schaltest du es ein und wählst einen Dienst, sendet die App den gescannten Code an diesen Dienst; für dessen Verarbeitung gilt seine eigene Datenschutzerklärung.</p>
<p>Die von dieser Webseite installierte Fassung kann nach Updates sehen. Das ist ausgeschaltet, bis du einen Abstand wählst oder selbst prüfst; dann ruft die App die Datei ha-smartlists.com/downloads/version.json ab. Dabei fällt dasselbe an wie bei jedem Seitenaufruf (Abschnitt 2). Die App sendet dabei keine Angaben über dich oder deine Listen.</p>
<h2>8. Kontakt</h2>
<p>Wenn du mir eine E-Mail schreibst, verarbeite ich deine Angaben, um die Anfrage zu beantworten (Art. 6 Abs. 1 Buchst. f DSGVO). Die Nachricht wird gelöscht, sobald sie erledigt ist und keine Aufbewahrungspflicht besteht. Der „zweite Kontaktweg“ im Impressum ist ein Formular von Online-Impressum.de; dafür gilt die Datenschutzerklärung dieses Anbieters.</p>
<h2>9. Deine Rechte</h2>
<p>Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15 bis 21 DSGVO). Außerdem kannst du dich bei einer Datenschutz-Aufsichtsbehörde beschweren, zum Beispiel bei der Behörde deines Wohnorts.</p>
<h2>10. Änderungen</h2>
<p>Diese Erklärung wird angepasst, wenn sich die Webseite oder die Rechtslage ändert. Es gilt die hier veröffentlichte Fassung.</p>""",
    },
    "en": {
        "home": "Back to the start page", "imprint": "Legal notice", "privacy": "Privacy",
        "tagline": "SmartLists — shopping lists, to-dos and notes with Home Assistant.",
        "unofficial": "Not an official product of Home Assistant or the Open Home Foundation.",
        "imprint_path": "legal-notice", "privacy_path": "privacy",
        "imprint_body": f"""<h1>Legal notice</h1><p class="lead">Information according to § 5 DDG (Germany) · The German version is the authoritative one.</p>
<div class="box">m3m0rex — {WHO}<br>Germany</div>
<h2>Contact</h2>
<p>E-mail: <a href="mailto:{MAIL}">{MAIL}</a><br><a href="{SECOND}">Second way of contact</a></p>
<p>Please address letters exactly as shown above; the line "c/o Online-Impressum 13167" must be included, otherwise the letter cannot be assigned.</p>
<h2>Supervisory authority</h2>
<p>Landesanstalt für Medien Nordrhein-Westfalen · seat: Germany</p>
<h2>Consumer dispute resolution</h2>
<p>I am neither willing nor obliged to take part in dispute resolution proceedings before a consumer arbitration board.</p>
<h2>Note</h2>
<p>SmartLists, SmartDiscounts and SmartLists Go are private, free projects and are not affiliated with Home Assistant or the Open Home Foundation.</p>""",
        "privacy_body": f"""<h1>Privacy policy</h1><p class="lead">As of November 2026 · The German version is the authoritative one.</p>
<div class="short"><div><b>No cookies</b>This website sets no cookies.</div><div><b>No tracking</b>No statistics, no advertising, no embedded services.</div><div><b>No account</b>No form, no sign-in, no newsletter.</div></div>
<h2>1. Controller</h2>
<div class="box">{WHO}<br>Germany<br>E-mail: <a href="mailto:{MAIL}">{MAIL}</a></div>
<h2>2. Visiting this website</h2>
<p>This website is provided through GitHub Pages, a service of GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA. When you visit it, GitHub processes technically necessary data to deliver the page and to secure the service, in particular:</p>
<ul><li>IP address</li><li>date and time of access</li><li>page requested and page visited before</li><li>browser and operating system</li></ul>
<p>I have no access to these logs and do not evaluate them. The legal basis is Art. 6(1)(f) GDPR; the legitimate interest is the secure and reliable operation of the website.</p>
<p>Data may be transferred to the USA. According to its own statement, GitHub is certified under the EU-US Data Privacy Framework. Details are in <a href="{GITHUB_PRIVACY}">GitHub's privacy statement</a>.</p>
<h2>3. Storage in the browser</h2>
<p>The website remembers the chosen language in your browser's local storage. This value stays on your device, is not transferred to me and can be deleted in the browser settings. No consent is required because the storage is necessary for the function you asked for (§ 25(2) no. 2 TDDDG).</p>
<h2>4. Demonstration of the cards</h2>
<p>The cards on this website run entirely in your browser and work with sample data. No input is transferred.</p>
<h2>5. Links to other websites</h2>
<p>This website links to GitHub and my.home-assistant.io, among others. Data is transferred to the respective provider only when you click such a link. Their privacy rules apply there.</p>
<h2>6. SmartLists and SmartDiscounts in Home Assistant</h2>
<p>The SmartLists integration and the SmartDiscounts card run exclusively in your own Home Assistant. I receive no data from them. Looking up products on the internet is switched off until you switch it on yourself and choose a service.</p>
<h2>7. The app SmartLists Go</h2>
<p>The app stores lists, notes and settings on your device. If you connect it to Home Assistant, it exchanges data only with the addresses you enter. There is no account with me, no usage analysis and no advertising. The app never sends error reports on its own; you can create a report, check it and send it yourself.</p>
<p>If you sign in through the sign-in page of your Home Assistant, your Home Assistant retrieves the page ha-smartlists.com/app/ once to recognise the app. The provider of this website then receives the same data as for any page view (section 2), i.e. the IP address of your Home Assistant. The page itself sets no cookies, contains no scripts and stores nothing. No credentials and no list contents are transferred.</p>
<p>Looking up barcodes on the internet is switched off. If you switch it on and choose a service, the app sends the scanned code to that service; its own privacy policy applies to that processing.</p>
<p>The version installed from this website can look for updates. This is switched off until you choose an interval or check manually; the app then retrieves the file ha-smartlists.com/downloads/version.json. The same data arises as for any page view (section 2). The app sends no information about you or your lists.</p>
<h2>8. Contact</h2>
<p>If you write me an e-mail, I process your details to answer the request (Art. 6(1)(f) GDPR). The message is deleted once it has been dealt with and no retention obligation applies. The "second way of contact" in the legal notice is a form by Online-Impressum.de; that provider's privacy policy applies to it.</p>
<h2>9. Your rights</h2>
<p>You have the right of access, rectification, erasure, restriction of processing, data portability and objection (Art. 15 to 21 GDPR). You may also lodge a complaint with a data protection supervisory authority, for example the one where you live.</p>
<h2>10. Changes</h2>
<p>This policy is adapted when the website or the legal situation changes. The version published here applies.</p>""",
    },
}


def style() -> str:
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    return src[src.index("<style"):src.index("</style>") + len("</style>")]


def build(lang: str, kind: str, css: str) -> tuple[Path, str]:
    p = PAGES[lang]
    path = p[f"{kind}_path"]
    up = "../" if lang == "de" else "../../"          # zur Wurzel der Webseite
    home = up if lang == "de" else "../"              # Startseite dieser Sprache
    other = "en" if lang == "de" else "de"
    other_url = f"{up}en/{PAGES['en'][kind + '_path']}/" if lang == "de" else f"{up}{PAGES['de'][kind + '_path']}/"
    title = p["imprint"] if kind == "imprint" else p["privacy"]
    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · SmartLists</title>
<link rel="icon" href="{up}assets/icon.png">
<link rel="canonical" href="https://ha-smartlists.com/{'' if lang == 'de' else 'en/'}{path}/">
{css}
{EXTRA}
</head>
<body data-product="hacs">
<nav>
  <a class="brand" href="{home}"><img src="{up}assets/icon.png" alt="">SmartLists</a>
  <div class="switch"></div>
  <div class="right langs">
    <a href="./" lang="{lang}" aria-current="page">{lang.upper()}</a><a href="{other_url}" lang="{other}">{other.upper()}</a>
  </div>
</nav>
<main class="legal">
<a class="back" href="{home}">← {p['home']}</a>
{p[kind + '_body']}
</main>
<footer>
  {p['tagline']}<br>
  {p['unofficial']}
  <div class="legal-links"><a href="../{p['imprint_path']}/">{p['imprint']}</a>·<a href="../{p['privacy_path']}/">{p['privacy']}</a></div>
</footer>
</body>
</html>
"""
    target = ROOT / ("" if lang == "de" else "en") / path / "index.html"
    return target, html


def main() -> int:
    css = style()
    for lang in PAGES:
        for kind in ("imprint", "privacy"):
            target, html = build(lang, kind, css)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            print("geschrieben:", target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
