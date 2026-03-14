import requests
import sqlite3
import time
import logging
import os
from datetime import datetime

# ============================================
# TES INFORMATIONS TELEGRAM
# ============================================

TELEGRAM_TOKEN = "8142414797:AAHW8tNIsrncPLNsruNO0aZUbspto7Nj2Ys"
TELEGRAM_CHAT_ID = "5741568179"

INTERVAL_SECONDES = 3

# ============================================
# TES ALERTES
# ============================================

ALERTES = [

    {
        "nom": "Rick Owens",
        "brand_id": 145654,
        "prix_min": None,
        "prix_max": None,
    },

    {
        "nom": "Ann Demeulemeester",
        "brand_id": 51445,
        "prix_min": None,
        "prix_max": None,
    },

    {
        "nom": "Isaac Sellam",
        "brand_id": 393343,
        "prix_min": None,
        "prix_max": None,
    },

    {
        "nom": "Mon profil",
        "user_id": 0,
        "prix_min": None,
        "prix_max": None,
    }

]

# ============================================
# LOGS
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

logger = logging.getLogger(__name__)

DB_PATH = 'vinted_alerts.db'

# ============================================
# HEADERS NAVIGATEUR
# ============================================

CHROME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Origin': 'https://www.vinted.fr',
    'Referer': 'https://www.vinted.fr/',
}

