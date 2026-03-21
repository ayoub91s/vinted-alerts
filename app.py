import requests
import time
import logging
import os
import json
import psycopg2
import threading

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

VINTED_TOKENS = {
    "access_token": "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhY2NvdW50X2lkIjozNzA2Mzc3OSwiYXBwX2lkIjo0LCJhdWQiOiJmci5jb3JlLmFwaSIsImNsaWVudF9pZCI6IndlYiIsImV4cCI6MTc3NDA1NzA4MywiaWF0IjoxNzc0MDQ5ODgzLCJpc3MiOiJ2aW50ZWQtaWFtLXNlcnZpY2UiLCJsb2dpbl90eXBlIjozLCJwdXJwb3NlIjoiYWNjZXNzIiwic2NvcGUiOiJ1c2VyIiwic2lkIjoiYzBiZGM0NzYtMTc3Mzc4MTE1OCIsInN1YiI6IjU1MzkyNDg2IiwiY2MiOiJGUiIsImFuaWQiOiJhYjIzZWRkYy0yYmI2LTQ0YzYtYTUyMS0yZTZjMGYzNWFlMGIiLCJhY3QiOnsic3ViIjoiNTUzOTI0ODYifX0.RcCK7wBVR17tpA-U0o5XsFz282yX_GmN9y_ECC98061m2wxmSfJAJYhK0J57IQM0Ca7mPrnCwZ00ajY0q1eiFMhtUUs1l951CJPezzWIJi10f4v_mEPiVhABBnmwaYvqmxyuaPPp-E1E7OJ_FhKaClxN-SlcuMNjkK8QC9XLcrRF-8ZpKdhhl1ed5A7oODtpW-12CMezsjC8CNFIs0TpBk5NlBPPvOnNfC0CQYGFyVQJ0qrPmLA2M4O4ihIb9kPen54G5v9x6eXyLtOLqvoMdX_vakPdx2fR-ufsr7a85y9TQaQVNleS3XvSFC6dPzpb0BHZobehw-X1ZHquw02u8g",
    "refresh_token": "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhY2NvdW50X2lkIjozNzA2Mzc3OSwiYXBwX2lkIjo0LCJhdWQiOiJmci5jb3JlLmFwaSIsImNsaWVudF9pZCI6IndlYiIsImV4cCI6MTc3NDY1NDY4MywiaWF0IjoxNzc0MDQ5ODgzLCJpc3MiOiJ2aW50ZWQtaWFtLXNlcnZpY2UiLCJsb2dpbl90eXBlIjozLCJwdXJwb3NlIjoicmVmcmVzaCIsInNjb3BlIjoidXNlciIsInNpZCI6ImMwYmRjNDc2LTE3NzM3ODExNTgiLCJzdWIiOiI1NTM5MjQ4NiIsImNjIjoiRlIiLCJhbmlkIjoiYWIyM2VkZGMtMmJiNi00NGM2LWE1MjEtMmU2YzBmMzVhZTBiIiwiYWN0Ijp7InN1YiI6IjU1MzkyNDg2In19.BrA3EnEbjziyCI2_QSfbs1NQcCewP2RZ18K_attmUQfJn9Q6tJe00MeI6BLN9lJMaq_-FTHOqFRyS0HfYa5YAKtSNbqm9pLM4erwr60xcnk_tHfhXUmVz_3RfhTeIfTnJpRff0ayjt0WW1EEF-kfK_nQpRv5GOwO_LUsM33dI6E0m0htMgHDOY1UZLuOMbFnB9yqGWmj5k_lExnktB289eYZ8z7hmxGeoawLj-TjWY_k9jr22lwjtoDeKz0P7wLWY2qJ_8vrxmCecH2bT4NLkRjMBnS6_GXmLdxijqEvrvlcb8gl0Qt13LiZkJQLADMiViZxzN2hdbvauVH9gI7gLw",
    "session": "dWltNEoxZXJuVy8wUGhua0pybTNaKzNZYkNiUnF4NDBVcGt5Zjg0QVBuTXFZbFR1eTFJNjlrVHlid2JBazk1NWoxZVVUenUyOWhLYVNVT3VIbk8ralltMWVYRDhXN016VkdFUHhiT1VuVWszRXBPazhDdVJ4VGFLTk0zcHkyS3BDTHhsK3pmdHNIT1VjS2k0WlU3ano3Y3pyQ0RlWVkrT0paaHV1RnpseHJzaE9QZ2QrMExsaTRYOWpRQUliWXFxOXBkQWFEVUUrem5IT1lJTnZ4VWwwRGxPMlhxdFBzWHcwaHR1bkFmR2N2RFBoUXI0Qlg0MXp2dXdOaHdnRjBsSWREbHFLWlo5aktqSTZDYWlFRXBXakxSTTZnRW9KUEltT3ZIcXdqR2l1MU12WHVmeGoxcVhBSzZGYm0zczJ6c2YtLWpPKzdKZE9hMDJGOWFkZEtrZFRCdVE5PQ%3D%3D--a306e0230f3a651402bd4d5ec7aef639c787554d",
    "cf_clearance": "6kBBFpXFtm3oeuA5zQyPULwQxGi2JGValAPDCW9Utd0-1774049882-1.2.1.1-Cxof9bCNlbYIoLVgXvMmkG.YnMYPGXs_.1nJdQO2GLaw.v1zI537Y7.LNhzExftAOuMzMfyzCswRx4psaC_gQ7D6alNIawujn2__tM2TPZa4GcMje8_F4mO0ET9vp6ajMrY4.woT67IA23cYtEzakfXEu2I4r.DwxPAsLOu3cMFCBSxy653PWCMgnU1CpH1zKyb7IqfP2kj9Euok_PgEEkBoh3PkSCam42eHEctttgM",
    "datadome": "VqF9XVeKa67BZpGskLTL_72z0DcknMlfM_NEYmFh8113iA202MgsQEjn12kL9R_2WKed5hz9PBG8WSVK9UcjmyZ5hBZ0ZYWkL_jr~d4cS14L_40nFAT~XXtZC5Mz7dRT",
}

