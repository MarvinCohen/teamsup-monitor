"""
utils/scorer.py — Moteur de scoring TeamsUp
Score 0-100 basé sur la pertinence pour TeamsUp.
Cas d'usage prioritaire : joueur manquant, annulation évitée, recherche de partenaires.
"""

# ──────────────────────────────────────────────
# Mots-clés haute valeur — exactement le problème que TeamsUp résout
# ──────────────────────────────────────────────
HIGH_VALUE_KEYWORDS = [
    # Joueur manquant — cas d'usage #1
    "joueur manquant", "joueur de dernière minute", "il nous manque",
    "on manque d'un joueur", "cherche joueur", "recherche joueur",
    "manque un joueur", "besoin d'un joueur", "joueur supplémentaire",
    "on est pas complet", "équipe incomplète", "match annulé faute",
    "annulation match", "annuler le match", "match annulé",
    "trouver un joueur", "trouver des joueurs", "joueur last minute",
    # Sports ciblés + recherche
    "five joueur", "five complet", "foot à 5", "football à 5",
    "padel partenaire", "padel joueur", "cherche partenaire padel",
    "tennis partenaire", "cherche partenaire tennis",
    "basket joueur", "volley joueur", "handball joueur",
    "badminton partenaire", "cherche partenaire badminton",
    # App / solution
    "trouver équipe", "rejoindre équipe", "rejoindre match",
    "application sport", "app sport", "plateforme sport",
]

# ──────────────────────────────────────────────
# Mots-clés pertinents — signal fort lié à l'usage TeamsUp
# ──────────────────────────────────────────────
RELEVANT_KEYWORDS = [
    # Sports ciblés
    "five", "foot", "football", "padel", "tennis", "basket", "basketball",
    "volleyball", "volley", "handball", "badminton",
    # Contexte amateur / loisir
    "amateur", "loisir", "match amical", "sport loisir", "sport amateur",
    "équipe amateur", "club amateur",
    # Organisateurs / tournois
    "tournoi", "tournois", "organiser match", "organisation match",
    "inscriptions", "inscription tournoi",
    # Recherche de joueurs
    "cherche", "recherche", "besoin", "disponible", "dispo",
    "ce soir", "ce week-end", "samedi", "dimanche", "demain",
    # Problèmes fréquents
    "désistement", "forfait", "absent", "remplaçant", "remplacement",
]

# ──────────────────────────────────────────────
# Mots-clés signal faible — contexte sport général
# ──────────────────────────────────────────────
WEAK_KEYWORDS = [
    "sport", "sports", "match", "matches", "matchs", "jeu", "jouer",
    "terrain", "salle", "gymnase", "complexe sportif",
    "équipe", "équipes", "team", "joueur", "joueurs",
    "Paris", "Lyon", "Marseille", "Bordeaux", "Nantes",
]

# ──────────────────────────────────────────────
# Mots-clés hors-sujet — pénalité
# ──────────────────────────────────────────────
OFFTOPIC_KEYWORDS = [
    "professionnel", "ligue 1", "ligue des champions", "champions league",
    "transfert", "mercato", "salaire joueur", "coupe du monde",
    "équipe nationale", "sélection", "fifa", "uefa",
    "blessure grave", "dopage", "scandale",
]

QUESTION_SIGNALS = [
    "?", "comment", "aide", "conseil", "help", "besoin",
    "quelqu'un", "someone", "anyone", "disponible", "dispo",
]


def normalize(text: str) -> str:
    """Normalise le texte pour un matching flexible."""
    text = text.lower()
    replacements = {
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a", "ä": "a",
        "ù": "u", "û": "u", "ü": "u",
        "î": "i", "ï": "i",
        "ô": "o", "ö": "o",
        "ç": "c",
    }
    for accented, plain in replacements.items():
        text = text.replace(accented, plain)
    return text


def count_keyword_matches(text: str, keywords: list[str]) -> int:
    """Compte les mots-clés présents dans le texte."""
    normalized_text = normalize(text)
    return sum(1 for kw in keywords if normalize(kw) in normalized_text)


def score_post(post: dict) -> int:
    """
    Calcule le score de pertinence d'un post pour TeamsUp (0-100).
    Focus sur : joueur manquant, annulation, recherche de partenaires.
    """
    full_text = f"{post.get('title', '')} {post.get('body', '')}"

    score = 0

    # Haute valeur (max 60 pts)
    high_matches = min(count_keyword_matches(full_text, HIGH_VALUE_KEYWORDS), 3)
    score += high_matches * 20

    # Pertinent (max 30 pts)
    relevant_matches = min(count_keyword_matches(full_text, RELEVANT_KEYWORDS), 3)
    score += relevant_matches * 10

    # Signal faible (max 10 pts)
    weak_matches = min(count_keyword_matches(full_text, WEAK_KEYWORDS), 2)
    score += weak_matches * 5

    # Bonus question / demande urgente (+10)
    for signal in QUESTION_SIGNALS:
        if signal in full_text.lower():
            score += 10
            break

    # Bonus engagement Reddit
    upvotes = post.get("upvotes", 0)
    comments = post.get("num_comments", 0)
    if upvotes > 50 or comments > 10:
        score += 10
    elif upvotes > 10 or comments > 3:
        score += 5

    # Malus hors-sujet
    if count_keyword_matches(full_text, OFFTOPIC_KEYWORDS) > 0:
        score -= 30

    return max(0, min(100, score))
