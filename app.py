import requests
import time
import logging
import os
import json
import psycopg2
import threading
from datetime import datetime

TELEGRAM_TOKEN = "8142414797:AAHW8tNIsrncPLNsruNO0aZUbspto7Nj2Ys"
TELEGRAM_CHAT_ID = "5741568179"
INTERVAL_SECONDES = 5
DATABASE_URL = os.environ.get("DATABASE_URL")

ALERTES = [
    {"nom": "Rick Owens", "brand_id": 145654, "prix_min": None, "prix_max": None},
    {"nom": "Ann Demeulemeester", "brand_id": 51445, "prix_min": None, "prix_max": None},
    {"nom": "Isaac Sellam", "brand_id": 393343, "prix_min": None, "prix_max": None},
    {"nom": "Mon profil", "user_id": 160573709, "prix_min": None, "prix_max": None},
]

# Tokens Vinted — a renouveler manuellement depuis Chrome DevTools si expires
# (DevTools -> Application -> Cookies -> vinted.fr)
VINTED_TOKENS = {
    "refresh_token": "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhY2NvdW50X2lkIjozNzA2Mzc3OSwiYXBwX2lkIjo0LCJhdWQiOiJmci5jb3JlLmFwaSIsImNsaWVudF9pZCI6IndlYiIsImV4cCI6MTc3NDMwNjYwNywiaWF0IjoxNzczNzAxODA3LCJpc3MiOiJ2aW50ZWQtaWFtLXNlcnZpY2UiLCJsb2dpbl90eXBlIjozLCJwdXJwb3NlIjoicmVmcmVzaCIsInNjb3BlIjoidXNlciIsInNpZCI6IjM5NWMyNjNiLTE3NzE1OTY0MTAiLCJzdWIiOiI1NTM5MjQ4NiIsImNjIjoiRlIiLCJhbmlkIjoiYWIyM2VkZGMtMmJiNi00NGM2LWE1MjEtMmU2YzBmMzVhZTBiIiwiYWN0Ijp7InN1YiI6IjU1MzkyNDg2In19.HcmY3o4lqKNd1Uh4kwyyjOwfI2e0lcxYNRzFgimBN9HhtXmTDTRVuB9fdIurH2X1cXzQelbfeuoJspcN7yYkMiKrfnntBn-Ts3Ii2GsNBt58DCCklV96j0XiZv3szV7WUbEPs2TpCRkgaVBk0HyvFf4R5ld_PVc6FFzzFCQyR6N2vQSsR3jOldjJqyG8rbLnham6RHNYpqpEeqlw1kozoC2YeqYsC5-K4lteT3YIqcFmL_rS6dPK0AGLcqnrIvwpRpZ0M4vxTwK9Hhq1iW0T3jR-Pm62D5BevsbDz0b6wuYLGXYTX0eK4IG1ZnsL3ao8ccXzk_v0u3WOPsiNGU-79Q",
    "access_token": "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhY2NvdW50X2lkIjozNzA2Mzc3OSwiYXBwX2lkIjo0LCJhdWQiOiJmci5jb3JlLmFwaSIsImNsaWVudF9pZCI6IndlYiIsImV4cCI6MTc3MzcwOTAwNywiaWF0IjoxNzczNzAxODA3LCJpc3MiOiJ2aW50ZWQtaWFtLXNlcnZpY2UiLCJsb2dpbl90eXBlIjozLCJwdXJwb3NlIjoiYWNjZXNzIiwic2NvcGUiOiJ1c2VyIiwic2lkIjoiMzk1YzI2M2ItMTc3MTU5NjQxMCIsInN1YiI6IjU1MzkyNDg2IiwiY2MiOiJGUiIsImFuaWQiOiJhYjIzZWRkYy0yYmI2LTQ0YzYtYTUyMS0yZTZjMGYzNWFlMGIiLCJhY3QiOnsic3ViIjoiNTUzOTI0ODYifX0.tKAHT_SHsH6i9oTayeu1fXBPcVLZgxYE4MfzB61UHLXGuJFa3QalIt2d0CmXx-TnYB49Bz6sX6npEIEHiHLQtK-MSfFkVPH5pFj4vzbkf53tjgGsgFI3zY2DP6nteGNhZ8BojLzdzWiSo-UGJYiR5sGJO6iLuV1Lv1m8jrg8AjmyuZy3e8OhzKrSRkhFjbLK14y9ujv4M977xqjcbu_uIjEU6vZ4Dw-2HO5JQ7IpjRydZgi5wySXC-KEziZaY6Zik6NnOmGWNNfr_RpobaF53XumlxruiAuo3XBmXZWlHfBFwpXP-BximMfe9H25DMq-EEd6HQm59twzG7N5S70SKA",
    "session": "bzJra3QrcWFxbzMxRThzRmlJLzJhK3lmUVN1L3IxWWNWcjFNS0Nua0RQR05nREVOa2xnNGJNdUZ2YVpaU2JyRXptT3lVMUp5ck5qVHc0Mk55YXhYTTZEV2lNMkJRSkhtZ2NPNXFwL0I1TmNLQzhCZDc3YnlGNURNT0duemF4ZmwwNlk5S1dzaWFLYWZDdXhHa3hJdndVM2kzQyt5UXE0VHJ6alVEVm83ZFZZUURFVUF6RnBsZkQrQzJTZEdTbWZIZWhPanVXTy9UUlZkT0U1S09pTUZTOGlId3p1dVdDUjM3Y3BWRml1allna1FVMW5mZmJicjM2MVZsNkpQb1FmNk1VS0VTeTNyU0RidTRtK1pVOVB3ZGtLbDZFMHBsbmRSRnI0NStwc2Q0K050SGkzS2pzV1dUYlVJanFoN0lWcXotLVUxMWRWb0JHd3NTUzBRY2ZkWWNWNWc9PQ==--34ee1cf1a40849e0b6030d755c1a5e7c3b611bad",
    "cf_clearance": "lvykSBBuDeKGIbmJcs.iczqn3q7TacwVU1t2phgn40k-1773701809-1.2.1.1-2occXASM7dbPcxy0oTt5SLvijaQVB4T.loFDKsI6EgdOnIyVP7bOm1E99ygL5YKB0TMu9XuaQ4t3HvMlLv5tzt5gIIvKdUqtqV_zYudiFkS2yWZKczvNS2LT4b9lUPkTJMFL4OVLRzRiC3xnlvJJsWhqSOPmAfHncIbTxX4Gpz05nber0udkU3nfQK.kyIYoWoSNQNkdAr8_0tvcNHuJ3ZuIpanP.MbSM.imU0NwgS4",
    "datadome": "X~gxBVEY9zRGHL3kdw1ljeqt_Ou01M1cAwt~q4RX9s_8NHZsa3FSm8pCtEpF5jrhTi~nYiwiEtrgD7N_whYbLVH_u0V1N4aoKjkp6mvFHuQ4mnyG47llU7Jm899igbXb",
}

