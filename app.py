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
    "session": "dWltNEoxZXJuVy8wUGhua0pybTNaKzNZYkNiUnF4NDBVcGt5Zjg0QVBuTXFZbFR1eTFJNjlrVHlid2JBazk1NWoxZVVUenUyOWhLYVNVT3VIbk8ralltMWVYRDhXN016VkdFUHhiT1VuVWszRXBPazhDdVJ4VGFLTk0zcHkyS3BDTHhsK3pmdHNIT1VjS2k0WlU3ano3Y3pyQ0RlWVkrT0paaHV1RnpseHJzaE9QZ2QrMExsaTRYOWpRQUliWXFxOXBkQWFEVUUrem5IT1lJTnZ4VWwwRGxPMlhxdFBzWHcwaHR1bkFmR2N2RFBoUXI0Qlg0MXp2dXdOaHdnRjBsSWREbHFLWlo5aktqSTZDYWlFRXBXakxSTTZnRW9KUEltT3ZIcXdqR2l1MU12WHVmeGoxcVhBSzZGYm0zczJ6c2YtLWpPKzdKZE9hMDJGOWFkZEtrZFRCdVE9PQ%3D%3D--a306e0230f3a651402bd4d5ec7aef639c787554d",
    "cf_clearance": "6kBBFpXFtm3oeuA5zQyPULwQxGi2JGValAPDCW9Utd0-1774049882-1.2.1.1-Cxof9bCNlbYIoLVgXvMmkG.YnMYPGXs_.1nJdQO2GLaw.v1zI537Y7.LNhzExftAOuMzMfyzCswRx4psaC_gQ7D6alNIawujn2__tM2TPZa4GcMje8_F4mO0ET9vp6ajMrY4.woT67IA23cYtEzakfXEu2I4r.DwxPAsLOu3cMFCBSxy653PWCMgnU1CpH1zKyb7IqfP2kj9Euok_PgEEkBoh3PkSCam42eHEctttgM",
    "datadome": "VqF9XVeKa67BZpGskLTL_72z0DcknMlfM_NEYmFh8113iA202MgsQEjn12kL9R_2WKed5hz9PBG8WSVK9UcjmyZ5hBZ0ZYWkL_jr~d4cS14L_40nFAT~XXtZC5Mz7dRT",
}

# Proxies residentiels francais — uniquement pour l achat
PROXIES_RESIDENTIELS = [
    {"ip": "46.203.41.87", "port": "5588"},
    {"ip": "159.148.239.8", "port": "6560"},
    {"ip": "46.203.86.184", "port": "5684"},
    {"ip": "46.203.76.220", "port": "6720"},
    {"ip": "31.98.8.132", "port": "5810"},
    {"ip": "96.62.193.101", "port": "7810"},
    {"ip": "31.98.9.107", "port": "5285"},
    {"ip": "82.23.57.245", "port": "7499"},
    {"ip": "31.98.8.45", "port": "5723"},
    {"ip": "82.23.57.82", "port": "7336"},
]
PROXY_USER = "xnhxmhza"
PROXY_PASS = "jh4ybh3tobea"
proxy_achat_index = 0

def get_proxy_achat():
    global proxy_achat_index
    p = PROXIES_RESIDENTIELS[proxy_achat_index % len(PROXIES_RESIDENTIELS)]
    proxy_achat_index += 1
    url = f"http://{PROXY_USER}:{PROXY_PASS}@{p['ip']}:{p['port']}"
    return {"http": url, "https": url}

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
# ACHAT (via proxy residentiel)
# ============================================

def creer_session_achat():
    """Session d achat avec proxy residentiel francais."""
    proxies = get_proxy_achat()
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
    session.proxies.update(proxies)
    proxy_ip = list(proxies.values())[0].split("@")[1]
    logger.info(f"Session achat via proxy {proxy_ip}")
    return session