# URL ngrok vers ton Mac (achat via extension Chrome)
LOCAL_ACHAT_URL = "https://unsymmetrized-chiropodical-octavio.ngrok-free.dev"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

CHROME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Origin': 'https://www.vinted.fr',
    'Referer': 'https://www.vinted.fr/',
}

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
    logger.info("Base de donnees initialisee")

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
# SESSION VINTED (surveillance sans proxy)
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
        r = session.post(
            "https://www.vinted.fr/api/v2/auth/token/refresh",
            json={"refresh_token": VINTED_TOKENS["refresh_token"]},
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
            logger.info("Tokens renouveles")
            return True
        else:
            logger.error(f"Echec renouvellement : {r.status_code}")
            envoyer_telegram("⚠️ Tokens expires — copie les 5 cookies depuis Chrome DevTools -> Application -> Cookies -> vinted.fr")
            return False
    except Exception as e:
        logger.error(f"Erreur renouvellement : {e}")
        return False

# ============================================
# RECHERCHE (sans proxy)
# ============================================

def chercher_articles(session, params, nom_alerte):
    try:
        r = session.get("https://www.vinted.fr/api/v2/catalog/items", params=params, timeout=15)
        if r.status_code == 401:
            if renouveler_token(session):
                r = session.get("https://www.vinted.fr/api/v2/catalog/items", params=params, timeout=15)
            else:
                return []
        if r.status_code == 200:
            return r.json().get("items", [])
        logger.warning(f"API Vinted [{nom_alerte}] : {r.status_code}")
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
# ACHAT (via extension Chrome sur ton Mac)
# ============================================

def acheter_article(item_id):
    try:
        logger.info(f"Envoi demande achat item {item_id} au Mac local via ngrok")
        response = requests.post(
            f"{LOCAL_ACHAT_URL}/acheter/{item_id}",
            timeout=35
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("succes", False), data.get("message", "Pas de message")
        return False, f"Erreur serveur local (status {response.status_code})"
    except Exception as e:
        return False, f"Mac local inaccessible (ngrok eteint ou Mac eteint) : {e}"

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
    envoyer_telegram("🟢 Bot Vinted demarre — surveillance active, achat via extension Chrome")
    session = creer_session()
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
            time.sleep(INTERVAL_SECONDES)
        except Exception as e:
            erreurs_consecutives += 1
            logger.error(f"Erreur (#{erreurs_consecutives}) : {e}")
            if erreurs_consecutives >= 5:
                session = creer_session()
                erreurs_consecutives = 0
                time.sleep(30)

if __name__ == "__main__":
    boucle_principale()
