"""
monitor.py — Agent de monitoring TeamsUp
Surveille Reddit, Google News et forums sport pour détecter les discussions
pertinentes : joueurs manquants, annulations, recherche de partenaires.
Envoie une alerte Discord avec les meilleures opportunités.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from scrapers.reddit_scraper import scrape_reddit
from scrapers.forums_scraper import scrape_forums
from utils.scorer import score_post
from utils.discord_notifier import send_discord_digest


# Seuil de pertinence (0-100)
THRESHOLD = 30

# Cache des posts déjà vus
CACHE_FILE = "seen_posts.json"


def load_cache() -> set:
    """Charge les IDs de posts déjà vus depuis le cache JSON."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_cache(seen_ids: set):
    """Sauvegarde le cache des posts déjà vus."""
    ids_list = list(seen_ids)[-2000:]
    with open(CACHE_FILE, "w") as f:
        json.dump(ids_list, f)


def make_post_id(post: dict) -> str:
    """Génère un identifiant unique pour un post à partir de son URL."""
    return hashlib.md5(post["url"].encode()).hexdigest()


def is_french(post: dict) -> bool:
    """Filtre pour garder uniquement les posts en français."""
    french_signals = [
        "joueur", "joueurs", "match", "équipe", "sport", "terrain",
        "five", "padel", "tennis", "foot", "football", "basket", "volley",
        "handball", "badminton", "annul", "manque", "cherche", "recherche",
        "pour ", "avec ", "dans ", "sur ", "une ", "des ", "les ",
        "est ", "sont ", "mon ", "ma ", "mes ", "je ", "nous ",
    ]
    text = f"{post.get('title', '')} {post.get('body', '')}".lower()
    matches = sum(1 for s in french_signals if s in text)
    return matches >= 2


def run():
    """Point d'entrée principal : scrape, score, filtre, notifie."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Démarrage du monitoring TeamsUp...")

    seen_ids = load_cache()
    all_posts = []

    print("→ Scraping Reddit...")
    all_posts += scrape_reddit()

    print("→ Scraping Forums & Google News...")
    all_posts += scrape_forums()

    print(f"  {len(all_posts)} posts récupérés au total.")

    new_relevant = []

    for post in all_posts:
        post_id = make_post_id(post)

        if post_id in seen_ids:
            continue

        seen_ids.add(post_id)
        post["score"] = score_post(post)

        if post["score"] >= THRESHOLD and is_french(post):
            new_relevant.append(post)

    new_relevant.sort(key=lambda p: p["score"], reverse=True)

    print(f"  {len(new_relevant)} posts pertinents trouvés (seuil: {THRESHOLD}).")

    if new_relevant:
        send_discord_digest(new_relevant)
        print(f"  ✓ Alerte Discord envoyée pour {len(new_relevant)} posts.")
    else:
        print("  Aucun nouveau post pertinent. Pas d'alerte envoyée.")

    save_cache(seen_ids)
    print("  ✓ Cache mis à jour.")


if __name__ == "__main__":
    run()