def acheter_article(item_id, tentative=1):
    session = creer_session_achat()
    try:
        # Etape 0 : build — recupere le purchase_id
        logger.info(f"Etape 0 : build pour item {item_id}")
        r0 = session.post(
            "https://www.vinted.fr/api/v2/purchases/checkout/build",
            json={"purchase_items": [{"id": int(item_id), "type": "transaction"}]},
            timeout=20
        )
        logger.info(f"Etape 0 status: {r0.status_code} — {r0.text[:300]}")
        if r0.status_code == 401 and tentative == 1:
            renouveler_token(session)
            return acheter_article(item_id, tentative=2)
        if r0.status_code not in [200, 201]:
            return False, f"Echec etape 0 ({r0.status_code}): {r0.text[:300]}"
        purchase_id = r0.json().get("checkout", {}).get("id")
        if not purchase_id:
            return False, "Purchase ID introuvable"
        logger.info(f"Purchase ID: {purchase_id}")

        # Etape 1 : PUT checkout
        logger.info(f"Etape 1 : PUT checkout {purchase_id}")
        r1 = session.put(
            f"https://www.vinted.fr/api/v2/purchases/{purchase_id}/checkout",
            json={"components": {"item_presentation_escrow_v2": {}, "additional_service": {}, "payment_method": {}, "shipping_address": {}, "shipping_pickup_options": {}, "shipping_pickup_details": {}}},
            timeout=20
        )
        logger.info(f"Etape 1 status: {r1.status_code}")
        if r1.status_code not in [200, 201]:
            return False, f"Echec etape 1 ({r1.status_code}): {r1.text[:300]}"
        checkout1 = r1.json().get("checkout", {})

        # Etape 2 : PATCH point relais
        pickup_types = checkout1.get("components", {}).get("shipping_pickup_details", {}).get("pickup_types", {})
        pickup_options = pickup_types.get("pickup", {}).get("shipping_options", [])
        if not pickup_options:
            pickup_option = checkout1.get("components", {}).get("shipping_pickup_options", {})
            selected_rate_uuid = pickup_option.get("pickup_options", {}).get("pickup", {}).get("selected_rate_uuid")
            point_uuid = pickup_option.get("pickup_options", {}).get("pickup", {}).get("shipping_point", {}).get("uuid")
            point_nom = "defaut"
        else:
            rate_uuids = {opt.get("rate_uuid") for opt in pickup_options}
            point = next((pt for pt in POINTS_RELAIS if pt["rate_uuid"] in rate_uuids), None)
            if point:
                selected_rate_uuid = point["rate_uuid"]
                point_uuid = point["uuid"]
                point_nom = point["nom"]
            else:
                selected_rate_uuid = pickup_options[0].get("rate_uuid")
                point_uuid = None
                point_nom = "premier disponible"

        logger.info(f"Etape 2 : point relais {point_nom}")
        r2 = session.patch(
            f"https://www.vinted.fr/api/v2/purchases/{purchase_id}/checkout",
            json={"components": {"shipping_pickup_options": {"pickup_type": 2}, "shipping_pickup_details": {"selected_rate_uuid": selected_rate_uuid, "shipping_point_uuid": point_uuid}}},
            timeout=20
        )
        logger.info(f"Etape 2 status: {r2.status_code}")
        if r2.status_code not in [200, 201]:
            return False, f"Echec etape 2 ({r2.status_code}): {r2.text[:300]}"
        checksum = r2.json().get("checkout", {}).get("checksum")
        if not checksum:
            return False, "Checksum introuvable"

        # Etape 3 : paiement
        logger.info("Etape 3 : paiement")
        r3 = session.post(
            f"https://www.vinted.fr/api/v2/purchases/{purchase_id}/payment",
            json={"checksum": checksum, "payment_options": {"browser_info": {"language": "fr-FR", "color_depth": 32, "java_enabled": False, "screen_height": 956, "screen_width": 1470, "timezone_offset": -60}}},
            timeout=20
        )
        logger.info(f"Etape 3 status: {r3.status_code} — {r3.text[:300]}")
        if r3.status_code in [200, 201]:
            return True, f"Achete via {point_nom}"
        return False, f"Echec paiement ({r3.status_code}): {r3.text[:300]}"

    except Exception as e:
        logger.error(f"Erreur achat : {e}")
        return False, f"Erreur : {e}"

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
    envoyer_telegram("🟢 Bot Vinted demarre — surveillance sans proxy, achat via proxy residentiel FR")
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