# ============================================
# BASE DE DONNÉES
# ============================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles_vus (
        vinted_id TEXT,
        nom_alerte TEXT,
        titre TEXT,
        trouve_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (vinted_id, nom_alerte)
    )''')
    conn.commit()
    conn.close()


def reset_db():
    logger.warning("Base de données corrompue — réinitialisation complète")
    try:
        os.remove(DB_PATH)
    except Exception as e:
        logger.error(f"Impossible de supprimer la DB : {e}")
    init_db()


def article_deja_vu(vinted_id, nom_alerte):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'SELECT 1 FROM articles_vus WHERE vinted_id=? AND nom_alerte=?',
            (str(vinted_id), nom_alerte)
        )
        existe = c.fetchone() is not None
        conn.close()
        return existe
    except sqlite3.DatabaseError:
        try:
            conn.close()
        except:
            pass
        reset_db()
        return False


def marquer_article_vu(vinted_id, nom_alerte, titre):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO articles_vus (vinted_id, nom_alerte, titre) VALUES (?,?,?)',
            (str(vinted_id), nom_alerte, titre)
        )
        conn.commit()
        conn.close()
    except sqlite3.DatabaseError:
        try:
            conn.close()
        except:
            pass
        reset_db()
    except Exception as e:
        logger.error(f"Erreur inattendue dans marquer_article_vu : {e}")

# ============================================
# TELEGRAM
# ============================================

def envoyer_telegram(message, photo_url=None):
    try:
        if photo_url:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            requests.post(url, json={
                'chat_id': TELEGRAM_CHAT_ID,
                'photo': photo_url,
                'caption': message,
                'parse_mode': 'HTML'
            })
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            })
    except Exception as e:
        logger.error(f"Erreur Telegram: {e}")

# ============================================
# SESSION VINTED
# ============================================

def creer_session_vinted():
    session = requests.Session()
    session.headers.update(CHROME_HEADERS)
    try:
        session.get('https://www.vinted.fr', timeout=15)
        logger.info("Session Vinted créée")
    except Exception as e:
        logger.error(f"Erreur session: {e}")
    return session

# ============================================
# RECHERCHE
# ============================================

def chercher_par_brand_id(session, brand_id, prix_min=None, prix_max=None):
    params = {
        'brand_ids[]': brand_id,
        'order': 'newest_first',
        'per_page': 20,
    }
    if prix_min:
        params["price_from"] = prix_min
    if prix_max:
        params["price_to"] = prix_max
    try:
        response = session.get(
            "https://www.vinted.fr/api/v2/catalog/items",
            params=params,
            timeout=15
        )
        if response.status_code == 200:
            return response.json().get("items", [])
        elif response.status_code == 429:
            logger.warning("Rate limit Vinted (429) — pause 60s")
            time.sleep(60)
    except Exception as e:
        logger.error(f"Erreur réseau brand_id {brand_id}: {e}")
    return []


def chercher_par_user_id(session, user_id, prix_min=None, prix_max=None):
    params = {
        'user_ids[]': user_id,
        'order': 'newest_first',
        'per_page': 20,
    }
    if prix_min:
        params["price_from"] = prix_min
    if prix_max:
        params["price_to"] = prix_max
    try:
        response = session.get(
            "https://www.vinted.fr/api/v2/catalog/items",
            params=params,
            timeout=15
        )
        if response.status_code == 200:
            return response.json().get("items", [])
        elif response.status_code == 429:
            logger.warning("Rate limit Vinted (429) — pause 60s")
            time.sleep(60)
    except Exception as e:
        logger.error(f"Erreur réseau user_id {user_id}: {e}")
    return []

# ============================================
# FORMATAGE ARTICLE
# ============================================

def formater_article(article, nom_alerte):
    titre = article.get("title", "")
    prix = article.get("price", {}).get("amount", "?")
    vid = str(article.get("id"))
    lien = f"https://www.vinted.fr/items/{vid}"
    photos = article.get("photos", [])
    photo_url = photos[0].get("url", "") if photos else ""
    message = (
        f"🎯 <b>{nom_alerte}</b>\n\n"
        f"{titre}\n"
        f"💰 {prix}€\n\n"
        f"{lien}"
    )
    return {
        "vid": vid,
        "titre": titre,
        "message": message,
        "photo_url": photo_url
    }

# ============================================
# CROSS-CHECK
# ============================================

def cross_check_et_notifier(article, nom_alerte_source):
    brand_id_article = article.get("brand_id")
    user_id_article = article.get("user", {}).get("id")
    vid = str(article.get("id"))

    for alerte in ALERTES:
        nom = alerte["nom"]
        if nom == nom_alerte_source:
            continue
        match = False
        if "brand_id" in alerte and alerte["brand_id"] == brand_id_article:
            match = True
        if "user_id" in alerte and alerte["user_id"] == user_id_article:
            match = True
        if match and not article_deja_vu(vid, nom):
            infos = formater_article(article, nom)
            marquer_article_vu(vid, nom, infos["titre"])
            logger.info(f"NOUVEAU [{nom}] (cross-check depuis {nom_alerte_source}) : {infos['titre']}")
            envoyer_telegram(infos["message"], infos["photo_url"])

# ============================================
# TRAITEMENT DES ARTICLES
# ============================================

def traiter_articles(articles, nom_alerte):
    for article in articles:
        vid = str(article.get("id"))
        if article_deja_vu(vid, nom_alerte):
            continue
        infos = formater_article(article, nom_alerte)
        marquer_article_vu(infos["vid"], nom_alerte, infos["titre"])
        logger.info(f"NOUVEAU [{nom_alerte}] : {infos['titre']}")
        envoyer_telegram(infos["message"], infos["photo_url"])
        cross_check_et_notifier(article, nom_alerte)

# ============================================
# BOUCLE PRINCIPALE
# ============================================

def boucle_principale():
    init_db()
    envoyer_telegram("🟢 Bot Vinted démarré")
    session = creer_session_vinted()
    compteur = 0
    erreurs_consecutives = 0

    while True:
        try:
            if compteur > 0 and compteur % 500 == 0:
                logger.info("Renouvellement de la session Vinted...")
                session = creer_session_vinted()

            for alerte in ALERTES:
                nom = alerte["nom"]
                prix_min = alerte.get("prix_min")
                prix_max = alerte.get("prix_max")
                logger.info(f"Recherche : {nom}")

                if "brand_id" in alerte:
                    articles = chercher_par_brand_id(session, alerte["brand_id"], prix_min, prix_max)
                elif "user_id" in alerte:
                    articles = chercher_par_user_id(session, alerte["user_id"], prix_min, prix_max)
                else:
                    articles = []

                traiter_articles(articles, nom)

            erreurs_consecutives = 0
            compteur += 1
            time.sleep(INTERVAL_SECONDES)

        except Exception as e:
            erreurs_consecutives += 1
            logger.error(f"Erreur inattendue (#{erreurs_consecutives}) : {e}")
            envoyer_telegram(f"⚠️ Erreur bot : {e}")

            if erreurs_consecutives >= 5:
                logger.info("Trop d'erreurs — renouvellement de session forcé")
                session = creer_session_vinted()
                erreurs_consecutives = 0

            time.sleep(30)

# ============================================

if __name__ == "__main__":
    boucle_principale()