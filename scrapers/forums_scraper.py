"""
scrapers/forums_scraper.py — Scraper Google News RSS pour TeamsUp
Surveille les actualités et discussions sport via Google News RSS.
Ciblé sur les cas d'usage TeamsUp : joueurs manquants, annulations, recherche.
"""

import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

GOOGLE_NEWS_FEEDS = [
    {
        "name": "Google News — joueur manquant foot",
        "url": "https://news.google.com/rss/search?q=joueur+manquant+football+five&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — cherche joueur padel",
        "url": "https://news.google.com/rss/search?q=cherche+joueur+padel+tennis&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — sport amateur annulation",
        "url": "https://news.google.com/rss/search?q=sport+amateur+annulation+match+joueur&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — football five Paris",
        "url": "https://news.google.com/rss/search?q=football+five+paris+joueur+%C3%A9quipe&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — padel France amateur",
        "url": "https://news.google.com/rss/search?q=padel+france+amateur+partenaire&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — sport collectif application",
        "url": "https://news.google.com/rss/search?q=sport+collectif+application+trouver+joueur&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — tournoi amateur football basket",
        "url": "https://news.google.com/rss/search?q=tournoi+amateur+football+basket+inscription&hl=fr&gl=FR&ceid=FR:fr",
    },
]

HEADERS = {
    "User-Agent": "TeamsUpMonitor/1.0 RSS Reader"
}


def scrape_forums() -> list[dict]:
    """
    Récupère les derniers articles via Google News RSS sport FR.
    Retourne une liste de dicts normalisés.
    """
    posts = []

    for feed in GOOGLE_NEWS_FEEDS:
        try:
            response = requests.get(feed["url"], headers=HEADERS, timeout=15)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            for item in root.findall(".//item"):
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")

                title = title_el.text if title_el is not None else ""
                url = link_el.text if link_el is not None else ""
                body = desc_el.text if desc_el is not None else ""

                if not title or len(title) < 10:
                    continue

                posts.append({
                    "title": title,
                    "body": body[:300] if body else "",
                    "url": url,
                    "source": feed["name"],
                    "author": "",
                    "created_at": datetime.now(timezone.utc).timestamp(),
                    "upvotes": 0,
                    "num_comments": 0,
                })

            time.sleep(1)

        except requests.RequestException as e:
            print(f"    [Google News] Erreur sur {feed['name']}: {e}")
            continue
        except ET.ParseError as e:
            print(f"    [Google News] Erreur XML: {e}")
            continue

    print(f"    [Forums/News] {len(posts)} articles récupérés.")
    return posts
