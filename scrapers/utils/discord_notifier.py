"""
utils/discord_notifier.py — Envoi des alertes vers Discord
Utilise les webhooks Discord pour envoyer un digest formaté
avec les discussions sport pertinentes pour TeamsUp.
"""

import os
import json
import requests
from datetime import datetime, timezone

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

SCORE_EMOJI = {
    90: "🔥",
    70: "⚽",
    55: "👀",
    30: "📌",
}


def get_score_emoji(score: int) -> str:
    """Retourne l'emoji correspondant au niveau de score."""
    for threshold, emoji in SCORE_EMOJI.items():
        if score >= threshold:
            return emoji
    return "📌"


def send_discord_digest(posts: list[dict]) -> bool:
    """
    Envoie le digest Discord avec les posts pertinents.
    Discord limite les messages à 2000 caractères — on envoie plusieurs messages si besoin.
    """
    if not DISCORD_WEBHOOK_URL:
        print("    [Discord] DISCORD_WEBHOOK_URL non définie.")
        return False

    now = datetime.now(timezone.utc).strftime("%d/%m/%Y à %Hh%M UTC")
    count = len(posts)
    max_score = max(p["score"] for p in posts) if posts else 0

    # ── Message d'en-tête ──
    header = {
        "embeds": [{
            "title": f"⚽ TeamsUp Monitor — {count} opportunité{'s' if count > 1 else ''} détectée{'s' if count > 1 else ''}",
            "description": (
                f"Rapport du {now} · Meilleur score : **{max_score}/100**\n\n"
                "**Comment répondre ?** Clique sur le lien, lis le contexte, "
                "réponds en apportant de la valeur. Mentionne TeamsUp seulement si c'est naturel."
            ),
            "color": 0x1D9E75,  # Vert TeamsUp
        }]
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(header),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"    [Discord] Erreur envoi header: {e}")
        return False

    # ── Un embed par post (max 10 par message Discord) ──
    # On regroupe par batches de 10
    batch_size = 10
    for i in range(0, len(posts), batch_size):
        batch = posts[i:i + batch_size]
        embeds = []

        for post in batch:
            emoji = get_score_emoji(post["score"])
            title = post["title"][:150] + ("..." if len(post["title"]) > 150 else "")
            source = post["source"]
            score = post["score"]
            url = post["url"]

            description = f"**Source :** {source}\n**Score :** {score}/100"
            if post.get("upvotes", 0) > 0:
                description += f" · ↑{post['upvotes']} · 💬{post['num_comments']}"

            embeds.append({
                "title": f"{emoji} {title}",
                "url": url,
                "description": description,
                "color": 0x378ADD if score >= 70 else 0xBA7517 if score >= 50 else 0x888780,
            })

        payload = {"embeds": embeds}

        try:
            import time
            time.sleep(1)  # Respect rate limit Discord
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"    [Discord] Erreur envoi batch: {e}")
            continue

    return True