POINTS_RELAIS = [
    {"nom": "Locker Rain X Wash Bondoufle", "uuid": "7d5b16ac-cc4c-4398-b07e-fbf8ac74c725", "rate_uuid": "abe64f67-389f-4c2b-b270-39c733127c64"},
    {"nom": "Rain x Wash", "uuid": "56ce4063-e960-4f68-adcc-4c2d5610603e", "rate_uuid": "99c3aec2-87a6-4435-b14b-68c376560184"},
    {"nom": "Wash N Dry", "uuid": "7fe02049-a4e6-47de-97bc-2131c78a112e", "rate_uuid": "99c3aec2-87a6-4435-b14b-68c376560184"},
    {"nom": "TLT Rapid Market (DPD)", "uuid": "36455f4f-130a-45ed-bc43-f8f927aee30b", "rate_uuid": "c16d2578-dd8c-4328-9b0c-55f0e8cfb084"},
    {"nom": "TLT Rapid Market (Chronopost)", "uuid": "491d0cc8-1c3e-4117-9833-1be724e5a2b2", "rate_uuid": "c50f3c3e-90c1-4420-b46f-5b35f85c293b"},
    {"nom": "SL Informatique", "uuid": "fd42da4b-fcc6-48d1-bfc7-c7a1b08e32fa", "rate_uuid": "c50f3c3e-90c1-4420-b46f-5b35f85c293b"},
    {"nom": "Chronodrive", "uuid": "3df26c07-3112-4c1c-b143-b08a7685587e", "rate_uuid": "99c3aec2-87a6-4435-b14b-68c376560184"},
    {"nom": "Tabac Le Pepere", "uuid": "196024f1-1bdb-4a2a-8f86-4b1695da1cc1", "rate_uuid": "99c3aec2-87a6-4435-b14b-68c376560184"},
    {"nom": "Monoprix", "uuid": "2fd1ea7e-9a1b-476c-8a9b-5db8fce4c77f", "rate_uuid": "99c3aec2-87a6-4435-b14b-68c376560184"},
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

CHROME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Origin': 'https://www.vinted.fr',
    'Referer': 'https://www.vinted.fr/',
}

