"""Übersetzte Seiten erzeugen: aus index.html (Deutsch, die Quelle) werden en/, fr/, es/, it/ und pl/index.html.

Nach jeder Änderung an index.html:   python build_i18n.py
Neue oder geänderte deutsche Texte, die hier noch keine Übersetzung haben, werden gemeldet und bleiben bis dahin
deutsch. Übersetzt werden Texte zwischen Tags sowie alt / title / aria-label / content.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LANGS = ("en", "fr", "es", "it", "pl")
# Texte, die gleich bleiben (Namen, Links, Code)
KEEP = {"HA SmartLists", "GitHub", "Download", "REWE", "👤 Anna", "todo.*", "https://github.com/m3m0rex/ha_smartlists",
        "🇩🇪 DE", "🇬🇧 EN", "🇫🇷 FR", "🇪🇸 ES", "🇮🇹 IT", "🇵🇱 PL",
        "Wiki"}

# Deutsch → (en, fr, es, it, pl)
T: dict[str, tuple[str, str, str, str, str]] = {
    "HA SmartLists – Einkaufslisten für Home Assistant": (
        "HA SmartLists – shopping lists for Home Assistant", "HA SmartLists – listes de courses pour Home Assistant",
        "HA SmartLists – listas de la compra para Home Assistant", "HA SmartLists – liste della spesa per Home Assistant",
        "HA SmartLists – listy zakupów dla Home Assistant"),
    "SmartLists: echte Einkaufslisten für Home Assistant – als HACS-Integration mit Kategorien, Einkaufsmodus und Teilen per Link, oder als Android-App mit lokalen Listen und Widget.": (
        "SmartLists: real shopping lists for Home Assistant – as a HACS integration with categories, shopping mode and sharing via link, or as an Android app with local lists and a widget.",
        "SmartLists : de vraies listes de courses pour Home Assistant – en intégration HACS avec catégories, mode courses et partage par lien, ou en app Android avec listes locales et widget.",
        "SmartLists: listas de la compra de verdad para Home Assistant – como integración HACS con categorías, modo compra y compartir por enlace, o como app Android con listas locales y widget.",
        "SmartLists: vere liste della spesa per Home Assistant – come integrazione HACS con categorie, modalità spesa e condivisione via link, o come app Android con liste locali e widget.",
        "SmartLists: prawdziwe listy zakupów dla Home Assistant – jako integracja HACS z kategoriami, trybem zakupów i udostępnianiem przez link albo jako aplikacja na Androida z lokalnymi listami i widżetem."),
    "und": ("and", "et", "y", "e", "i"),
    "Sprache": ("Language", "Langue", "Idioma", "Lingua", "Język"),
    "Produkt wählen": ("Choose product", "Choisir le produit", "Elegir producto", "Scegli il prodotto", "Wybierz produkt"),
    "🏠 HACS-Integration": ("🏠 HACS integration", "🏠 Intégration HACS", "🏠 Integración HACS", "🏠 Integrazione HACS", "🏠 Integracja HACS"),
    "🤖 Android-App": ("🤖 Android app", "🤖 App Android", "🤖 App Android", "🤖 App Android", "🤖 Aplikacja Android"),
    "HACS-Integration": ("HACS integration", "Intégration HACS", "Integración HACS", "Integrazione HACS", "Integracja HACS"),
    "Android-App": ("Android app", "App Android", "App Android", "App Android", "Aplikacja Android"),
    "Noch nicht veröffentlicht": ("Not released yet", "Pas encore publiée", "Aún no publicada", "Non ancora pubblicata", "Jeszcze nie wydana"),
    "🚧 Noch nicht veröffentlicht – bald verfügbar": (
        "🚧 Not released yet – coming soon", "🚧 Pas encore publiée – bientôt disponible", "🚧 Aún no publicada – disponible pronto",
        "🚧 Non ancora pubblicata – presto disponibile", "🚧 Jeszcze nie wydana – wkrótce dostępna"),
    # ---------- HACS ----------
    "Integration für Home Assistant": ("Integration for Home Assistant", "Intégration pour Home Assistant", "Integración para Home Assistant", "Integrazione per Home Assistant", "Integracja dla Home Assistant"),
    "SmartLists für Home Assistant": ("SmartLists for Home Assistant", "SmartLists pour Home Assistant", "SmartLists para Home Assistant", "SmartLists per Home Assistant", "SmartLists dla Home Assistant"),
    "Milch 2 l 1,19€ @REWE *Anna #bio": ("Milk 2 l 1,19€ @REWE *Anna #organic", "Lait 2 l 1,19€ @REWE *Anna #bio", "Leche 2 l 1,19€ @REWE *Anna #bio", "Latte 2 l 1,19€ @REWE *Anna #bio", "Mleko 2 l 1,19€ @REWE *Anna #bio"),
    "eintippen – SmartLists erkennt Menge, Preis, Markt, Person und Kategorie und sortiert den Artikel wie im Laden ein. Direkt in Home Assistant, ohne Cloud.": (
        "– type it and SmartLists recognises quantity, price, store, person and category and files the item like in the store. Right in Home Assistant, no cloud.",
        "– tape-le et SmartLists reconnaît quantité, prix, magasin, personne et catégorie et range l'article comme en magasin. Directement dans Home Assistant, sans cloud.",
        "– escríbelo y SmartLists reconoce cantidad, precio, tienda, persona y categoría y ordena el artículo como en la tienda. Directamente en Home Assistant, sin nube.",
        "– scrivilo e SmartLists riconosce quantità, prezzo, negozio, persona e categoria e ordina l'articolo come in negozio. Direttamente in Home Assistant, senza cloud.",
        "– wpisz, a SmartLists rozpozna ilość, cenę, sklep, osobę i kategorię i ułoży produkt jak w sklepie. Bezpośrednio w Home Assistant, bez chmury."),
    "⬇️ In HACS öffnen": ("⬇️ Open in HACS", "⬇️ Ouvrir dans HACS", "⬇️ Abrir en HACS", "⬇️ Apri in HACS", "⬇️ Otwórz w HACS"),
    "GitHub &amp; Doku": ("GitHub &amp; docs", "GitHub &amp; doc", "GitHub y documentación", "GitHub e documentazione", "GitHub i dokumentacja"),
    "Kostenlos · Open Source (MIT) · Home Assistant 2025.3 oder neuer · 6 Sprachen": (
        "Free · open source (MIT) · Home Assistant 2025.3 or newer · 6 languages", "Gratuit · open source (MIT) · Home Assistant 2025.3 ou plus récent · 6 langues",
        "Gratis · código abierto (MIT) · Home Assistant 2025.3 o posterior · 6 idiomas", "Gratis · open source (MIT) · Home Assistant 2025.3 o successivo · 6 lingue",
        "Za darmo · open source (MIT) · Home Assistant 2025.3 lub nowszy · 6 języków"),
    "Ein Eingabefeld. Alles erkannt.": ("One input field. Everything recognised.", "Un seul champ. Tout est reconnu.", "Un solo campo. Todo reconocido.", "Un solo campo. Tutto riconosciuto.", "Jedno pole. Wszystko rozpoznane."),
    "Schon beim Tippen siehst du, was daraus wird – und mit dem nächsten Tipp steht der Artikel an der richtigen Stelle der Liste.": (
        "While you type you already see what it becomes – one more tap and the item sits in the right place of the list.",
        "Pendant la saisie, tu vois déjà le résultat – un tap de plus et l'article est au bon endroit de la liste.",
        "Mientras escribes ya ves el resultado – un toque más y el artículo está en su sitio en la lista.",
        "Mentre scrivi vedi già il risultato – un tocco ancora e l'articolo è al posto giusto nella lista.",
        "Już podczas pisania widzisz efekt – jeszcze jedno dotknięcie i produkt jest we właściwym miejscu listy."),
    "#bio": ("#organic", "#bio", "#bio", "#bio", "#bio"),
    "🧀 Kühlung": ("🧀 Chilled", "🧀 Frais", "🧀 Refrigerados", "🧀 Freschi", "🧀 Chłodnia"),
    "sind nur die Vorgabe – die Zeichen legst du selbst fest.": (
        "are just the default – you choose the characters yourself.", "ne sont que la valeur par défaut – tu choisis toi-même les caractères.",
        "son solo el valor por defecto – tú eliges los caracteres.", "sono solo il valore predefinito – i caratteri li scegli tu.",
        "to tylko domyślne znaki – możesz wybrać własne."),
    "SmartLists macht aus den To-do-Listen von Home Assistant echte Einkaufslisten: mehrere Listen zu einer zusammenfassen, nach Kategorie sortieren, Mengen, Märkte und Personen als Badges, ein Einkaufsmodus für unterwegs und Teilen per QR-Code. Jede Liste bleibt eine ganz normale": (
        "SmartLists turns Home Assistant's to-do lists into real shopping lists: combine several lists into one, sort by category, quantities, stores and people as badges, a shopping mode on the go and sharing via QR code. Every list stays a regular",
        "SmartLists transforme les listes de tâches de Home Assistant en vraies listes de courses : regrouper plusieurs listes, trier par catégorie, quantités, magasins et personnes en badges, un mode courses et le partage par QR code. Chaque liste reste une entité",
        "SmartLists convierte las listas de tareas de Home Assistant en listas de la compra de verdad: juntar varias listas en una, ordenar por categoría, cantidades, tiendas y personas como insignias, un modo compra y compartir por código QR. Cada lista sigue siendo una entidad",
        "SmartLists trasforma le liste di cose da fare di Home Assistant in vere liste della spesa: unire più liste, ordinare per categoria, quantità, negozi e persone come badge, una modalità spesa e condivisione via codice QR. Ogni lista resta una normale entità",
        "SmartLists zamienia listy zadań Home Assistant w prawdziwe listy zakupów: łączenie kilku list w jedną, sortowanie wg kategorii, ilości, sklepy i osoby jako odznaki, tryb zakupów i udostępnianie kodem QR. Każda lista pozostaje zwykłą encją"),
    "-Entität – sie funktioniert in Dashboards, mit Assist, in Automationen und in den Widgets der Home-Assistant-App.": (
        "entity – it works in dashboards, with Assist, in automations and in the widgets of the Home Assistant app.",
        "normale – elle fonctionne dans les tableaux de bord, avec Assist, dans les automatisations et dans les widgets de l'app Home Assistant.",
        "normal – funciona en paneles, con Assist, en automatizaciones y en los widgets de la app de Home Assistant.",
        "– funziona nelle dashboard, con Assist, nelle automazioni e nei widget dell'app Home Assistant.",
        "– działa na pulpitach, z Assist, w automatyzacjach i w widżetach aplikacji Home Assistant."),
    "Listen &amp; Eingabe": ("Lists &amp; input", "Listes &amp; saisie", "Listas y entrada", "Liste e inserimento", "Listy i wpisywanie"),
    "Listen zusammenfassen": ("Combine lists", "Regrouper des listes", "Juntar listas", "Unire le liste", "Łączenie list"),
    "Die Listen von Anna und Max (Einkaufsliste, Local To-do, Google Tasks, Bring!, CalDAV …) werden zu einer gemeinsamen Liste. Abhaken wirkt in der Original-Liste.": (
        "Anna's and Max's lists (Shopping List, Local To-do, Google Tasks, Bring!, CalDAV …) become one shared list. Checking off acts on the original list.",
        "Les listes d'Anna et de Max (liste de courses, Local To-do, Google Tasks, Bring!, CalDAV …) deviennent une liste commune. Cocher agit sur la liste d'origine.",
        "Las listas de Anna y Max (lista de la compra, Local To-do, Google Tasks, Bring!, CalDAV …) se convierten en una lista común. Marcar actúa en la lista original.",
        "Le liste di Anna e Max (lista della spesa, Local To-do, Google Tasks, Bring!, CalDAV …) diventano una lista comune. Spuntare agisce sulla lista originale.",
        "Listy Anny i Maksa (lista zakupów, Local To-do, Google Tasks, Bring!, CalDAV …) stają się jedną wspólną listą. Odhaczenie działa na liście źródłowej."),
    "Sortiert wie im Laden": ("Sorted like in the store", "Trié comme en magasin", "Ordenado como en la tienda", "Ordinato come in negozio", "Ułożone jak w sklepie"),
    "Wortlisten in sechs Sprachen, gemerkte Korrekturen und eine Gang-Reihenfolge je Markt und Filiale. Je Liste abschaltbar.": (
        "Keyword packs in six languages, remembered corrections and an aisle order per store and branch. Can be switched off per list.",
        "Listes de mots en six langues, corrections mémorisées et ordre des rayons par magasin. Désactivable par liste.",
        "Listas de palabras en seis idiomas, correcciones recordadas y orden de pasillos por tienda. Desactivable por lista.",
        "Elenchi di parole in sei lingue, correzioni memorizzate e ordine delle corsie per negozio. Disattivabile per lista.",
        "Słowniki w sześciu językach, zapamiętane poprawki i kolejność alejek dla każdego sklepu. Można wyłączyć dla listy."),
    "Vorschläge je Liste": ("Suggestions per list", "Suggestions par liste", "Sugerencias por lista", "Suggerimenti per lista", "Podpowiedzi dla każdej listy"),
    "„Häufig gekauft“, fällige Artikel nach eurem Rhythmus und Vorschläge beim Tippen – aus genau dieser Liste, nicht aus allen.": (
        "“Bought often”, items due by your rhythm and suggestions while typing – from exactly this list, not from all of them.",
        "« Souvent achetés », articles à racheter selon votre rythme et suggestions à la saisie – de cette liste précise, pas de toutes.",
        "«Comprado a menudo», artículos pendientes según vuestro ritmo y sugerencias al escribir – de esta lista, no de todas.",
        "«Acquistati spesso», articoli in scadenza secondo il vostro ritmo e suggerimenti mentre scrivi – proprio da questa lista, non da tutte.",
        "„Często kupowane”, produkty do kupienia wg waszego rytmu i podpowiedzi podczas pisania – z tej listy, nie ze wszystkich."),
    "Einfache Listen": ("Plain lists", "Listes simples", "Listas simples", "Liste semplici", "Proste listy"),
    "NEU": ("NEW", "NOUVEAU", "NUEVO", "NUOVO", "NOWE"),
    "Für den Baumarkt oder die Packliste: keine Kategorien, keine Vorschläge, nichts gemerkt – was dort steht, taucht nirgends sonst auf.": (
        "For the hardware store or a packing list: no categories, no suggestions, nothing remembered – what is there shows up nowhere else.",
        "Pour le bricolage ou la liste de bagages : pas de catégories, pas de suggestions, rien de mémorisé – ce qui y figure n'apparaît nulle part ailleurs.",
        "Para la ferretería o la lista de equipaje: sin categorías, sin sugerencias, nada recordado – lo que hay ahí no aparece en ningún otro sitio.",
        "Per il fai da te o la lista bagagli: niente categorie, niente suggerimenti, nulla memorizzato – ciò che c'è non compare altrove.",
        "Do marketu budowlanego albo listy pakowania: bez kategorii, bez podpowiedzi, nic nie zapamiętane – to, co tam jest, nie pojawia się nigdzie indziej."),
    "Eigene Listen mit Rechten": ("Own lists with permissions", "Listes propres avec droits", "Listas propias con permisos", "Liste proprie con permessi", "Własne listy z uprawnieniami"),
    "Listen mit Besitzer, pro Person freigegeben zum Sehen, Abhaken oder Bearbeiten. Vorhandene Listen lassen sich mit allen Artikeln übernehmen.": (
        "Lists with an owner, shared per person to view, check off or edit. Existing lists can be taken over with all items.",
        "Listes avec propriétaire, partagées par personne pour voir, cocher ou modifier. Les listes existantes se reprennent avec tous leurs articles.",
        "Listas con propietario, compartidas por persona para ver, marcar o editar. Las listas existentes se pueden traspasar con todos sus artículos.",
        "Liste con proprietario, condivise per persona per vedere, spuntare o modificare. Le liste esistenti si possono trasferire con tutti gli articoli.",
        "Listy z właścicielem, udostępniane osobom do podglądu, odhaczania lub edycji. Istniejące listy można przejąć ze wszystkimi produktami."),
    "Extras nach Bedarf": ("Extras when you need them", "Extras à la demande", "Extras según necesidad", "Extra quando servono", "Dodatki według potrzeb"),
    "Wochenplan mit Kalender und Mealie-Import, Notizen, Statistik und Ausgaben, ein Einkaufs-Dashboard mit Unterseite je Liste – für Einsteiger aus, jederzeit zuschaltbar.": (
        "Meal plan with calendar and Mealie import, notes, statistics and expenses, a shopping dashboard with one sub-page per list – off for beginners, switch on any time.",
        "Menu de la semaine avec calendrier et import Mealie, notes, statistiques et dépenses, un tableau de bord courses avec une sous-page par liste – désactivés au départ, activables à tout moment.",
        "Plan semanal con calendario e importación de Mealie, notas, estadísticas y gastos, un panel de compras con una subpágina por lista – desactivados al empezar, activables en cualquier momento.",
        "Piano settimanale con calendario e import da Mealie, note, statistiche e spese, una dashboard della spesa con una sottopagina per lista – spenti all'inizio, attivabili in qualsiasi momento.",
        "Plan tygodnia z kalendarzem i importem z Mealie, notatki, statystyki i wydatki, pulpit zakupów z podstroną dla każdej listy – na start wyłączone, można je włączyć w każdej chwili."),
    "Einkaufen": ("Shopping", "Courses", "Compra", "Spesa", "Zakupy"),
    "Einkaufsmodus": ("Shopping mode", "Mode courses", "Modo compra", "Modalità spesa", "Tryb zakupów"),
    "Große Zeilen, ganze Zeile antippen zum Abhaken (mit 3 Sekunden Rückgängig), auf Wunsch lange drücken zum Löschen, Markt-Leiste, Bildschirm bleibt an. Der Markt wird per Zone automatisch gewählt.": (
        "Large rows, tap the whole row to check off (with 3-second undo), optionally long press to delete, store bar, screen stays on. The store is picked automatically by zone.",
        "Grandes lignes, toucher toute la ligne pour cocher (annulation pendant 3 secondes), appui long pour supprimer si tu veux, barre des magasins, écran allumé. Le magasin est choisi automatiquement par zone.",
        "Filas grandes, tocar toda la fila para marcar (con 3 segundos para deshacer), opcionalmente pulsación larga para borrar, barra de tiendas, pantalla encendida. La tienda se elige sola por zona.",
        "Righe grandi, tocca tutta la riga per spuntare (con 3 secondi per annullare), se vuoi pressione lunga per eliminare, barra dei negozi, schermo acceso. Il negozio viene scelto in automatico per zona.",
        "Duże wiersze, dotknięcie całego wiersza odhacza (z 3 sekundami na cofnięcie), opcjonalnie długie przytrzymanie usuwa, pasek sklepów, ekran nie gaśnie. Sklep wybierany automatycznie wg strefy."),
    "Offline im Supermarkt": ("Offline in the supermarket", "Hors ligne au supermarché", "Sin conexión en el súper", "Offline al supermercato", "Offline w supermarkecie"),
    "Kein Empfang? Abhaken und Hinzufügen gehen weiter und werden übertragen, sobald Home Assistant wieder erreichbar ist.": (
        "No signal? Checking off and adding keep working and are sent as soon as Home Assistant is reachable again.",
        "Pas de réseau ? Cocher et ajouter continuent de fonctionner et sont envoyés dès que Home Assistant est de nouveau joignable.",
        "¿Sin cobertura? Marcar y añadir siguen funcionando y se envían en cuanto Home Assistant vuelve a estar accesible.",
        "Niente campo? Spuntare e aggiungere funzionano lo stesso e vengono inviati appena Home Assistant è di nuovo raggiungibile.",
        "Brak zasięgu? Odhaczanie i dodawanie działają dalej i zostaną wysłane, gdy Home Assistant znów będzie dostępny."),
    "Preise &amp; Ausgaben": ("Prices &amp; expenses", "Prix &amp; dépenses", "Precios y gastos", "Prezzi e spese", "Ceny i wydatki"),
    "Preise im Text werden erkannt und je Einheit gemerkt, die Liste zeigt eine Summe, abgehakt wird als Ausgabe gebucht – pro Monat und Markt.": (
        "Prices in the text are recognised and remembered per unit, the list shows a total, checking off books an expense – per month and store.",
        "Les prix dans le texte sont reconnus et mémorisés par unité, la liste affiche un total, cocher enregistre une dépense – par mois et par magasin.",
        "Los precios del texto se reconocen y recuerdan por unidad, la lista muestra un total y al marcar se registra un gasto – por mes y tienda.",
        "I prezzi nel testo vengono riconosciuti e memorizzati per unità, la lista mostra un totale, spuntare registra una spesa – per mese e negozio.",
        "Ceny w tekście są rozpoznawane i zapamiętywane za jednostkę, lista pokazuje sumę, odhaczenie księguje wydatek – wg miesiąca i sklepu."),
    "Teilen": ("Sharing", "Partage", "Compartir", "Condivisione", "Udostępnianie"),
    "Per Link &amp; QR-Code": ("Via link &amp; QR code", "Par lien &amp; QR code", "Por enlace y código QR", "Via link e codice QR", "Przez link i kod QR"),
    "Für Nachbarn, Gäste oder Freunde ohne Konto: nur diese eine Liste, befristet, jederzeit widerrufbar – nur ansehen, „soft“ abhaken oder auch hinzufügen.": (
        "For neighbours, guests or friends without an account: only this one list, time-limited, revocable any time – view only, “soft” check or also add.",
        "Pour voisins, invités ou amis sans compte : seulement cette liste, limitée dans le temps, révocable à tout moment – voir, cocher « soft » ou aussi ajouter.",
        "Para vecinos, invitados o amigos sin cuenta: solo esta lista, con fecha límite, revocable en cualquier momento – solo ver, marcar «soft» o también añadir.",
        "Per vicini, ospiti o amici senza account: solo questa lista, a tempo, revocabile in qualsiasi momento – solo vedere, spuntare «soft» o anche aggiungere.",
        "Dla sąsiadów, gości lub znajomych bez konta: tylko ta lista, czasowo, z możliwością cofnięcia – tylko podgląd, odhaczanie „soft” lub też dodawanie."),
    "Ohne deine Adresse zu verraten": ("Without revealing your address", "Sans révéler ton adresse", "Sin revelar tu dirección", "Senza rivelare il tuo indirizzo", "Bez ujawniania twojego adresu"),
    "Links laufen auf Wunsch über einen Cloudflare-Tunnel (auch mit fester Adresse auf deiner Domain) oder deinen eigenen Proxy. Home Assistant selbst ist darüber nie erreichbar.": (
        "Links can run through a Cloudflare tunnel (also with a fixed address on your domain) or your own proxy. Home Assistant itself is never reachable that way.",
        "Les liens peuvent passer par un tunnel Cloudflare (aussi avec adresse fixe sur ton domaine) ou ton propre proxy. Home Assistant lui-même n'est jamais accessible ainsi.",
        "Los enlaces pueden ir por un túnel de Cloudflare (también con dirección fija en tu dominio) o por tu propio proxy. Home Assistant nunca es accesible por ahí.",
        "I link possono passare da un tunnel Cloudflare (anche con indirizzo fisso sul tuo dominio) o dal tuo proxy. Home Assistant stesso non è mai raggiungibile così.",
        "Linki mogą działać przez tunel Cloudflare (także ze stałym adresem w twojej domenie) lub twój własny proxy. Sam Home Assistant nie jest przez nie dostępny."),
    "Man sieht, wer es war": ("You see who it was", "On voit qui c'était", "Se ve quién fue", "Si vede chi è stato", "Widać, kto to był"),
    "Wer über den Link markiert oder hinzufügt, gibt einmal seinen Namen an – in deiner Liste steht dann „von Max markiert (Link)“.": (
        "Whoever marks or adds via the link enters their name once – your list then says “marked by Max (link)”.",
        "Qui coche ou ajoute via le lien indique une fois son nom – ta liste affiche alors « marqué par Max (lien) ».",
        "Quien marca o añade por el enlace indica su nombre una vez – tu lista muestra entonces «marcado por Max (enlace)».",
        "Chi segna o aggiunge tramite il link inserisce una volta il proprio nome – nella tua lista compare «segnato da Max (link)».",
        "Kto oznacza lub dodaje przez link, raz podaje swoje imię – na twojej liście widać wtedy „oznaczone przez Max (link)”."),
    "Überall dabei": ("Everywhere you need it", "Partout avec toi", "Siempre a mano", "Sempre a portata di mano", "Zawsze pod ręką"),
    "Eigene Seite in der Seitenleiste": ("Its own sidebar page", "Une page dans la barre latérale", "Página propia en la barra lateral", "Pagina propria nella barra laterale", "Własna strona na pasku bocznym"),
    "Alle Listen ohne Dashboard – eine oder mehrere nebeneinander, Artikel per Ziehen verschieben, Einstellungen an einem Ort.": (
        "All lists without a dashboard – one or several side by side, drag items between them, settings in one place.",
        "Toutes les listes sans tableau de bord – une ou plusieurs côte à côte, déplacer les articles en les glissant, réglages au même endroit.",
        "Todas las listas sin panel – una o varias en paralelo, arrastrar artículos entre ellas, ajustes en un solo lugar.",
        "Tutte le liste senza dashboard – una o più affiancate, trascina gli articoli, impostazioni in un unico posto.",
        "Wszystkie listy bez pulpitu – jedna lub kilka obok siebie, przeciąganie produktów, ustawienia w jednym miejscu."),
    "Lovelace-Karte": ("Lovelace card", "Carte Lovelace", "Tarjeta Lovelace", "Scheda Lovelace", "Karta Lovelace"),
    "Mit Vorlagen für Familie, Küchen-Tablet, Markt-Karte, Nur-ansehen und Kachel. Funktioniert mit jeder To-do-Liste.": (
        "With presets for family, kitchen tablet, store card, view only and tile. Works with every to-do list.",
        "Avec des modèles famille, tablette de cuisine, carte magasin, lecture seule et tuile. Fonctionne avec toute liste de tâches.",
        "Con plantillas para familia, tablet de cocina, tarjeta de tienda, solo ver y mosaico. Funciona con cualquier lista de tareas.",
        "Con modelli per famiglia, tablet in cucina, scheda negozio, sola lettura e riquadro. Funziona con qualsiasi lista di cose da fare.",
        "Z szablonami: rodzina, tablet w kuchni, karta sklepu, tylko podgląd i kafelek. Działa z każdą listą zadań."),
    "Widgets &amp; App-Symbol": ("Widgets &amp; app icon", "Widgets &amp; icône d'app", "Widgets e icono de app", "Widget e icona app", "Widżety i ikona aplikacji"),
    "Läuft mit den Startbildschirm-Widgets der Home-Assistant-App (Android und iOS), unter Android auch hübsch gestaltet im Template-Widget. Dazu ein App-Symbol, das eine Liste direkt im Einkaufsmodus öffnet.": (
        "Works with the home-screen widgets of the Home Assistant app (Android and iOS), on Android also nicely formatted in the Template widget. Plus an app icon that opens a list straight in shopping mode.",
        "Fonctionne avec les widgets d'écran d'accueil de l'app Home Assistant (Android et iOS), sous Android aussi joliment mis en forme dans le widget Template. Plus une icône qui ouvre une liste directement en mode courses.",
        "Funciona con los widgets de pantalla de inicio de la app de Home Assistant (Android e iOS), en Android también con buen formato en el widget Template. Además, un icono que abre una lista directamente en modo compra.",
        "Funziona con i widget della schermata Home dell'app Home Assistant (Android e iOS), su Android anche ben formattata nel widget Template. In più un'icona che apre una lista direttamente in modalità spesa.",
        "Działa z widżetami ekranu głównego aplikacji Home Assistant (Android i iOS), na Androidzie także ładnie sformatowana w widżecie Template. Do tego ikona otwierająca listę od razu w trybie zakupów."),
    "Assist &amp; Automationen": ("Assist &amp; automations", "Assist &amp; automatisations", "Assist y automatizaciones", "Assist e automazioni", "Assist i automatyzacje"),
    "„Setz Milch auf die Einkaufsliste“, „Bin im Laden“-Ereignis, Markt-Erinnerung, fällige Artikel und fertige Blueprints.": (
        "“Put milk on the shopping list”, “I'm at the store” event, store reminder, due items and ready-made blueprints.",
        "« Ajoute du lait à la liste de courses », événement « je suis au magasin », rappel de magasin, articles à racheter et blueprints prêts à l'emploi.",
        "«Añade leche a la lista de la compra», evento «estoy en la tienda», recordatorio de tienda, artículos pendientes y blueprints listos.",
        "«Aggiungi il latte alla lista della spesa», evento «sono al negozio», promemoria negozio, articoli in scadenza e blueprint pronti.",
        "„Dodaj mleko do listy zakupów”, zdarzenie „jestem w sklepie”, przypomnienie o sklepie, produkty do kupienia i gotowe blueprinty."),
    "So sieht es aus": ("What it looks like", "À quoi ça ressemble", "Así se ve", "Ecco come appare", "Tak to wygląda"),
    "Seite „SmartLists“ – kombinierte Liste mit Kategorien, Badges und Preisen.": (
        "“SmartLists” page – combined list with categories, badges and prices.", "Page « SmartLists » – liste combinée avec catégories, badges et prix.",
        "Página «SmartLists» – lista combinada con categorías, insignias y precios.", "Pagina «SmartLists» – lista combinata con categorie, badge e prezzi.",
        "Strona „SmartLists” – połączona lista z kategoriami, odznakami i cenami."),
    "Einkaufsmodus: große Zeilen, Markt-Leiste.": ("Shopping mode: large rows, store bar.", "Mode courses : grandes lignes, barre des magasins.", "Modo compra: filas grandes, barra de tiendas.", "Modalità spesa: righe grandi, barra dei negozi.", "Tryb zakupów: duże wiersze, pasek sklepów."),
    "Teilen per Link und QR-Code – nur diese Liste, befristet.": ("Share via link and QR code – only this list, time-limited.", "Partage par lien et QR code – seulement cette liste, limité dans le temps.", "Compartir por enlace y código QR – solo esta lista, con fecha límite.", "Condivisione via link e codice QR – solo questa lista, a tempo.", "Udostępnianie przez link i kod QR – tylko ta lista, czasowo."),
    "Einstellungen an einem Ort – für mich, für alle, je Liste.": ("Settings in one place – for me, for everyone, per list.", "Réglages au même endroit – pour moi, pour tous, par liste.", "Ajustes en un solo lugar – para mí, para todos, por lista.", "Impostazioni in un unico posto – per me, per tutti, per lista.", "Ustawienia w jednym miejscu – dla mnie, dla wszystkich, dla listy."),
    "Alles bleibt bei dir": ("Everything stays with you", "Tout reste chez toi", "Todo se queda contigo", "Tutto resta da te", "Wszystko zostaje u ciebie"),
    "SmartLists läuft komplett in deinem Home Assistant. Keine Cloud, kein Konto, kein Tracking. Geteilte Links enthalten einen zufälligen 256-Bit-Schlüssel und zeigen nur die Artikel dieser einen Liste – keine Notizen, Preise oder Personen.": (
        "SmartLists runs entirely in your Home Assistant. No cloud, no account, no tracking. Shared links contain a random 256-bit key and show only the items of that one list – no notes, prices or people.",
        "SmartLists fonctionne entièrement dans ton Home Assistant. Pas de cloud, pas de compte, pas de pistage. Les liens partagés contiennent une clé aléatoire de 256 bits et ne montrent que les articles de cette liste – ni notes, ni prix, ni personnes.",
        "SmartLists funciona por completo en tu Home Assistant. Sin nube, sin cuenta, sin rastreo. Los enlaces compartidos llevan una clave aleatoria de 256 bits y solo muestran los artículos de esa lista – sin notas, precios ni personas.",
        "SmartLists gira interamente nel tuo Home Assistant. Niente cloud, niente account, nessun tracciamento. I link condivisi contengono una chiave casuale a 256 bit e mostrano solo gli articoli di quella lista – niente note, prezzi o persone.",
        "SmartLists działa w całości w twoim Home Assistant. Bez chmury, bez konta, bez śledzenia. Udostępnione linki zawierają losowy 256-bitowy klucz i pokazują tylko produkty tej jednej listy – bez notatek, cen i osób."),
    "Für die ganze Familie": ("For the whole family", "Pour toute la famille", "Para toda la familia", "Per tutta la famiglia", "Dla całej rodziny"),
    "Jeder behält seine Liste, die gemeinsame zeigt alles. Wer etwas einträgt, kann eine Benachrichtigung auslösen – an die Companion-App, Telegram oder jeden anderen notify-Dienst.": (
        "Everyone keeps their own list, the shared one shows everything. Adding something can trigger a notification – to the companion app, Telegram or any other notify service.",
        "Chacun garde sa liste, la liste commune montre tout. Un ajout peut déclencher une notification – vers l'app compagnon, Telegram ou tout autre service notify.",
        "Cada uno mantiene su lista, la común lo muestra todo. Añadir algo puede enviar una notificación – a la app companion, Telegram o cualquier otro servicio notify.",
        "Ognuno tiene la sua lista, quella comune mostra tutto. Aggiungere qualcosa può inviare una notifica – all'app companion, a Telegram o a qualsiasi altro servizio notify.",
        "Każdy ma swoją listę, wspólna pokazuje wszystko. Dodanie czegoś może wysłać powiadomienie – do aplikacji companion, na Telegram lub do innej usługi notify."),
    "Installation": ("Installation", "Installation", "Instalación", "Installazione", "Instalacja"),
    "In HACS hinzufügen": ("Add in HACS", "Ajouter dans HACS", "Añadir en HACS", "Aggiungi in HACS", "Dodaj w HACS"),
    "HACS → ⋮ → Benutzerdefinierte Repositories →": ("HACS → ⋮ → Custom repositories →", "HACS → ⋮ → Dépôts personnalisés →", "HACS → ⋮ → Repositorios personalizados →", "HACS → ⋮ → Repository personalizzati →", "HACS → ⋮ → Niestandardowe repozytoria →"),
    ", Typ „Integration“.": (", type “Integration”.", ", type « Intégration ».", ", tipo «Integración».", ", tipo «Integrazione».", ", typ „Integracja”."),
    "Herunterladen &amp; neu starten": ("Download &amp; restart", "Télécharger &amp; redémarrer", "Descargar y reiniciar", "Scarica e riavvia", "Pobierz i uruchom ponownie"),
    "„SmartLists“ herunterladen und Home Assistant neu starten.": ("Download “SmartLists” and restart Home Assistant.", "Télécharger « SmartLists » et redémarrer Home Assistant.", "Descargar «SmartLists» y reiniciar Home Assistant.", "Scarica «SmartLists» e riavvia Home Assistant.", "Pobierz „SmartLists” i uruchom ponownie Home Assistant."),
    "Integration hinzufügen": ("Add the integration", "Ajouter l'intégration", "Añadir la integración", "Aggiungi l'integrazione", "Dodaj integrację"),
    "Einstellungen → Geräte &amp; Dienste → Integration hinzufügen → SmartLists.": (
        "Settings → Devices &amp; services → Add integration → SmartLists.", "Paramètres → Appareils et services → Ajouter une intégration → SmartLists.",
        "Ajustes → Dispositivos y servicios → Añadir integración → SmartLists.", "Impostazioni → Dispositivi e servizi → Aggiungi integrazione → SmartLists.",
        "Ustawienia → Urządzenia i usługi → Dodaj integrację → SmartLists."),
    "Assistent folgen": ("Follow the assistant", "Suivre l'assistant", "Seguir el asistente", "Segui l'assistente", "Postępuj zgodnie z kreatorem"),
    "Links „SmartLists“ öffnen – ein kurzer Assistent fragt nach Listen, Märkten und Sprache. Etwa zwei Minuten.": (
        "Open “SmartLists” in the sidebar – a short assistant asks for lists, stores and language. About two minutes.",
        "Ouvrir « SmartLists » dans la barre latérale – un court assistant demande listes, magasins et langue. Environ deux minutes.",
        "Abrir «SmartLists» en la barra lateral – un breve asistente pregunta por listas, tiendas e idioma. Unos dos minutos.",
        "Apri «SmartLists» nella barra laterale – un breve assistente chiede liste, negozi e lingua. Circa due minuti.",
        "Otwórz „SmartLists” na pasku bocznym – krótki kreator zapyta o listy, sklepy i język. Około dwóch minut."),
    "Bereit für bessere Einkaufslisten?": ("Ready for better shopping lists?", "Prêt pour de meilleures listes de courses ?", "¿Listo para mejores listas de la compra?", "Pronto per liste della spesa migliori?", "Gotowy na lepsze listy zakupów?"),
    "Kostenlos und Open Source. Läuft komplett in deinem Home Assistant.": ("Free and open source. Runs entirely in your Home Assistant.", "Gratuit et open source. Fonctionne entièrement dans ton Home Assistant.", "Gratis y de código abierto. Funciona por completo en tu Home Assistant.", "Gratis e open source. Gira interamente nel tuo Home Assistant.", "Za darmo i open source. Działa w całości w twoim Home Assistant."),
    "📖 Dokumentation": ("📖 Documentation", "📖 Documentation", "📖 Documentación", "📖 Documentazione", "📖 Dokumentacja"),
    "Lieber eine eigene App mit lokalen Listen und Widget?": ("Prefer an app of its own with local lists and a widget?", "Plutôt une app dédiée avec listes locales et widget ?", "¿Prefieres una app propia con listas locales y widget?", "Preferisci un'app dedicata con liste locali e widget?", "Wolisz osobną aplikację z lokalnymi listami i widżetem?"),
    "Zur Android-App →": ("To the Android app →", "Vers l'app Android →", "A la app Android →", "All'app Android →", "Do aplikacji Android →"),
    "Passwort &amp; Notizen": ("Password &amp; notes", "Mot de passe &amp; notes", "Contraseña y notas", "Password e note", "Hasło i notatki"),
    "Jeder Link optional mit Passwort; Notizen der Artikel nur, wenn du sie freigibst. Die geteilte Seite hat Suche, Sortierung, Angebote und zeigt, wie lange sie noch geteilt ist.": (
        "Every link optionally with a password; item notes only if you allow them. The shared page has search, sorting, offers and shows how long it is still shared.",
        "Chaque lien avec mot de passe en option ; les notes des articles seulement si tu les autorises. La page partagée a recherche, tri, promos et indique combien de temps elle reste partagée.",
        "Cada enlace con contraseña opcional; las notas de los artículos solo si las permites. La página compartida tiene búsqueda, orden, ofertas y muestra cuánto tiempo sigue compartida.",
        "Ogni link con password facoltativa; le note degli articoli solo se le consenti. La pagina condivisa ha ricerca, ordinamento, offerte e mostra per quanto è ancora condivisa.",
        "Każdy link opcjonalnie z hasłem; notatki produktów tylko, jeśli na to pozwolisz. Udostępniona strona ma wyszukiwanie, sortowanie, promocje i pokazuje, jak długo jeszcze jest udostępniona."),
    "Wer darf was?": ("Who may do what?", "Qui peut faire quoi ?", "¿Quién puede hacer qué?", "Chi può fare cosa?", "Kto może co?"),
    "Für Personen in Home Assistant: nur wer hinzugefügt ist, hat Zugriff – je Person sehen, abhaken oder bearbeiten.": (
        "For people in Home Assistant: only people you add have access – view, check off or edit per person.",
        "Pour les personnes dans Home Assistant : seules celles que tu ajoutes ont accès – voir, cocher ou modifier par personne.",
        "Para personas en Home Assistant: solo quien añadas tiene acceso – ver, marcar o editar por persona.",
        "Per le persone in Home Assistant: ha accesso solo chi aggiungi – vedere, spuntare o modificare per persona.",
        "Dla osób w Home Assistant: dostęp mają tylko dodane osoby – podgląd, odhaczanie lub edycja dla każdej."),
    # ---------- App ----------
    "App für Android": ("App for Android", "App pour Android", "App para Android", "App per Android", "Aplikacja na Androida"),
    "Einkaufslisten, To-dos und Notizen – lokal auf dem Gerät, optional verbunden mit Home Assistant. Ganz ohne eigenes Backend.": (
        "Shopping lists, to-dos and notes – locally on the device, optionally connected to Home Assistant. No backend of its own.",
        "Listes de courses, tâches et notes – en local sur l'appareil, connectées à Home Assistant si tu veux. Sans backend propre.",
        "Listas de la compra, tareas y notas – en local en el dispositivo, conectadas a Home Assistant si quieres. Sin backend propio.",
        "Liste della spesa, cose da fare e note – in locale sul dispositivo, collegate a Home Assistant se vuoi. Senza backend proprio.",
        "Listy zakupów, zadania i notatki – lokalnie na urządzeniu, opcjonalnie połączone z Home Assistant. Bez własnego backendu."),
    "⬇️ APK herunterladen": ("⬇️ Download APK", "⬇️ Télécharger l'APK", "⬇️ Descargar APK", "⬇️ Scarica l'APK", "⬇️ Pobierz APK"),
    "Android 13 oder neuer · direkte Installation, kein Play Store nötig": (
        "Android 13 or newer · direct install, no Play Store needed", "Android 13 ou plus récent · installation directe, sans Play Store",
        "Android 13 o posterior · instalación directa, sin Play Store", "Android 13 o successivo · installazione diretta, senza Play Store",
        "Android 13 lub nowszy · bezpośrednia instalacja, bez Sklepu Play"),
    "HA SmartLists ist eine native Android-App für Einkaufs- und To-do-Listen sowie Notizen. Listen lassen sich komplett lokal auf dem Gerät führen oder mit Home Assistant verbinden, mehrere Home-Assistant-Listen importieren und beliebig zu eigenen Merge-Listen zusammenführen. Alles läuft direkt zwischen App und Home Assistant – es gibt keinen zusätzlichen Cloud-Dienst und keinen Zwischenserver.": (
        "HA SmartLists is a native Android app for shopping and to-do lists and notes. Keep lists entirely on the device or connect them to Home Assistant, import several Home Assistant lists and merge them into your own merge lists. Everything runs directly between the app and Home Assistant – no extra cloud service, no middle server.",
        "HA SmartLists est une app Android native pour listes de courses, tâches et notes. Les listes restent entièrement sur l'appareil ou se connectent à Home Assistant ; on peut importer plusieurs listes Home Assistant et les fusionner librement. Tout passe directement entre l'app et Home Assistant – aucun service cloud ni serveur intermédiaire.",
        "HA SmartLists es una app Android nativa para listas de la compra, tareas y notas. Las listas pueden quedarse en el dispositivo o conectarse a Home Assistant, importar varias listas de Home Assistant y fusionarlas a tu gusto. Todo va directamente entre la app y Home Assistant – sin servicio en la nube ni servidor intermedio.",
        "HA SmartLists è un'app Android nativa per liste della spesa, cose da fare e note. Le liste restano tutte sul dispositivo o si collegano a Home Assistant; si possono importare più liste di Home Assistant e unirle a piacere. Tutto passa direttamente tra app e Home Assistant – nessun servizio cloud né server intermedio.",
        "HA SmartLists to natywna aplikacja na Androida do list zakupów, zadań i notatek. Listy mogą być w całości na urządzeniu lub połączone z Home Assistant; można importować kilka list z Home Assistant i dowolnie je łączyć. Wszystko działa bezpośrednio między aplikacją a Home Assistant – bez chmury i serwera pośredniego."),
    "Listen &amp; Organisation": ("Lists &amp; organisation", "Listes &amp; organisation", "Listas y organización", "Liste e organizzazione", "Listy i organizacja"),
    "Lokale Listen": ("Local lists", "Listes locales", "Listas locales", "Liste locali", "Lokalne listy"),
    "Einkaufs- oder To-do-Listen komplett offline anlegen, umbenennen, löschen und mit Artikeln füllen – ganz ohne Home Assistant.": (
        "Create, rename, delete and fill shopping or to-do lists completely offline – without Home Assistant.",
        "Créer, renommer, supprimer et remplir des listes de courses ou de tâches entièrement hors ligne – sans Home Assistant.",
        "Crear, renombrar, borrar y llenar listas de la compra o de tareas totalmente sin conexión – sin Home Assistant.",
        "Crea, rinomina, elimina e riempi liste della spesa o di cose da fare completamente offline – senza Home Assistant.",
        "Twórz, zmieniaj nazwy, usuwaj i wypełniaj listy zakupów lub zadań całkowicie offline – bez Home Assistant."),
    "Home Assistant verbinden": ("Connect Home Assistant", "Connecter Home Assistant", "Conectar Home Assistant", "Collega Home Assistant", "Połącz Home Assistant"),
    "Bestehende To-do-Listen aus Home Assistant importieren und direkt in der App verwalten – Änderungen laufen in beide Richtungen synchron.": (
        "Import existing to-do lists from Home Assistant and manage them in the app – changes sync both ways.",
        "Importer des listes existantes de Home Assistant et les gérer dans l'app – les modifications se synchronisent dans les deux sens.",
        "Importar listas existentes de Home Assistant y gestionarlas en la app – los cambios se sincronizan en ambos sentidos.",
        "Importa liste esistenti da Home Assistant e gestiscile nell'app – le modifiche si sincronizzano in entrambe le direzioni.",
        "Importuj istniejące listy z Home Assistant i zarządzaj nimi w aplikacji – zmiany synchronizują się w obie strony."),
    "Merge-Listen mit Konfliktmodus": ("Merge lists with conflict mode", "Listes fusionnées avec mode de conflit", "Listas fusionadas con modo de conflicto", "Liste unite con modalità conflitti", "Listy scalone z trybem konfliktów"),
    "Mehrere lokale und Home-Assistant-Listen zu einer Ansicht zusammenführen. Pro Merge-Liste wählbar: beidseitig synchron, Home Assistant führend oder rein lokal.": (
        "Merge several local and Home Assistant lists into one view. Per merge list: two-way sync, Home Assistant leading or local only.",
        "Réunir plusieurs listes locales et Home Assistant en une vue. Par liste fusionnée : synchro bidirectionnelle, Home Assistant prioritaire ou purement local.",
        "Unir varias listas locales y de Home Assistant en una vista. Por lista fusionada: sincronización en ambos sentidos, Home Assistant manda o solo local.",
        "Unisci più liste locali e di Home Assistant in una vista. Per ogni lista unita: sincronizzazione bidirezionale, Home Assistant prioritario o solo locale.",
        "Połącz kilka list lokalnych i z Home Assistant w jeden widok. Dla każdej: synchronizacja dwukierunkowa, Home Assistant nadrzędny lub tylko lokalnie."),
    "Favorisieren, umbenennen, löschen": ("Favourite, rename, delete", "Favori, renommer, supprimer", "Favorito, renombrar, borrar", "Preferiti, rinomina, elimina", "Ulubione, zmiana nazwy, usuwanie"),
    "Ein langer Druck auf einen Artikel öffnet ein Menü zum Favorisieren, Umbenennen, Kopieren oder Löschen – Favoriten wandern automatisch nach oben.": (
        "A long press on an item opens a menu to favourite, rename, copy or delete – favourites move to the top automatically.",
        "Un appui long sur un article ouvre un menu pour le mettre en favori, le renommer, le copier ou le supprimer – les favoris remontent automatiquement.",
        "Una pulsación larga en un artículo abre un menú para marcar como favorito, renombrar, copiar o borrar – los favoritos suben solos.",
        "Una pressione lunga su un articolo apre un menu per preferiti, rinomina, copia o elimina – i preferiti salgono in cima da soli.",
        "Długie przytrzymanie produktu otwiera menu: ulubione, zmiana nazwy, kopiowanie, usuwanie – ulubione same przesuwają się na górę."),
    "Listen ausblenden": ("Hide lists", "Masquer des listes", "Ocultar listas", "Nascondere liste", "Ukrywanie list"),
    "Listen, die gerade nicht gebraucht werden, lassen sich als „unsichtbar\" markieren. Sie bleiben erhalten, verschwinden aber aus allen Übersichten und Auswahlfeldern.": (
        "Lists you don't need right now can be marked “invisible”. They are kept but disappear from all overviews and pickers.",
        "Les listes inutiles pour l'instant peuvent être marquées « invisibles ». Elles sont conservées mais disparaissent des vues et sélecteurs.",
        "Las listas que no necesitas ahora se pueden marcar como «invisibles». Se conservan pero desaparecen de vistas y selectores.",
        "Le liste che ora non servono si possono segnare come «invisibili». Restano salvate ma spariscono da panoramiche e selettori.",
        "Listy, których teraz nie potrzebujesz, można oznaczyć jako „niewidoczne”. Zostają zachowane, ale znikają z przeglądów i wyborów."),
    "Text-Import": ("Text import", "Import de texte", "Importar texto", "Importazione testo", "Import tekstu"),
    "Bestehende Listen aus anderen Apps (z.B. ColorNote-Checklisten oder einfaches CSV) per Copy &amp; Paste als fertige Artikel übernehmen.": (
        "Take over lists from other apps (e.g. ColorNote checklists or simple CSV) as items via copy &amp; paste.",
        "Reprendre des listes d'autres apps (p. ex. checklists ColorNote ou CSV simple) en articles par copier-coller.",
        "Pasar listas de otras apps (p. ej. checklists de ColorNote o CSV sencillo) como artículos copiando y pegando.",
        "Trasferisci liste da altre app (ad es. checklist di ColorNote o CSV semplice) come articoli con copia e incolla.",
        "Przenoś listy z innych aplikacji (np. listy ColorNote lub prosty CSV) jako produkty przez kopiuj-wklej."),
    "Notizen": ("Notes", "Notes", "Notas", "Note", "Notatki"),
    "Eigener Notizen-Bereich": ("A notes area of its own", "Espace notes dédié", "Zona de notas propia", "Area note dedicata", "Osobna sekcja notatek"),
    "Notizen mit Titel und Text, getrennt von den Einkaufslisten. Lokal speicherbar oder mit Home Assistant synchronisiert.": (
        "Notes with title and text, separate from the shopping lists. Stored locally or synced with Home Assistant.",
        "Notes avec titre et texte, séparées des listes de courses. Stockées localement ou synchronisées avec Home Assistant.",
        "Notas con título y texto, separadas de las listas de la compra. Guardadas en local o sincronizadas con Home Assistant.",
        "Note con titolo e testo, separate dalle liste della spesa. Salvate in locale o sincronizzate con Home Assistant.",
        "Notatki z tytułem i treścią, oddzielnie od list zakupów. Zapisywane lokalnie lub synchronizowane z Home Assistant."),
    "Migration zu Home Assistant": ("Migration to Home Assistant", "Migration vers Home Assistant", "Migración a Home Assistant", "Migrazione a Home Assistant", "Migracja do Home Assistant"),
    "Lokale Notizlisten lassen sich jederzeit nachträglich zu Home Assistant migrieren, inklusive kompletten Inhalts.": (
        "Local note lists can be migrated to Home Assistant at any time, including all content.",
        "Les listes de notes locales peuvent être migrées vers Home Assistant à tout moment, avec tout leur contenu.",
        "Las listas de notas locales se pueden migrar a Home Assistant en cualquier momento, con todo su contenido.",
        "Le liste di note locali si possono migrare a Home Assistant in qualsiasi momento, con tutto il contenuto.",
        "Lokalne listy notatek można w każdej chwili przenieść do Home Assistant wraz z całą treścią."),
    "Übersichtlich lesen, einfach bearbeiten": ("Clear to read, easy to edit", "Lecture claire, édition facile", "Lectura clara, edición sencilla", "Lettura chiara, modifica semplice", "Czytelnie i łatwo do edycji"),
    "Eine Notiz öffnet sich zunächst schreibgeschützt im Vollbild mit anklickbaren Links – ein Tipp auf das Stift-Symbol schaltet auf Bearbeiten um.": (
        "A note first opens read-only in full screen with clickable links – tap the pencil to switch to editing.",
        "Une note s'ouvre d'abord en lecture seule en plein écran avec des liens cliquables – un tap sur le crayon passe en édition.",
        "Una nota se abre primero en solo lectura a pantalla completa con enlaces pulsables – al tocar el lápiz se pasa a editar.",
        "Una nota si apre prima in sola lettura a schermo intero con link cliccabili – un tocco sulla matita passa alla modifica.",
        "Notatka otwiera się najpierw tylko do odczytu na pełnym ekranie z klikalnymi linkami – dotknięcie ołówka włącza edycję."),
    "Widget &amp; Alltag": ("Widget &amp; everyday use", "Widget &amp; quotidien", "Widget y día a día", "Widget e uso quotidiano", "Widżet i codzienność"),
    "Home-Bildschirm-Widget": ("Home-screen widget", "Widget d'écran d'accueil", "Widget de pantalla de inicio", "Widget della schermata Home", "Widżet ekranu głównego"),
    "Eine Liste, Merge-Liste oder Notizliste direkt auf dem Homescreen anzeigen, inklusive Abhaken direkt im Widget und anpassbaren Farben/Schrift.": (
        "Show a list, merge list or note list right on the home screen, check off in the widget, with adjustable colours and font.",
        "Afficher une liste, une liste fusionnée ou une liste de notes sur l'écran d'accueil, cocher dans le widget, couleurs et police réglables.",
        "Mostrar una lista, lista fusionada o lista de notas en la pantalla de inicio, marcar en el widget, colores y letra ajustables.",
        "Mostra una lista, lista unita o lista di note sulla schermata Home, spunta nel widget, colori e carattere personalizzabili.",
        "Pokaż listę, listę scaloną lub listę notatek na ekranie głównym, odhaczaj w widżecie, kolory i czcionka do ustawienia."),
    "Backup &amp; Wiederherstellung": ("Backup &amp; restore", "Sauvegarde &amp; restauration", "Copia y restauración", "Backup e ripristino", "Kopia i przywracanie"),
    "Lokale Listen, Merge-Listen und Einstellungen lassen sich manuell oder automatisch in Home Assistant sichern, verwalten und mit Zeitstempel wiederherstellen.": (
        "Local lists, merge lists and settings can be backed up to Home Assistant manually or automatically, managed and restored with a timestamp.",
        "Listes locales, listes fusionnées et réglages se sauvegardent dans Home Assistant à la main ou automatiquement, et se restaurent par horodatage.",
        "Listas locales, fusionadas y ajustes se pueden guardar en Home Assistant a mano o automáticamente, gestionar y restaurar por fecha.",
        "Liste locali, liste unite e impostazioni si salvano in Home Assistant a mano o in automatico, si gestiscono e si ripristinano per data.",
        "Lokalne listy, listy scalone i ustawienia można zapisywać w Home Assistant ręcznie lub automatycznie i przywracać według daty."),
    "Sync-Status &amp; Protokoll": ("Sync status &amp; log", "Statut de synchro &amp; journal", "Estado de sincronización y registro", "Stato sincronizzazione e registro", "Stan synchronizacji i dziennik"),
    "Der Verbindungsstatus ist immer sichtbar. Eine eigene Detailseite zeigt die Warteschlange offener Änderungen und ein Protokoll der letzten Sync-Vorgänge.": (
        "The connection status is always visible. A detail page shows the queue of pending changes and a log of recent syncs.",
        "L'état de connexion est toujours visible. Une page de détail montre la file des modifications en attente et un journal des dernières synchros.",
        "El estado de conexión siempre está visible. Una página de detalle muestra la cola de cambios pendientes y un registro de las últimas sincronizaciones.",
        "Lo stato della connessione è sempre visibile. Una pagina di dettaglio mostra la coda delle modifiche in attesa e un registro delle ultime sincronizzazioni.",
        "Stan połączenia jest zawsze widoczny. Osobna strona pokazuje kolejkę oczekujących zmian i dziennik ostatnich synchronizacji."),
    "Zusammen mit der HACS-Integration": ("Together with the HACS integration", "Avec l'intégration HACS", "Junto con la integración HACS", "Insieme all'integrazione HACS", "Razem z integracją HACS"),
    "Mit der SmartLists-Integration in Home Assistant koppelt sich die App automatisch: dieselben Badges, Kategorien und Vorschläge, kombinierte Listen aus Home Assistant und gemeinsam gemerkte Kategorien.": (
        "With the SmartLists integration in Home Assistant the app pairs automatically: the same badges, categories and suggestions, combined lists from Home Assistant and shared remembered categories.",
        "Avec l'intégration SmartLists dans Home Assistant, l'app s'associe automatiquement : mêmes badges, catégories et suggestions, listes combinées de Home Assistant et catégories mémorisées en commun.",
        "Con la integración SmartLists en Home Assistant la app se vincula sola: mismas insignias, categorías y sugerencias, listas combinadas de Home Assistant y categorías recordadas en común.",
        "Con l'integrazione SmartLists in Home Assistant l'app si abbina da sola: stessi badge, categorie e suggerimenti, liste combinate da Home Assistant e categorie memorizzate in comune.",
        "Z integracją SmartLists w Home Assistant aplikacja paruje się automatycznie: te same odznaki, kategorie i podpowiedzi, połączone listy z Home Assistant i wspólnie zapamiętane kategorie."),
    "Mehr zur Integration →": ("More about the integration →", "En savoir plus sur l'intégration →", "Más sobre la integración →", "Di più sull'integrazione →", "Więcej o integracji →"),
    "Perfekt für Familien": ("Perfect for families", "Parfait pour les familles", "Perfecto para familias", "Perfetto per le famiglie", "Idealne dla rodzin"),
    "Mehrere Personen greifen über ihre eigenen Geräte auf dieselben Home-Assistant-Listen zu. Jeder sieht, was noch fehlt – ohne Chat-Nachrichten hin und her.": (
        "Several people use the same Home Assistant lists from their own devices. Everyone sees what is still missing – no chat messages back and forth.",
        "Plusieurs personnes accèdent aux mêmes listes Home Assistant depuis leurs appareils. Chacun voit ce qui manque – sans échanges de messages.",
        "Varias personas usan las mismas listas de Home Assistant desde sus dispositivos. Todos ven lo que falta – sin mensajes de ida y vuelta.",
        "Più persone usano le stesse liste di Home Assistant dai propri dispositivi. Tutti vedono cosa manca – senza messaggi avanti e indietro.",
        "Kilka osób korzysta z tych samych list Home Assistant na swoich urządzeniach. Każdy widzi, czego brakuje – bez wysyłania wiadomości."),
    "Datenschutz": ("Privacy", "Confidentialité", "Privacidad", "Privacy", "Prywatność"),
    "Zugangsdaten zu Home Assistant werden ausschließlich verschlüsselt auf dem Gerät gespeichert. Es gibt keinen externen Server, keine Werbung und kein Tracking – die Kommunikation läuft direkt zwischen App und der eigenen Home-Assistant-Instanz.": (
        "Home Assistant credentials are stored only encrypted on the device. No external server, no ads, no tracking – communication runs directly between the app and your own Home Assistant.",
        "Les identifiants Home Assistant sont stockés uniquement chiffrés sur l'appareil. Pas de serveur externe, pas de pub, pas de pistage – la communication passe directement entre l'app et ton Home Assistant.",
        "Las credenciales de Home Assistant se guardan solo cifradas en el dispositivo. Sin servidor externo, sin anuncios, sin rastreo – la comunicación va directamente entre la app y tu Home Assistant.",
        "Le credenziali di Home Assistant sono salvate solo cifrate sul dispositivo. Nessun server esterno, niente pubblicità né tracciamento – la comunicazione va direttamente tra l'app e il tuo Home Assistant.",
        "Dane logowania do Home Assistant są przechowywane tylko w zaszyfrowanej postaci na urządzeniu. Bez zewnętrznego serwera, reklam i śledzenia – komunikacja idzie bezpośrednio między aplikacją a twoim Home Assistant."),
    "So geht's": ("How it works", "Comment ça marche", "Cómo funciona", "Come funziona", "Jak to działa"),
    "APK herunterladen": ("Download the APK", "Télécharger l'APK", "Descargar el APK", "Scarica l'APK", "Pobierz APK"),
    "Über den Download-Button oben. Die Installation aus unbekannten Quellen muss einmalig erlaubt werden.": (
        "Via the download button above. Installing from unknown sources has to be allowed once.",
        "Via le bouton de téléchargement ci-dessus. L'installation de sources inconnues doit être autorisée une fois.",
        "Con el botón de descarga de arriba. Hay que permitir una vez la instalación desde fuentes desconocidas.",
        "Con il pulsante di download in alto. L'installazione da fonti sconosciute va consentita una volta.",
        "Przyciskiem pobierania powyżej. Instalację z nieznanych źródeł trzeba raz zezwolić."),
    "App öffnen": ("Open the app", "Ouvrir l'app", "Abrir la app", "Apri l'app", "Otwórz aplikację"),
    "Direkt lokale Listen anlegen – oder im Menü Einstellungen → Verbindung Home Assistant verbinden.": (
        "Create local lists right away – or connect Home Assistant under Settings → Connection.",
        "Créer tout de suite des listes locales – ou connecter Home Assistant sous Paramètres → Connexion.",
        "Crear listas locales directamente – o conectar Home Assistant en Ajustes → Conexión.",
        "Crea subito liste locali – oppure collega Home Assistant in Impostazioni → Connessione.",
        "Od razu twórz lokalne listy – albo połącz Home Assistant w Ustawienia → Połączenie."),
    "Long-Lived Token eintragen": ("Enter a long-lived token", "Saisir un jeton longue durée", "Introducir un token de larga duración", "Inserisci un token di lunga durata", "Wpisz token długoterminowy"),
    "In Home Assistant unter dem eigenen Profil erstellt, dann in der App unter „Integration-Token\" einfügen.": (
        "Create it in Home Assistant under your profile, then paste it in the app under “Integration token”.",
        "Le créer dans Home Assistant depuis ton profil, puis le coller dans l'app sous « Jeton d'intégration ».",
        "Créalo en Home Assistant en tu perfil y pégalo en la app en «Token de integración».",
        "Crealo in Home Assistant dal tuo profilo, poi incollalo nell'app in «Token integrazione».",
        "Utwórz go w Home Assistant w swoim profilu, potem wklej w aplikacji w „Token integracji”."),
    "Loslegen": ("Get going", "C'est parti", "A empezar", "Si parte", "Do dzieła"),
    "Listen laden, Merge-Listen anlegen, Widget einrichten – fertig.": ("Load lists, create merge lists, set up the widget – done.", "Charger les listes, créer des listes fusionnées, configurer le widget – terminé.", "Cargar listas, crear listas fusionadas, configurar el widget – listo.", "Carica le liste, crea liste unite, configura il widget – fatto.", "Wczytaj listy, utwórz listy scalone, skonfiguruj widżet – gotowe."),
    "Bereit loszulegen?": ("Ready to start?", "Prêt à commencer ?", "¿Listo para empezar?", "Pronto a iniziare?", "Gotowy, by zacząć?"),
    "Kostenlos, ohne Login, ohne Cloud-Zwang.": ("Free, no login, no cloud required.", "Gratuit, sans connexion, sans cloud obligatoire.", "Gratis, sin login, sin nube obligatoria.", "Gratis, senza login, senza cloud obbligatorio.", "Za darmo, bez logowania, bez przymusu chmury."),
    "Alles direkt in Home Assistant, ohne App?": ("Everything right in Home Assistant, without an app?", "Tout directement dans Home Assistant, sans app ?", "¿Todo directamente en Home Assistant, sin app?", "Tutto direttamente in Home Assistant, senza app?", "Wszystko bezpośrednio w Home Assistant, bez aplikacji?"),
    "Zur HACS-Integration →": ("To the HACS integration →", "Vers l'intégration HACS →", "A la integración HACS →", "All'integrazione HACS →", "Do integracji HACS →"),
    # ---------- Vergleich & Fußzeile ----------
    "Integration oder App?": ("Integration or app?", "Intégration ou app ?", "¿Integración o app?", "Integrazione o app?", "Integracja czy aplikacja?"),
    "Läuft in": ("Runs in", "Fonctionne dans", "Funciona en", "Funziona in", "Działa w"),
    "Home Assistant (Browser, HA-App, Dashboards)": ("Home Assistant (browser, HA app, dashboards)", "Home Assistant (navigateur, app HA, tableaux de bord)", "Home Assistant (navegador, app de HA, paneles)", "Home Assistant (browser, app HA, dashboard)", "Home Assistant (przeglądarka, aplikacja HA, pulpity)"),
    "Eigene App auf dem Android-Gerät": ("Its own app on the Android device", "App dédiée sur l'appareil Android", "App propia en el dispositivo Android", "App dedicata sul dispositivo Android", "Osobna aplikacja na urządzeniu z Androidem"),
    "Ohne Home Assistant nutzbar": ("Usable without Home Assistant", "Utilisable sans Home Assistant", "Utilizable sin Home Assistant", "Utilizzabile senza Home Assistant", "Działa bez Home Assistant"),
    "✓ lokale Listen": ("✓ local lists", "✓ listes locales", "✓ listas locales", "✓ liste locali", "✓ lokalne listy"),
    "Kategorien &amp; Badges": ("Categories &amp; badges", "Catégories &amp; badges", "Categorías e insignias", "Categorie e badge", "Kategorie i odznaki"),
    "✓ wenn mit der Integration gekoppelt": ("✓ when paired with the integration", "✓ si associée à l'intégration", "✓ si está vinculada con la integración", "✓ se abbinata all'integrazione", "✓ po sparowaniu z integracją"),
    "Einkaufsmodus, Offline-Einkauf": ("Shopping mode, offline shopping", "Mode courses, courses hors ligne", "Modo compra, compra sin conexión", "Modalità spesa, spesa offline", "Tryb zakupów, zakupy offline"),
    "Listen liegen lokal auf dem Gerät": ("Lists are stored on the device", "Listes stockées sur l'appareil", "Listas guardadas en el dispositivo", "Liste salvate sul dispositivo", "Listy zapisane na urządzeniu"),
    "Teilen per Link für Leute ohne Konto": ("Sharing via link for people without an account", "Partage par lien pour personnes sans compte", "Compartir por enlace con personas sin cuenta", "Condivisione via link per chi non ha account", "Udostępnianie linkiem osobom bez konta"),
    "Widget zum Abhaken": ("Widget to check off", "Widget pour cocher", "Widget para marcar", "Widget per spuntare", "Widżet do odhaczania"),
    "über die Widgets der HA-App": ("via the widgets of the HA app", "via les widgets de l'app HA", "con los widgets de la app de HA", "tramite i widget dell'app HA", "przez widżety aplikacji HA"),
    "✓ eigenes Widget": ("✓ own widget", "✓ widget propre", "✓ widget propio", "✓ widget proprio", "✓ własny widżet"),
    "Kosten &amp; Lizenz": ("Cost &amp; licence", "Coût &amp; licence", "Coste y licencia", "Costo e licenza", "Koszt i licencja"),
    "kostenlos, Open Source (MIT)": ("free, open source (MIT)", "gratuit, open source (MIT)", "gratis, código abierto (MIT)", "gratis, open source (MIT)", "za darmo, open source (MIT)"),
    "kostenlos, proprietär": ("free, proprietary", "gratuit, propriétaire", "gratis, propietaria", "gratis, proprietaria", "za darmo, własnościowa"),
    "HA SmartLists — Einkaufslisten, To-dos und Notizen mit Home Assistant.": (
        "HA SmartLists — shopping lists, to-dos and notes with Home Assistant.", "HA SmartLists — listes de courses, tâches et notes avec Home Assistant.",
        "HA SmartLists — listas de la compra, tareas y notas con Home Assistant.", "HA SmartLists — liste della spesa, cose da fare e note con Home Assistant.",
        "HA SmartLists — listy zakupów, zadania i notatki z Home Assistant."),
    "Integration:": ("Integration:", "Intégration :", "Integración:", "Integrazione:", "Integracja:"),
    "MIT-Lizenz": ("MIT licence", "Licence MIT", "Licencia MIT", "Licenza MIT", "Licencja MIT"),
    "App: proprietär, Nutzung der offiziellen APK für den privaten Gebrauch – siehe": (
        "App: proprietary, use of the official APK for personal use – see", "App : propriétaire, usage de l'APK officiel à titre privé – voir",
        "App: propietaria, uso del APK oficial para fines personales – ver", "App: proprietaria, uso dell'APK ufficiale per uso personale – vedi",
        "Aplikacja: własnościowa, korzystanie z oficjalnego APK do użytku prywatnego – zob."),
    "Lizenz": ("licence", "licence", "licencia", "licenza", "licencja"),
    # ---------- Bildbeschreibungen ----------
    "Eintippen von „Milch 2 l 1,19€ @REWE *Anna #bio“: Vorschau mit Menge, Preis, Badges und Kategorie, danach landet der Artikel unter Kühlung": (
        "Typing “Milk 2 l 1,19€ @REWE *Anna #organic”: preview with quantity, price, badges and category, then the item lands under Chilled",
        "Saisie de « Milk 2 l 1,19€ @REWE *Anna #organic » : aperçu avec quantité, prix, badges et catégorie, puis l'article arrive dans Frais",
        "Escribiendo «Milk 2 l 1,19€ @REWE *Anna #organic»: vista previa con cantidad, precio, insignias y categoría; luego el artículo pasa a Refrigerados",
        "Digitando «Milk 2 l 1,19€ @REWE *Anna #organic»: anteprima con quantità, prezzo, badge e categoria, poi l'articolo finisce in Freschi",
        "Wpisywanie „Milk 2 l 1,19€ @REWE *Anna #organic”: podgląd z ilością, ceną, odznakami i kategorią, potem produkt trafia do Chłodni"),
    "SmartLists-Seite mit kombinierter Liste, Kategorien, Badges und Preisen": (
        "SmartLists page with a combined list, categories, badges and prices", "Page SmartLists avec liste combinée, catégories, badges et prix",
        "Página de SmartLists con lista combinada, categorías, insignias y precios", "Pagina SmartLists con lista combinata, categorie, badge e prezzi",
        "Strona SmartLists z połączoną listą, kategoriami, odznakami i cenami"),
    "Einkaufsmodus am Gerät": ("Shopping mode on the device", "Mode courses sur l'appareil", "Modo compra en el dispositivo", "Modalità spesa sul dispositivo", "Tryb zakupów na urządzeniu"),
    "Teilen-Fenster mit QR-Code": ("Share window with QR code", "Fenêtre de partage avec QR code", "Ventana de compartir con código QR", "Finestra di condivisione con codice QR", "Okno udostępniania z kodem QR"),
    "Bild vergrößert": ("Enlarged image", "Image agrandie", "Imagen ampliada", "Immagine ingrandita", "Powiększony obraz"),
    "Schließen": ("Close", "Fermer", "Cerrar", "Chiudi", "Zamknij"),
    "Einstellungen mit Bereichen": ("Settings with areas", "Réglages par sections", "Ajustes por secciones", "Impostazioni per sezioni", "Ustawienia w sekcjach"),
    # „Probier es aus“
    "Probier es aus": ('Try it out', 'Essaie-le', 'Pruébalo', 'Provalo', 'Wypróbuj'),
    "Tipp einen Artikel ein, so wie du ihn in Home Assistant schreiben würdest – hier siehst du sofort, was SmartLists daraus macht.": ('Type an item the way you would write it in Home Assistant – you see right away what SmartLists makes of it.', "Saisis un article comme tu l'écrirais dans Home Assistant – tu vois tout de suite ce que SmartLists en fait.", 'Escribe un artículo como lo harías en Home Assistant – verás al instante qué hace SmartLists con él.', 'Scrivi un articolo come lo scriveresti in Home Assistant – vedi subito cosa ne fa SmartLists.', 'Wpisz produkt tak, jak w Home Assistant – od razu zobaczysz, co zrobi z nim SmartLists.'),
    "Artikel eintippen": ('Type an item', 'Saisir un article', 'Escribir un artículo', 'Scrivi un articolo', 'Wpisz produkt'),
    "Hinzufügen": ('Add', 'Ajouter', 'Añadir', 'Aggiungi', 'Dodaj'),
    "Beispiele:": ('Examples:', 'Exemples :', 'Ejemplos:', 'Esempi:', 'Przykłady:'),
    "4x Joghurt 150g": ('4x yoghurt 150g', '4x yaourt 150g', '4x yogur 150g', '4x yogurt 150g', '4x jogurt 150g'),
    "2,5kg Kartoffeln @Lidl": ('2,5kg potatoes @Lidl', '2,5kg pommes de terre @Lidl', '2,5kg patatas @Lidl', '2,5kg patate @Lidl', '2,5kg ziemniaki @Lidl'),
    "3 Brötchen": ('3 bread rolls', '3 baguettes', '3 panecillos', '3 panini', '3 bułki'),
    "Spülmittel 0,99€ @dm *Max": ('Washing up liquid 0,99€ @dm *Max', 'Liquide vaisselle 0,99€ @dm *Max', 'Lavavajillas 0,99€ @dm *Max', 'Detersivo piatti 0,99€ @dm *Max', 'Płyn do naczyń 0,99€ @dm *Max'),
    "Artikel": ('Item', 'Article', 'Artículo', 'Articolo', 'Produkt'),
    "Anzahl": ('Count', 'Nombre', 'Cantidad', 'Numero', 'Liczba'),
    "Größe": ('Size', 'Taille', 'Tamaño', 'Formato', 'Wielkość'),
    "Preis": ('Price', 'Prix', 'Precio', 'Prezzo', 'Cena'),
    "Markt": ('Store', 'Magasin', 'Tienda', 'Negozio', 'Sklep'),
    "Person": ('Person', 'Personne', 'Persona', 'Persona', 'Osoba'),
    "Tag": ('Tag', 'Tag', 'Etiqueta', 'Tag', 'Tag'),
    "Kategorie": ('Category', 'Catégorie', 'Categoría', 'Categoria', 'Kategoria'),
    "Läuft nur in deinem Browser, mit den Wortlisten der Integration. In Home Assistant merkt sich SmartLists zusätzlich deine Korrekturen und die Reihenfolge der Gänge je Markt.": ('Runs only in your browser, with the word lists of the integration. In Home Assistant, SmartLists also remembers your corrections and the aisle order per store.', "Fonctionne uniquement dans ton navigateur, avec les listes de mots de l'intégration. Dans Home Assistant, SmartLists retient en plus tes corrections et l'ordre des rayons par magasin.", 'Funciona solo en tu navegador, con las listas de palabras de la integración. En Home Assistant, SmartLists recuerda además tus correcciones y el orden de los pasillos por tienda.', "Funziona solo nel tuo browser, con gli elenchi di parole dell'integrazione. In Home Assistant, SmartLists ricorda anche le tue correzioni e l'ordine delle corsie per negozio.", 'Działa tylko w twojej przeglądarce, z listami słów integracji. W Home Assistant SmartLists zapamiętuje też twoje poprawki i kolejność alejek w sklepie.'),
    "Deine Test-Liste": ('Your test list', "Ta liste d'essai", 'Tu lista de prueba', 'La tua lista di prova', 'Twoja lista testowa'),
    "Leeren": ('Clear', 'Vider', 'Vaciar', 'Svuota', 'Wyczyść'),
    "Mit + oder Enter landet der Artikel hier – sortiert nach Kategorie.": ('With + or Enter the item lands here – sorted by category.', "Avec + ou Entrée, l'article arrive ici – trié par catégorie.", 'Con + o Intro el artículo aparece aquí – ordenado por categoría.', "Con + o Invio l'articolo arriva qui – ordinato per categoria.", 'Po + lub Enter produkt trafia tutaj – posortowany według kategorii.'),
    "🥬 Obst & Gemüse": ('🥬 Fruit & veg', '🥬 Fruits & légumes', '🥬 Frutas y verduras', '🥬 Frutta e verdura', '🥬 Owoce i warzywa'),
    "🥩 Fleisch- & Fischtheke": ('🥩 Meat & fish', '🥩 Viande & poisson', '🥩 Carne y pescado', '🥩 Carne e pesce', '🥩 Mięso i ryby'),
    "🥛 Kühlung": ('🥛 Chilled & dairy', '🥛 Frais & produits laitiers', '🥛 Refrigerados y lácteos', '🥛 Freschi e latticini', '🥛 Nabiał i chłodzone'),
    "🥫 Konserven & Trockensortiment": ('🥫 Pantry & tins', '🥫 Épicerie & conserves', '🥫 Despensa y conservas', '🥫 Dispensa e scatolame', '🥫 Spiżarnia i konserwy'),
    "🍞 Brot & Backwaren": ('🍞 Bread & bakery', '🍞 Pain & boulangerie', '🍞 Pan y bollería', '🍞 Pane e prodotti da forno', '🍞 Pieczywo'),
    "🥤 Getränke": ('🥤 Drinks', '🥤 Boissons', '🥤 Bebidas', '🥤 Bevande', '🥤 Napoje'),
    "🍫 Süßwaren & Snacks": ('🍫 Sweets & snacks', '🍫 Confiserie & snacks', '🍫 Dulces y snacks', '🍫 Dolci e snack', '🍫 Słodycze i przekąski'),
    "🧹 Haushalt": ('🧹 Household', '🧹 Entretien', '🧹 Hogar y limpieza', '🧹 Casa e pulizia', '🧹 Chemia domowa'),
    "🧴 Drogerie": ('🧴 Personal care', '🧴 Hygiène & beauté', '🧴 Higiene y belleza', '🧴 Igiene e bellezza', '🧴 Drogeria'),
    "❄️ Tiefkühl": ('❄️ Frozen', '❄️ Surgelés', '❄️ Congelados', '❄️ Surgelati', '❄️ Mrożonki'),
    "🐕 Tierbedarf": ('🐕 Pets', '🐕 Animaux', '🐕 Mascotas', '🐕 Animali', '🐕 Zwierzęta'),
    "📦 Sonstiges": ('📦 Other', '📦 Autres', '📦 Otros', '📦 Altro', '📦 Inne'),
    # drei Produkte, Neu in 4.0
    "Neu in 4.0": ('New in 4.0', 'Nouveau dans la 4.0', 'Novedades de la 4.0', 'Novità della 4.0', 'Nowości w 4.0'),
    "Die größte Überarbeitung bisher – zuerst als Beta: in HACS „Beta-Versionen anzeigen“ einschalten.": ('The biggest overhaul so far – first as a beta: switch on "Show beta versions" in HACS.', "La plus grande refonte à ce jour – d'abord en bêta : active « Afficher les versions bêta » dans HACS.", 'La mayor renovación hasta ahora – primero como beta: activa «Mostrar versiones beta» en HACS.', 'La revisione più grande finora – prima in beta: attiva «Mostra versioni beta» in HACS.', 'Największa przebudowa do tej pory – najpierw jako beta: włącz „Pokaż wersje beta” w HACS.'),
    "Neues Listen-Design": ('New list design', 'Nouveau design de liste', 'Nuevo diseño de lista', 'Nuovo design della lista', 'Nowy wygląd listy'),
    "Anzahl und Größe fest markiert, getönte Kategorien zum Einklappen, Badges unter dem Namen – auch auf der geteilten Seite.": ('Count and size clearly marked, tinted categories that collapse, badges below the name – on the shared page too.', 'Nombre et taille bien marqués, catégories teintées repliables, badges sous le nom – aussi sur la page partagée.', 'Cantidad y tamaño bien marcados, categorías coloreadas plegables, insignias bajo el nombre – también en la página compartida.', 'Numero e formato ben evidenziati, categorie colorate richiudibili, badge sotto il nome – anche nella pagina condivisa.', 'Liczba i wielkość wyraźnie oznaczone, kolorowe zwijane kategorie, odznaki pod nazwą – także na udostępnionej stronie.'),
    "Angebots-Karte": ('Offers card', 'Carte des promos', 'Tarjeta de ofertas', 'Scheda offerte', 'Karta promocji'),
    "Supermarkt-Angebote, abgeglichen mit deiner Liste. Ein gewähltes Angebot steht als Badge am Artikel, abgelaufene räumst du mit einem Tipp weg.": ('Supermarket offers matched with your list. A chosen offer shows as a badge on the item; expired ones are cleared with one tap.', "Les promos des supermarchés, comparées à ta liste. Une promo choisie s'affiche en badge sur l'article ; les promos expirées s'enlèvent d'un tap.", 'Ofertas del supermercado comparadas con tu lista. La oferta elegida aparece como insignia en el artículo; las caducadas se quitan con un toque.', "Offerte dei supermercati confrontate con la tua lista. L'offerta scelta compare come badge sull'articolo; quelle scadute si tolgono con un tocco.", 'Promocje z marketów dopasowane do twojej listy. Wybrana promocja widnieje jako odznaka przy produkcie; wygasłe usuwasz jednym dotknięciem.'),
    "Teilen-Links bearbeiten": ('Edit share links', 'Modifier les liens de partage', 'Editar enlaces compartidos', 'Modifica i link di condivisione', 'Edycja linków udostępniania'),
    "Rechte, Laufzeit und Passwort nachträglich ändern – der Link und der QR-Code bleiben gleich.": ('Change rights, duration and password afterwards – the link and the QR code stay the same.', 'Modifie droits, durée et mot de passe après coup – le lien et le QR code restent les mêmes.', 'Cambia permisos, duración y contraseña después – el enlace y el código QR siguen igual.', 'Cambia permessi, durata e password in seguito – il link e il codice QR restano gli stessi.', 'Zmień uprawnienia, czas i hasło później – link i kod QR pozostają te same.'),
    "Währung wählbar": ('Choose your currency', 'Devise au choix', 'Moneda a elegir', 'Valuta a scelta', 'Wybór waluty'),
    "Franken, Pfund, Złoty und weitere – für Preise, Summe und Ausgaben, auch beim Eintippen erkannt.": ('Francs, pounds, złoty and more – for prices, total and expenses, also recognised while typing.', "Francs, livres, złoty et d'autres – pour les prix, le total et les dépenses, reconnus aussi à la saisie.", 'Francos, libras, złoty y más – para precios, total y gastos, también reconocidos al escribir.', 'Franchi, sterline, złoty e altre – per prezzi, totale e spese, riconosciute anche durante la digitazione.', 'Franki, funty, złote i inne – dla cen, sumy i wydatków, rozpoznawane także przy wpisywaniu.'),
    "Preis-Verlauf": ('Price history', 'Historique des prix', 'Historial de precios', 'Cronologia prezzi', 'Historia cen'),
    "Was ein Artikel wann und wo gekostet hat. Ob der letzte Preis automatisch wieder eingetragen wird, entscheidest du.": ('What an item cost, when and where. Whether the last price is filled in again automatically is up to you.', "Ce qu'un article a coûté, quand et où. À toi de décider si le dernier prix est repris automatiquement.", 'Cuánto costó un artículo, cuándo y dónde. Tú decides si el último precio se rellena de nuevo automáticamente.', "Quanto è costato un articolo, quando e dove. Decidi tu se l'ultimo prezzo viene reinserito automaticamente.", 'Ile kosztował produkt, kiedy i gdzie. Sam decydujesz, czy ostatnia cena ma być wpisywana automatycznie.'),
    "Aufgeräumte Einstellungen": ('Tidier settings', 'Réglages mieux rangés', 'Ajustes más ordenados', 'Impostazioni più ordinate', 'Uporządkowane ustawienia'),
    "Klar gegliedert, mit eigener Reihenfolge der Badges und besserer Ansicht am Smartphone.": ('Clearly structured, with your own badge order and a better view on the smartphone.', 'Clairement structurés, avec ton propre ordre des badges et un meilleur affichage sur smartphone.', 'Bien estructurados, con tu propio orden de insignias y mejor vista en el smartphone.', 'Ben strutturate, con il tuo ordine dei badge e una vista migliore su smartphone.', 'Przejrzyście ułożone, z własną kolejnością odznak i lepszym widokiem na smartfonie.'),
    "Liste nach Kategorie im neuen Design": ('List by category in the new design', 'Liste par catégorie, nouveau design', 'Lista por categoría con el nuevo diseño', 'Lista per categoria nel nuovo design', 'Lista według kategorii w nowym wyglądzie'),
    "Einkaufsmodus mit Markt-Leiste": ('Shopping mode with store bar', 'Mode courses avec barre des magasins', 'Modo compra con barra de tiendas', 'Modalità spesa con barra dei negozi', 'Tryb zakupów z paskiem sklepów'),
    "Geteilte Seite für Leute ohne Konto": ('Shared page for people without an account', 'Page partagée pour les personnes sans compte', 'Página compartida para personas sin cuenta', 'Pagina condivisa per chi non ha un account', 'Udostępniona strona dla osób bez konta'),
    "Angebote für deine Liste": ('Offers for your list', 'Promos pour ta liste', 'Ofertas para tu lista', 'Offerte per la tua lista', 'Promocje dla twojej listy'),
    "Zusammen mit der Angebots-Karte": ('Together with the offers card', 'Avec la carte des promos', 'Junto con la tarjeta de ofertas', 'Insieme alla scheda offerte', 'Razem z kartą promocji'),
    "Die SmartDiscounts Card ist in SmartLists 4.0 schon enthalten. Sie zeigt, welche Artikel deiner Liste gerade im Angebot sind – und wo am günstigsten.": ('The SmartDiscounts Card is already included in SmartLists 4.0. It shows which items on your list are on offer right now – and where they are cheapest.', 'La SmartDiscounts Card est déjà incluse dans SmartLists 4.0. Elle montre quels articles de ta liste sont en promo – et où ils sont le moins chers.', 'La SmartDiscounts Card ya viene incluida en SmartLists 4.0. Muestra qué artículos de tu lista están en oferta – y dónde son más baratos.', 'La SmartDiscounts Card è già inclusa in SmartLists 4.0. Mostra quali articoli della tua lista sono in offerta – e dove costano meno.', 'SmartDiscounts Card jest już częścią SmartLists 4.0. Pokazuje, które produkty z listy są teraz w promocji – i gdzie najtaniej.'),
    "Zur Angebots-Karte →": ('To the offers card →', 'Vers la carte des promos →', 'A la tarjeta de ofertas →', 'Alla scheda offerte →', 'Do karty promocji →'),
    "Dashboard-Karte · läuft auch ohne SmartLists": ('Dashboard card · also works without SmartLists', 'Carte de tableau de bord · fonctionne aussi sans SmartLists', 'Tarjeta de panel · también funciona sin SmartLists', 'Scheda dashboard · funziona anche senza SmartLists', 'Karta dashboardu · działa też bez SmartLists'),
    "Die Angebote deiner Supermärkte, abgeglichen mit deiner Einkaufsliste: für jeden Artikel siehst du, wo er gerade im Angebot ist – und wo am günstigsten.": ("Your supermarkets' offers matched with your shopping list: for every item you see where it is on offer right now – and where it is cheapest.", 'Les promos de tes supermarchés, comparées à ta liste de courses : pour chaque article, tu vois où il est en promo – et où il est le moins cher.', 'Las ofertas de tus supermercados comparadas con tu lista de la compra: para cada artículo ves dónde está en oferta – y dónde es más barato.', 'Le offerte dei tuoi supermercati confrontate con la lista della spesa: per ogni articolo vedi dove è in offerta – e dove costa meno.', 'Promocje z twoich marketów dopasowane do listy zakupów: przy każdym produkcie widzisz, gdzie jest w promocji – i gdzie najtaniej.'),
    "Kostenlos · Open Source (MIT) · braucht nur Angebots-Sensoren · in SmartLists 4.0 schon enthalten": ('Free · open source (MIT) · only needs offer sensors · already included in SmartLists 4.0', 'Gratuit · open source (MIT) · ne nécessite que des capteurs de promos · déjà inclus dans SmartLists 4.0', 'Gratis · código abierto (MIT) · solo necesita sensores de ofertas · ya incluido en SmartLists 4.0', 'Gratis · open source (MIT) · servono solo sensori delle offerte · già incluso in SmartLists 4.0', 'Za darmo · open source (MIT) · wymaga tylko sensorów promocji · już zawarte w SmartLists 4.0'),
    "Merkliste": ('Watch list', 'À surveiller', 'Seguimiento', "Da tenere d'occhio", 'Obserwowane'),
    "Das kann die Karte": ('What the card does', 'Ce que fait la carte', 'Lo que hace la tarjeta', 'Cosa fa la scheda', 'Co potrafi karta'),
    "Meine Liste": ('My list', 'Ma liste', 'Mi lista', 'La mia lista', 'Moja lista'),
    "Zu jedem offenen Artikel die passenden Angebote je Markt, das günstigste mit ★. „Günstigste wählen“ oder „nur REWE“ gilt für die ganze Liste. Vier Ansichten, von Kacheln bis Tabelle.": ('For every open item the matching offers per store, the cheapest marked ★. "Pick cheapest" or "only REWE" applies to the whole list. Four views, from tiles to table.', 'Pour chaque article ouvert, les promos correspondantes par magasin, la moins chère avec ★. « Choisir les moins chères » ou « seulement REWE » vaut pour toute la liste. Quatre vues, des tuiles au tableau.', 'Para cada artículo pendiente, las ofertas de cada tienda, la más barata con ★. «Elegir las más baratas» o «solo REWE» vale para toda la lista. Cuatro vistas, de mosaico a tabla.', 'Per ogni articolo aperto le offerte per negozio, la più conveniente con ★. «Scegli le più convenienti» o «solo REWE» vale per tutta la lista. Quattro viste, dalle tessere alla tabella.', 'Dla każdego otwartego produktu pasujące promocje z każdego sklepu, najtańsza z ★. „Wybierz najtańsze” lub „tylko REWE” działa na całą listę. Cztery widoki, od kafelków po tabelę.'),
    "Alle Angebote": ('All offers', 'Toutes les promos', 'Todas las ofertas', 'Tutte le offerte', 'Wszystkie promocje'),
    "Ein Regal je Markt mit Suche und Kategorien – als Kacheln oder als Liste mit kleinen Bildern. Ein Tipp setzt ein Angebot auf die Liste.": ('One shelf per store with search and categories – as tiles or as a list with small images. One tap puts an offer on the list.', 'Un rayon par magasin avec recherche et catégories – en tuiles ou en liste avec petites images. Un tap ajoute une promo à la liste.', 'Un estante por tienda con búsqueda y categorías – en mosaico o en lista con imágenes pequeñas. Un toque añade una oferta a la lista.', "Uno scaffale per negozio con ricerca e categorie – a riquadri o come elenco con piccole immagini. Un tocco mette un'offerta in lista.", 'Półka dla każdego sklepu z wyszukiwaniem i kategoriami – jako kafelki lub lista z małymi zdjęciami. Jedno dotknięcie dodaje promocję do listy.'),
    "Was du nur im Angebot kaufst: Die Karte zeigt, wo es gerade günstig ist, und sagt auf Wunsch Bescheid.": ('What you only buy on offer: the card shows where it is cheap right now and lets you know if you like.', "Ce que tu n'achètes qu'en promo : la carte montre où c'est avantageux en ce moment et te prévient si tu veux.", 'Lo que solo compras en oferta: la tarjeta muestra dónde está barato ahora y te avisa si quieres.', 'Quello che compri solo in offerta: la scheda mostra dove conviene adesso e ti avvisa se vuoi.', 'To, co kupujesz tylko w promocji: karta pokazuje, gdzie jest teraz tanio, i na życzenie daje znać.'),
    "In die Liste übernehmen": ('Apply to the list', 'Reporter dans la liste', 'Pasar a la lista', 'Riporta nella lista', 'Przenieś na listę'),
    "Schreibt Markt, Preis und Gültigkeit an den Eintrag: mit SmartLists als Badge, sonst als lesbare Zeile in der Beschreibung.": ('Writes store, price and validity to the entry: as a badge with SmartLists, otherwise as a readable line in the description.', "Inscrit magasin, prix et validité sur l'entrée : en badge avec SmartLists, sinon en ligne lisible dans la description.", 'Anota tienda, precio y validez en la entrada: como insignia con SmartLists, si no como línea legible en la descripción.', 'Scrive negozio, prezzo e validità sulla voce: come badge con SmartLists, altrimenti come riga leggibile nella descrizione.', 'Zapisuje sklep, cenę i ważność przy wpisie: z SmartLists jako odznakę, w innym razie jako czytelny wiersz w opisie.'),
    "Abgelaufene Angebote": ('Expired offers', 'Promos expirées', 'Ofertas caducadas', 'Offerte scadute', 'Wygasłe promocje'),
    "Ist ein übernommenes Angebot vorbei, weist die Karte darauf hin – entfernen oder später erinnern.": ('When an applied offer is over, the card points it out – remove it or be reminded later.', 'Quand une promo reportée est terminée, la carte le signale – la retirer ou se le faire rappeler plus tard.', 'Cuando una oferta aplicada ha terminado, la tarjeta lo avisa – quitarla o recordarlo más tarde.', "Quando un'offerta riportata è finita, la scheda lo segnala – rimuovila o fatti avvisare più tardi.", 'Gdy przeniesiona promocja się skończy, karta o tym przypomni – usuń ją lub wróć do tego później.'),
    "Deine Sensoren": ('Your sensors', 'Tes capteurs', 'Tus sensores', 'I tuoi sensori', 'Twoje sensory'),
    "Erkennt die Integrationen für REWE, EDEKA, Lidl, ALDI und Norma von selbst. Eigene REST- oder Template-Sensoren ordnest du Feld für Feld zu.": ('Recognises the integrations for REWE, EDEKA, Lidl, ALDI and Norma by itself. Your own REST or template sensors are mapped field by field.', "Reconnaît d'elle-même les intégrations REWE, EDEKA, Lidl, ALDI et Norma. Tes propres capteurs REST ou template s'associent champ par champ.", 'Reconoce por sí sola las integraciones de REWE, EDEKA, Lidl, ALDI y Norma. Tus propios sensores REST o de plantilla se asignan campo a campo.', 'Riconosce da sola le integrazioni per REWE, EDEKA, Lidl, ALDI e Norma. I tuoi sensori REST o template si associano campo per campo.', 'Sama rozpoznaje integracje REWE, EDEKA, Lidl, ALDI i Norma. Własne sensory REST lub szablonowe przypisujesz pole po polu.'),
    "Meine Liste: Preise der Märkte nebeneinander": ('My list: store prices side by side', 'Ma liste : prix des magasins côte à côte', 'Mi lista: precios de las tiendas lado a lado', 'La mia lista: prezzi dei negozi affiancati', 'Moja lista: ceny sklepów obok siebie'),
    "Meine Liste: ein Angebot je Zeile": ('My list: one offer per row', 'Ma liste : une promo par ligne', 'Mi lista: una oferta por fila', "La mia lista: un'offerta per riga", 'Moja lista: jedna promocja w wierszu'),
    "Alle Angebote als Liste": ('All offers as a list', 'Toutes les promos en liste', 'Todas las ofertas en lista', 'Tutte le offerte come elenco', 'Wszystkie promocje jako lista'),
    "Konfiguration": ('Configuration', 'Configuration', 'Configuración', 'Configurazione', 'Konfiguracja'),
    "Eine Zeile genügt. Alles Weitere ist optional – alle Optionen und Felder stehen in der Doku auf GitHub.": ('One line is enough. Everything else is optional – all options and fields are in the docs on GitHub.', 'Une ligne suffit. Tout le reste est facultatif – toutes les options et tous les champs sont dans la doc sur GitHub.', 'Basta una línea. Todo lo demás es opcional – todas las opciones y campos están en la documentación de GitHub.', 'Basta una riga. Tutto il resto è facoltativo – tutte le opzioni e i campi sono nella documentazione su GitHub.', 'Wystarczy jedna linia. Reszta jest opcjonalna – wszystkie opcje i pola są w dokumentacji na GitHubie.'),
    "Noch besser mit SmartLists": ('Even better with SmartLists', 'Encore mieux avec SmartLists', 'Aún mejor con SmartLists', 'Ancora meglio con SmartLists', 'Jeszcze lepiej z SmartLists'),
    "Mit der Integration erscheint das gewählte Angebot als Badge am Artikel, der Einkaufsmodus sortiert nach Markt, und die Karte ist ohne eigene Installation dabei.": ('With the integration the chosen offer appears as a badge on the item, the shopping mode sorts by store, and the card comes without a separate installation.', "Avec l'intégration, la promo choisie apparaît en badge sur l'article, le mode courses trie par magasin et la carte est fournie sans installation séparée.", 'Con la integración, la oferta elegida aparece como insignia en el artículo, el modo compra ordena por tienda y la tarjeta viene sin instalación aparte.', "Con l'integrazione l'offerta scelta compare come badge sull'articolo, la modalità spesa ordina per negozio e la scheda è inclusa senza installazione separata.", 'Z integracją wybrana promocja pojawia się jako odznaka przy produkcie, tryb zakupów sortuje według sklepu, a karta jest dołączona bez osobnej instalacji.'),
    "Zu SmartLists →": ('To SmartLists →', 'Vers SmartLists →', 'A SmartLists →', 'A SmartLists →', 'Do SmartLists →'),
    "Angebots-Sensoren einrichten": ('Set up offer sensors', 'Configurer les capteurs de promos', 'Configurar sensores de ofertas', 'Configura i sensori delle offerte', 'Skonfiguruj sensory promocji'),
    "Zum Beispiel die Integrationen ha-rewe, ha-edeka oder ha-lidl – oder ein eigener Sensor.": ('For example the integrations ha-rewe, ha-edeka or ha-lidl – or a sensor of your own.', 'Par exemple les intégrations ha-rewe, ha-edeka ou ha-lidl – ou ton propre capteur.', 'Por ejemplo las integraciones ha-rewe, ha-edeka o ha-lidl – o un sensor propio.', 'Ad esempio le integrazioni ha-rewe, ha-edeka o ha-lidl – oppure un tuo sensore.', 'Na przykład integracje ha-rewe, ha-edeka lub ha-lidl – albo własny sensor.'),
    ", Typ „Dashboard“.": (', type "Dashboard".', ', type « Dashboard ».', ', tipo «Dashboard».', ', tipo «Dashboard».', ', typ „Dashboard”.'),
    "Karte einfügen": ('Add the card', 'Ajouter la carte', 'Añadir la tarjeta', 'Aggiungi la scheda', 'Dodaj kartę'),
    "Im Dashboard „SmartDiscounts Card“ wählen und die Einkaufsliste angeben. Mit SmartLists 4.0 entfallen Schritt 2 und die Ressource.": ('Pick "SmartDiscounts Card" in the dashboard and enter the shopping list. With SmartLists 4.0 you can skip step 2 and the resource.', "Choisis « SmartDiscounts Card » dans le tableau de bord et indique la liste de courses. Avec SmartLists 4.0, l'étape 2 et la ressource sont inutiles.", 'Elige «SmartDiscounts Card» en el panel e indica la lista de la compra. Con SmartLists 4.0 sobran el paso 2 y el recurso.', 'Scegli «SmartDiscounts Card» nella dashboard e indica la lista della spesa. Con SmartLists 4.0 il passo 2 e la risorsa non servono.', 'Wybierz „SmartDiscounts Card” w dashboardzie i wskaż listę zakupów. Z SmartLists 4.0 krok 2 i zasób są zbędne.'),
    "Nie wieder ein Angebot verpassen": ('Never miss an offer again', 'Ne rate plus aucune promo', 'No te pierdas ninguna oferta', "Non perdere più un'offerta", 'Nie przegap żadnej promocji'),
    "Die ganze Einkaufsliste in Home Assistant?": ('The whole shopping list in Home Assistant?', 'Toute la liste de courses dans Home Assistant ?', '¿Toda la lista de la compra en Home Assistant?', 'Tutta la lista della spesa in Home Assistant?', 'Cała lista zakupów w Home Assistant?'),
    "SmartDiscounts Card:": ('SmartDiscounts Card:', 'SmartDiscounts Card :', 'SmartDiscounts Card:', 'SmartDiscounts Card:', 'SmartDiscounts Card:'),
    "Drei Bausteine": ('Three building blocks', 'Trois briques', 'Tres piezas', 'Tre componenti', 'Trzy elementy'),
    "Einzeln oder zusammen nutzbar.": ('Use them on their own or together.', 'À utiliser seules ou ensemble.', 'Se usan por separado o juntas.', 'Da usare da soli o insieme.', 'Do użycia osobno lub razem.'),
    "Was es ist": ('What it is', "Ce que c'est", 'Qué es', "Che cos'è", 'Co to jest'),
    "Integration, Karte und eigene Seite": ('Integration, card and its own page', 'Intégration, carte et page dédiée', 'Integración, tarjeta y página propia', 'Integrazione, scheda e pagina dedicata', 'Integracja, karta i własna strona'),
    "Dashboard-Karte": ('Dashboard card', 'Carte de tableau de bord', 'Tarjeta de panel', 'Scheda dashboard', 'Karta dashboardu'),
    "App (bald)": ('App (soon)', 'Appli (bientôt)', 'App (pronto)', 'App (presto)', 'Aplikacja (wkrótce)'),
    "Braucht SmartLists": ('Needs SmartLists', 'Nécessite SmartLists', 'Necesita SmartLists', 'Richiede SmartLists', 'Wymaga SmartLists'),
    "nein": ('no', 'non', 'no', 'no', 'nie'),
    "Kategorien, Badges, Einkaufsmodus": ('Categories, badges, shopping mode', 'Catégories, badges, mode courses', 'Categorías, insignias, modo compra', 'Categorie, badge, modalità spesa', 'Kategorie, odznaki, tryb zakupów'),
    "Supermarkt-Angebote": ('Supermarket offers', 'Promos des supermarchés', 'Ofertas del supermercado', 'Offerte dei supermercati', 'Promocje z marketów'),
    "✓ (Karte enthalten)": ('✓ (card included)', '✓ (carte incluse)', '✓ (tarjeta incluida)', '✓ (scheda inclusa)', '✓ (karta w zestawie)'),
    "Teilen per Link": ('Share by link', 'Partage par lien', 'Compartir por enlace', 'Condivisione tramite link', 'Udostępnianie linkiem'),
    "MIT, kostenlos": ('MIT, free', 'MIT, gratuit', 'MIT, gratis', 'MIT, gratis', 'MIT, za darmo'),
    "proprietär": ('proprietary', 'propriétaire', 'propietaria', 'proprietaria', 'własnościowa'),
    "Zum Beispiel die REWE-Integration ha-rewe von FaserF – oder ein eigener Sensor.": ("For example FaserF's REWE integration ha-rewe – or a sensor of your own.", "Par exemple l'intégration REWE ha-rewe de FaserF – ou ton propre capteur.", 'Por ejemplo la integración de REWE ha-rewe de FaserF – o un sensor propio.', "Ad esempio l'integrazione REWE ha-rewe di FaserF – oppure un tuo sensore.", 'Na przykład integracja REWE ha-rewe od FaserF – albo własny sensor.'),
    "Erkennt Angebots-Sensoren von selbst, z. B. die REWE-Integration ha-rewe von FaserF. Eigene REST- oder Template-Sensoren ordnest du Feld für Feld zu.": ("Recognises offer sensors by itself, e.g. FaserF's REWE integration ha-rewe. Your own REST or template sensors are mapped field by field.", "Reconnaît d'elle-même les capteurs de promos, p. ex. l'intégration REWE ha-rewe de FaserF. Tes propres capteurs REST ou template s'associent champ par champ.", 'Reconoce por sí sola los sensores de ofertas, p. ej. la integración de REWE ha-rewe de FaserF. Tus propios sensores REST o de plantilla se asignan campo a campo.', "Riconosce da sola i sensori delle offerte, ad es. l'integrazione REWE ha-rewe di FaserF. I tuoi sensori REST o template si associano campo per campo.", 'Sama rozpoznaje sensory promocji, np. integrację REWE ha-rewe od FaserF. Własne sensory REST lub szablonowe przypisujesz pole po polu.'),
    "Empfohlene Integrationen": ('Recommended integrations', 'Intégrations recommandées', 'Integraciones recomendadas', 'Integrazioni consigliate', 'Polecane integracje'),
    "Danke, FaserF!": ('Thank you, FaserF!', 'Merci, FaserF !', '¡Gracias, FaserF!', 'Grazie, FaserF!', 'Dziękujemy, FaserF!'),
    "Die Karte bringt selbst keine Angebots-Daten mit – sie zeigt, was Sensoren in deinem Home Assistant liefern. Dafür empfehlen wir die Integrationen von FaserF.": ('The card does not bring any offer data itself – it shows what sensors in your Home Assistant deliver. For that we recommend the integrations by FaserF.', "La carte n'apporte pas elle-même de données de promos – elle affiche ce que fournissent les capteurs de ton Home Assistant. Pour cela, nous recommandons les intégrations de FaserF.", 'La tarjeta no trae datos de ofertas por sí misma: muestra lo que entregan los sensores de tu Home Assistant. Para eso recomendamos las integraciones de FaserF.', 'La scheda non porta dati sulle offerte: mostra ciò che forniscono i sensori del tuo Home Assistant. Per questo consigliamo le integrazioni di FaserF.', 'Karta sama nie dostarcza danych o promocjach – pokazuje to, co dostarczają sensory w twoim Home Assistant. Polecamy do tego integracje FaserF.'),
    "Alle Projekte von FaserF": ('All projects by FaserF', 'Tous les projets de FaserF', 'Todos los proyectos de FaserF', 'Tutti i progetti di FaserF', 'Wszystkie projekty FaserF'),
    "Preisvergleich über mehrere Märkte – fasst die Markt-Integrationen zusammen und zeigt je Suchbegriff den besten Preis.": ('Price comparison across several stores – aggregates the store integrations and shows the best price per search term.', 'Comparaison de prix entre plusieurs magasins – regroupe les intégrations des magasins et affiche le meilleur prix par mot-clé.', 'Comparación de precios entre varias tiendas: agrupa las integraciones de las tiendas y muestra el mejor precio por término de búsqueda.', 'Confronto prezzi tra più negozi: riunisce le integrazioni dei negozi e mostra il prezzo migliore per termine di ricerca.', 'Porównanie cen w kilku sklepach – łączy integracje sklepów i pokazuje najlepszą cenę dla szukanego hasła.'),
    "Wochenangebote, Bonuspunkte und Rabatte.": ('Weekly offers, bonus points and discounts.', 'Promos de la semaine, points bonus et remises.', 'Ofertas semanales, puntos y descuentos.', 'Offerte settimanali, punti bonus e sconti.', 'Oferty tygodnia, punkty i rabaty.'),
    "Wochenangebote, Rabatte und PAYBACK-Karte.": ('Weekly offers, discounts and PAYBACK card.', 'Promos de la semaine, remises et carte PAYBACK.', 'Ofertas semanales, descuentos y tarjeta PAYBACK.', 'Offerte settimanali, sconti e carta PAYBACK.', 'Oferty tygodnia, rabaty i karta PAYBACK.'),
    "Lidl Plus: Wochenangebote, Coupons und digitale Kassenbons.": ('Lidl Plus: weekly offers, coupons and digital receipts.', 'Lidl Plus : promos de la semaine, coupons et tickets de caisse numériques.', 'Lidl Plus: ofertas semanales, cupones y tickets digitales.', 'Lidl Plus: offerte settimanali, coupon e scontrini digitali.', 'Lidl Plus: oferty tygodnia, kupony i cyfrowe paragony.'),
    "ALDI Süd und ALDI Nord: Wochenprospekte.": ('ALDI Süd and ALDI Nord: weekly flyers.', 'ALDI Süd et ALDI Nord : prospectus de la semaine.', 'ALDI Süd y ALDI Nord: folletos semanales.', 'ALDI Süd e ALDI Nord: volantini settimanali.', 'ALDI Süd i ALDI Nord: gazetki tygodniowe.'),
    "Wochenangebote und Prospekt.": ('Weekly offers and flyer.', 'Promos de la semaine et prospectus.', 'Ofertas semanales y folleto.', 'Offerte settimanali e volantino.', 'Oferty tygodnia i gazetka.'),
    "Digitale Kassenbons (eBons) und Treuepunkte.": ('Digital receipts (eBons) and loyalty points.', 'Tickets de caisse numériques (eBons) et points de fidélité.', 'Tickets digitales (eBons) y puntos de fidelidad.', 'Scontrini digitali (eBons) e punti fedeltà.', 'Cyfrowe paragony (eBons) i punkty lojalnościowe.'),
    "HA SmartLists und die Discounts Card sind eigenständige Projekte und nicht mit FaserF oder den genannten Märkten verbunden.": ('HA SmartLists and the Discounts Card are independent projects and not affiliated with FaserF or the stores mentioned.', 'HA SmartLists et la Discounts Card sont des projets indépendants, sans lien avec FaserF ni avec les magasins cités.', 'HA SmartLists y la Discounts Card son proyectos independientes, sin relación con FaserF ni con las tiendas mencionadas.', 'HA SmartLists e la Discounts Card sono progetti indipendenti, non collegati a FaserF né ai negozi citati.', 'HA SmartLists i Discounts Card to niezależne projekty, niezwiązane z FaserF ani z wymienionymi sklepami.'),
    "Zum Beispiel eine der empfohlenen Integrationen von FaserF – oder ein eigener Sensor.": ('For example one of the recommended integrations by FaserF – or a sensor of your own.', 'Par exemple une des intégrations recommandées de FaserF – ou ton propre capteur.', 'Por ejemplo una de las integraciones recomendadas de FaserF – o un sensor propio.', 'Ad esempio una delle integrazioni consigliate di FaserF – oppure un tuo sensore.', 'Na przykład jedna z polecanych integracji FaserF – albo własny sensor.'),
    "Erkennt Angebots-Sensoren von selbst, z. B. die der empfohlenen Integrationen von FaserF. Eigene REST- oder Template-Sensoren ordnest du Feld für Feld zu.": ('Recognises offer sensors by itself, e.g. those of the recommended integrations by FaserF. Your own REST or template sensors are mapped field by field.', "Reconnaît d'elle-même les capteurs de promos, p. ex. ceux des intégrations recommandées de FaserF. Tes propres capteurs REST ou template s'associent champ par champ.", 'Reconoce por sí sola los sensores de ofertas, p. ej. los de las integraciones recomendadas de FaserF. Tus propios sensores REST o de plantilla se asignan campo a campo.', 'Riconosce da sola i sensori delle offerte, ad es. quelli delle integrazioni consigliate di FaserF. I tuoi sensori REST o template si associano campo per campo.', 'Sama rozpoznaje sensory promocji, np. z polecanych integracji FaserF. Własne sensory REST lub szablonowe przypisujesz pole po polu.'),
    "Bisher ohne Prospekt-Angebote.": ("No flyer offers so far.", "Pas encore de promos de prospectus.", "Por ahora sin ofertas de folleto.", "Finora senza offerte da volantino.", "Na razie bez ofert z gazetki."),
    "Das ist die echte Karte mit Beispieldaten – zum Ausprobieren: Reiter und Ansicht wechseln, Angebote wählen, auf die Liste setzen.": ('This is the real card with sample data – try it: switch tabs and views, pick offers, put them on the list.', "Voici la vraie carte avec des données d'exemple – à essayer : change d'onglet et de vue, choisis des promos, ajoute-les à la liste.", 'Esta es la tarjeta real con datos de ejemplo – pruébala: cambia de pestaña y de vista, elige ofertas, añádelas a la lista.', 'Questa è la scheda vera con dati di esempio – provala: cambia scheda e vista, scegli le offerte, mettile in lista.', 'To prawdziwa karta z przykładowymi danymi – wypróbuj: zmieniaj zakładki i widok, wybierz promocje, dodaj je do listy.'),
}
KEEP |= {'Grocery Deals', 'ha-grocery-deals', 'ha-rewe', 'ha-edeka', 'ha-lidl', 'ha-aldi', 'ha-norma', 'ha-penny', 'EDEKA', 'Lidl', 'ALDI', 'Norma', 'PENNY', 'Home Assistant', 'Android', '🏷️ Discounts Card', 'https://github.com/m3m0rex/ha_smartdiscounts-card', '🛒 SmartLists', '· MIT', 'type: custom:smartdiscounts-card\nlist: todo.einkauf\nsources:\n  - auto\n  - entity: sensor.mein_markt\n    store: Kaufland\n    map:\n      name: product.name\n      price: prices.current\n      old_price: prices.regular\n      image: images.0.url\n      until: validity.to\nmatch: word\nlist_view: rows\nall_view: list', 'SmartDiscounts Card'}

LANG_IDX = {lang: i for i, lang in enumerate(LANGS)}
ATTR = re.compile(r'\b(alt|title|aria-label|content)="([^"]*)"')
TEXT = re.compile(r">([^<]+)<")


def translate(src: str, lang: str, missing: set[str]) -> str:
    i = LANG_IDX[lang]

    def tr(text: str) -> str:
        core = text.strip()
        if not core or not re.search(r"[A-Za-zÄÖÜäöüß]{2}", core) or core in KEEP:
            return text
        if core not in T:
            missing.add(core)
            return text
        lead, trail = text[: len(text) - len(text.lstrip())], text[len(text.rstrip()):]
        return lead + T[core][i] + trail

    head, sep, rest = src.partition("<body")
    head = re.sub(r"<title>([^<]*)</title>", lambda m: f"<title>{tr(m.group(1))}</title>", head)
    head = ATTR.sub(lambda m: f'{m.group(1)}="{tr(m.group(2))}"' if m.group(1) == "content" and "description" in head[max(0, m.start() - 40):m.start()] else m.group(0), head)
    body_html, script_sep, script = rest.partition("<script>")
    body_html = TEXT.sub(lambda m: ">" + tr(m.group(1)) + "<", body_html)
    body_html = ATTR.sub(lambda m: f'{m.group(1)}="{tr(m.group(2))}"', body_html)
    return head + sep + body_html + script_sep + script


def page(lang: str, missing: set[str]) -> str:
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    out = translate(src, lang, missing)
    out = out.replace('<html lang="de">', f'<html lang="{lang}">', 1)
    # Pfade aus dem Unterordner
    out = out.replace('src="assets/', 'src="../assets/').replace('href="assets/', 'href="../assets/').replace('href="LICENSE.md"', 'href="../LICENSE.md"')
    out = out.replace("demo-de.gif", "demo.gif")
    # Sprachauswahl: Pfade relativ zum Unterordner, aktuelle Sprache gewählt
    out = out.replace('value="./" data-lang="de" selected', 'value="../" data-lang="de"')
    for other in LANGS:
        out = out.replace(f'value="{other}/" data-lang="{other}"', f'value="../{other}/" data-lang="{other}"' + (" selected" if other == lang else ""))
    return out


def main() -> int:
    missing: set[str] = set()
    for lang in LANGS:
        d = ROOT / lang
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(lang, missing), encoding="utf-8")
    if missing:
        print("Noch ohne Übersetzung (bleibt deutsch):")
        for m in sorted(missing):
            print("  -", m)
    print("fertig:", ", ".join(f"{lang}/index.html" for lang in LANGS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
