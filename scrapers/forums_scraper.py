"""
scrapers/forums_scraper.py — Scraper Google News RSS pour TeamsUp
Recherches très ciblées par sport, ville et cas d'usage.
"""

import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

GOOGLE_NEWS_FEEDS = [
    # ── Joueur manquant — cas d'usage #1 ──
    {
        "name": "Google News — joueur manquant five",
        "url": "https://news.google.com/rss/search?q=joueur+manquant+five+foot&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — cherche joueur ce soir",
        "url": "https://news.google.com/rss/search?q=%22cherche+joueur%22+%22ce+soir%22&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — il nous manque joueur",
        "url": "https://news.google.com/rss/search?q=%22il+nous+manque%22+joueur+match&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — match annulé faute joueurs",
        "url": "https://news.google.com/rss/search?q=%22match+annul%C3%A9%22+%22faute+de+joueurs%22&hl=fr&gl=FR&ceid=FR:fr",
    },
    # ── Par sport ──
    {
        "name": "Google News — cherche joueur padel",
        "url": "https://news.google.com/rss/search?q=%22cherche+joueur%22+padel&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — cherche partenaire tennis",
        "url": "https://news.google.com/rss/search?q=%22cherche+partenaire%22+tennis+amateur&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — cherche joueur basket handball",
        "url": "https://news.google.com/rss/search?q=%22cherche+joueur%22+basket+handball+amateur&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — cherche joueur badminton volley",
        "url": "https://news.google.com/rss/search?q=%22cherche+joueur%22+badminton+volley+amateur&hl=fr&gl=FR&ceid=FR:fr",
    },
    # ── Par ville ──
    {
        "name": "Google News — sport amateur Paris joueur",
        "url": "https://news.google.com/rss/search?q=sport+amateur+Paris+cherche+joueur&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — sport amateur Lyon joueur",
        "url": "https://news.google.com/rss/search?q=sport+amateur+Lyon+cherche+joueur&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — sport amateur Marseille joueur",
        "url": "https://news.google.com/rss/search?q=sport+amateur+Marseille+cherche+joueur&hl=fr&gl=FR&ceid=FR:fr",
    },
    # ── Tournois ──
    {
        "name": "Google News — tournoi amateur inscription",
        "url": "https://news.google.com/rss/search?q=tournoi+amateur+inscription+%C3%A9quipe+sport&hl=fr&gl=FR&ceid=FR:fr",
    },
    {
        "name": "Google News — application trouver joueur sport",
        "url": "https://news.google.com/rss/search?q=application+trouver+joueur+sport+amateur&hl=fr&gl=FR&ceid=FR:fr",
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