LOCAL_ACHAT_URL = "https://unsymmetrized-chiropodical-octavio.ngrok-free.dev"

# ============================================
# BASE DE DONNEES
# ============================================

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles_vus (
        vinted_id TEXT,
        nom_alerte TEXT,
        titre TEXT,
        photo_url TEXT,
        prix TEXT,
        trouve_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (vinted_id, nom_alerte)
    )''')
    c.execute("ALTER TABLE articles_vus ADD COLUMN IF NOT EXISTS photo_url TEXT")
    c.execute("ALTER TABLE articles_vus ADD COLUMN IF NOT EXISTS prix TEXT")
    conn.commit()
    conn.close()
    logger.info("Base de donnees PostgreSQL initialisee")

def article_deja_vu(vinted_id, nom_alerte):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute('SELECT 1 FROM articles_vus WHERE vinted_id=%s AND nom_alerte=%s', (str(vinted_id), nom_alerte))
        existe = c.fetchone() is not None
        conn.close()
        return existe
    except Exception as e:
        logger.error(f"Erreur article_deja_vu : {e}")
        return False

def marquer_article_vu(vinted_id, nom_alerte, titre, photo_url="", prix=""):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            'INSERT INTO articles_vus (vinted_id, nom_alerte, titre, photo_url, prix) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING',
            (str(vinted_id), nom_alerte, titre, photo_url, prix)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur marquer_article_vu : {e}")

# ============================================
# SESSION VINTED (sans proxy)
# ============================================

def creer_session():
    session = requests.Session()
    session.headers.update(CHROME_HEADERS)
    session.headers.update({
        "Authorization": f"Bearer {VINTED_TOKENS['access_token']}",
        "X-Requested-With": "XMLHttpRequest",
    })
    session.cookies.set("access_token_web", VINTED_TOKENS["access_token"], domain=".vinted.fr")
    session.cookies.set("refresh_token_web", VINTED_TOKENS["refresh_token"], domain=".vinted.fr")
    session.cookies.set("_vinted_fr_session", VINTED_TOKENS["session"], domain=".vinted.fr")
    session.cookies.set("cf_clearance", VINTED_TOKENS["cf_clearance"], domain=".vinted.fr")
    session.cookies.set("datadome", VINTED_TOKENS["datadome"], domain=".vinted.fr")
    return session

def renouveler_token(session):
    logger.info("Renouvellement access_token...")
    try:
        r = requests.post(
            "https://www.vinted.fr/api/v2/tokens",
            json={"grant_type": "refresh_token", "refresh_token": VINTED_TOKENS["refresh_token"], "client_id": "web"},
            headers=CHROME_HEADERS,
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("access_token"):
                VINTED_TOKENS["access_token"] = data["access_token"]
                session.headers.update({"Authorization": f"Bearer {VINTED_TOKENS['access_token']}"})
                session.cookies.set("access_token_web", VINTED_TOKENS["access_token"], domain=".vinted.fr")
            if data.get("refresh_token"):
                VINTED_TOKENS["refresh_token"] = data["refresh_token"]
                session.cookies.set("refresh_token_web", VINTED_TOKENS["refresh_token"], domain=".vinted.fr")
            logger.info("Tokens renouveles avec succes")
            return True
        else:
            logger.error(f"Echec renouvellement token : {r.status_code}")
            envoyer_telegram("⚠️ Tokens Vinted expires — va sur vinted.fr dans Chrome, copie les cookies depuis DevTools -> Application -> Cookies et mets a jour le code.")
            return False
    except Exception as e:
        logger.error(f"Erreur renouvellement token : {e}")
        return False

# ============================================
# RECHERCHE (API directe, sans proxy)
# ============================================

def chercher_articles(session, params, nom_alerte):
    try:
        r = session.get(
            "https://www.vinted.fr/api/v2/catalog/items",
            params=params,
            timeout=15
        )
        if r.status_code == 401:
            logger.warning("Token expire, renouvellement...")
            if renouveler_token(session):
                r = session.get(
                    "https://www.vinted.fr/api/v2/catalog/items",
                    params=params,
                    timeout=15
                )
            else:
                return []
        if r.status_code == 200:
            data = r.json()
            return data.get("items", [])
        else:
            logger.warning(f"Erreur API Vinted [{nom_alerte}] : {r.status_code}")
            return []
    except Exception as e:
        logger.error(f"Erreur recherche [{nom_alerte}] : {e}")
        return []

def chercher_par_brand_id(session, brand_id, prix_min=None, prix_max=None, nom_alerte=""):
    params = {"brand_ids[]": brand_id, "order": "newest_first", "per_page": 20}
    if prix_min: params["price_from"] = prix_min
    if prix_max: params["price_to"] = prix_max
    return chercher_articles(session, params, nom_alerte)

def chercher_par_user_id(session, user_id, prix_min=None, prix_max=None, nom_alerte=""):
    params = {"user_ids[]": user_id, "order": "newest_first", "per_page": 20}
    if prix_min: params["price_from"] = prix_min
    if prix_max: params["price_to"] = prix_max
    return chercher_articles(session, params, nom_alerte)

# ============================================
# TELEGRAM
# ============================================

def envoyer_telegram(message, photo_url=None, reply_markup=None):
    try:
        if photo_url:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'photo': photo_url, 'caption': message, 'parse_mode': 'HTML'}
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Erreur Telegram: {e}")

# ============================================
# FORMATAGE
# ============================================

def formater_article(article, nom_alerte):
    titre = article.get("title", "")
    vid = str(article.get("id", "0"))
    lien = f"https://www.vinted.fr/items/{vid}"

    prix_raw = article.get("price", "?")
    if isinstance(prix_raw, dict):
        prix = str(prix_raw.get("amount", "?"))
    else:
        prix = str(prix_raw) if prix_raw else "?"

    photo_url = ""
    photos = article.get("photos", [])
    if photos:
        p = photos[0]
        if isinstance(p, dict):
            for thumb in p.get("thumbnails", []):
                if isinstance(thumb, dict) and thumb.get("width") == 310:
                    photo_url = thumb.get("url", "")
                    break
            if not photo_url:
                photo_url = p.get("url", "")

    message = f"🎯 <b>{nom_alerte}</b>\n\n{titre}\n💰 {prix}€\n\n{lien}"
    reply_markup = {"inline_keyboard": [[{"text": "🛒 Acheter", "callback_data": f"acheter_{vid}"}, {"text": "👁 Voir", "url": lien}]]}
    return {"vid": vid, "titre": titre, "message": message, "photo_url": photo_url, "reply_markup": reply_markup, "prix": prix}

# ============================================
# CROSS-CHECK
# ============================================

def cross_check_et_notifier(article, nom_alerte_source):
    brand_id_article = article.get("brand_id")
    user_raw = article.get("user")
    user_id_article = user_raw.get("id") if isinstance(user_raw, dict) else None
    vid = str(article.get("id", "0"))
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
            marquer_article_vu(vid, nom, infos["titre"], infos["photo_url"], infos["prix"])
            envoyer_telegram(infos["message"], infos["photo_url"], infos["reply_markup"])

def traiter_articles(articles, nom_alerte):
    for article in articles:
        vid = str(article.get("id", "0"))
        if article_deja_vu(vid, nom_alerte):
            continue
        infos = formater_article(article, nom_alerte)
        marquer_article_vu(infos["vid"], nom_alerte, infos["titre"], infos["photo_url"], infos["prix"])
        logger.info(f"NOUVEAU [{nom_alerte}] : {infos['titre']}")
        envoyer_telegram(infos["message"], infos["photo_url"], infos["reply_markup"])
        cross_check_et_notifier(article, nom_alerte)

# ============================================
# ACHAT
# ============================================

def acheter_article(item_id):
    try:
        logger.info(f"Envoi demande achat item {item_id} au Mac local")
        response = requests.post(
            f"{LOCAL_ACHAT_URL}/acheter/{item_id}",
            timeout=35
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("succes", False), data.get("message", "Pas de message")
        return False, f"Erreur serveur local (status {response.status_code})"
    except Exception as e:
        return False, f"Erreur connexion Mac local : {e}"

def traiter_callback_achat(item_id):
    envoyer_telegram(f"⏳ Achat en cours pour l'article {item_id}...")
    succes, message = acheter_article(item_id)
    if succes:
        envoyer_telegram(f"✅ Achat reussi !\n\n{message}")
    else:
        envoyer_telegram(f"❌ Achat echoue : {message}")

# ============================================
# CALLBACKS TELEGRAM
# ============================================

derniere_update_id = None

def verifier_callbacks_telegram():
    global derniere_update_id
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {"limit": 100, "allowed_updates": ["callback_query"]}
        if derniere_update_id is not None:
            params["offset"] = derniere_update_id + 1
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return
        updates = response.json().get("result", [])
        if not updates:
            return
        for update in updates:
            update_id = update.get("update_id")
            if derniere_update_id is None or update_id > derniere_update_id:
                derniere_update_id = update_id
            callback = update.get("callback_query")
            if not callback:
                continue
            callback_id = callback.get("id")
            callback_data = callback.get("data", "")
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery",
                    json={"callback_query_id": callback_id, "text": "⏳ Achat en cours..."},
                    timeout=5
                )
            except:
                pass
            if callback_data.startswith("acheter_"):
                item_id = callback_data.replace("acheter_", "")
                logger.info(f"Callback recu — achat item {item_id}")
                t = threading.Thread(target=traiter_callback_achat, args=(item_id,))
                t.daemon = True
                t.start()
    except Exception as e:
        logger.error(f"Erreur callbacks: {e}")

# ============================================
# BOUCLE PRINCIPALE
# ============================================

def boucle_principale():
    init_db()
    envoyer_telegram("🟢 Bot Vinted demarre (surveillance sans proxy)")
    session = creer_session()
    compteur = 0
    erreurs_consecutives = 0

    while True:
        try:
            verifier_callbacks_telegram()
            for alerte in ALERTES:
                nom = alerte["nom"]
                logger.info(f"Recherche : {nom}")
                if "brand_id" in alerte:
                    articles = chercher_par_brand_id(session, alerte["brand_id"], alerte.get("prix_min"), alerte.get("prix_max"), nom)
                elif "user_id" in alerte:
                    articles = chercher_par_user_id(session, alerte["user_id"], alerte.get("prix_min"), alerte.get("prix_max"), nom)
                else:
                    articles = []
                traiter_articles(articles, nom)
            erreurs_consecutives = 0
            compteur += 1
            time.sleep(INTERVAL_SECONDES)
        except Exception as e:
            erreurs_consecutives += 1
            logger.error(f"Erreur inattendue (#{erreurs_consecutives}) : {e}")
            if erreurs_consecutives >= 5:
                logger.info("5 erreurs consecutives, recreation session...")
                session = creer_session()
                erreurs_consecutives = 0
                time.sleep(30)

if __name__ == "__main__":
    boucle_principale()
