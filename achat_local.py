"""
Script local qui tourne sur ton Mac et effectue les achats Vinted
avec ton IP personnelle. A lancer avant d'utiliser le bouton Acheter.
"""
from flask import Flask, request, jsonify
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================
# TES TOKENS VINTED — mets à jour si expirés
# ============================================

VINTED_TOKENS = {
    "refresh_token": "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhY2NvdW50X2lkIjozNzA2Mzc3OSwiYXBwX2lkIjo0LCJhdWQiOiJmci5jb3JlLmFwaSIsImNsaWVudF9pZCI6IndlYiIsImV4cCI6MTc3NDMwNjYwNywiaWF0IjoxNzczNzAxODA3LCJpc3MiOiJ2aW50ZWQtaWFtLXNlcnZpY2UiLCJsb2dpbl90eXBlIjozLCJwdXJwb3NlIjoicmVmcmVzaCIsInNjb3BlIjoidXNlciIsInNpZCI6IjM5NWMyNjNiLTE3NzE1OTY0MTAiLCJzdWIiOiI1NTM5MjQ4NiIsImNjIjoiRlIiLCJhbmlkIjoiYWIyM2VkZGMtMmJiNi00NGM2LWE1MjEtMmU2YzBmMzVhZTBiIiwiYWN0Ijp7InN1YiI6IjU1MzkyNDg2In19.HcmY3o4lqKNd1Uh4kwyyjOwfI2e0lcxYNRzFgimBN9HhtXmTDTRVuB9fdIurH2X1cXzQelbfeuoJspcN7yYkMiKrfnntBn-Ts3Ii2GsNBt58DCCklV96j0XiZv3szV7WUbEPs2TpCRkgaVBk0HyvFf4R5ld_PVc6FFzzFCQyR6N2vQSsR3jOldjJqyG8rbLnham6RHNYpqpEeqlw1kozoC2YeqYsC5-K4lteT3YIqcFmL_rS6dPK0AGLcqnrIvwpRpZ0M4vxTwK9Hhq1iW0T3jR-Pm62D5BevsbDz0b6wuYLGXYTX0eK4IG1ZnsL3ao8ccXzk_v0u3WOPsiNGU-79Q",
    "access_token": "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhY2NvdW50X2lkIjozNzA2Mzc3OSwiYXBwX2lkIjo0LCJhdWQiOiJmci5jb3JlLmFwaSIsImNsaWVudF9pZCI6IndlYiIsImV4cCI6MTc3MzcwOTAwNywiaWF0IjoxNzczNzAxODA3LCJpc3MiOiJ2aW50ZWQtaWFtLXNlcnZpY2UiLCJsb2dpbl90eXBlIjozLCJwdXJwb3NlIjoiYWNjZXNzIiwic2NvcGUiOiJ1c2VyIiwic2lkIjoiMzk1YzI2M2ItMTc3MTU5NjQxMCIsInN1YiI6IjU1MzkyNDg2IiwiY2MiOiJGUiIsImFuaWQiOiJhYjIzZWRkYy0yYmI2LTQ0YzYtYTUyMS0yZTZjMGYzNWFlMGIiLCJhY3QiOnsic3ViIjoiNTUzOTI0ODYifX0.tKAHT_SHsH6i9oTayeu1fXBPcVLZgxYE4MfzB61UHLXGuJFa3QalIt2d0CmXx-TnYB49Bz6sX6npEIEHiHLQtK-MSfFkVPH5pFj4vzbkf53tjgGsgFI3zY2DP6nteGNhZ8BojLzdzWiSo-UGJYiR5sGJO6iLuV1Lv1m8jrg8AjmyuZy3e8OhzKrSRkhFjbLK14y9ujv4M977xqjcbu_uIjEU6vZ4Dw-2HO5JQ7IpjRydZgi5wySXC-KEziZaY6Zik6NnOmGWNNfr_RpobaF53XumlxruiAuo3XBmXZWlHfBFwpXP-BximMfe9H25DMq-EEd6HQm59twzG7N5S70SKA",
    "session": "bzJra3QrcWFxbzMxRThzRmlJLzJhK3lmUVN1L3IxWWNWcjFNS0Nua0RQR05nREVOa2xnNGJNdUZ2YVpaU2JyRXptT3lVMUp5ck5qVHc0Mk55YXhYTTZEV2lNMkJRSkhtZ2NPNXFwL0I1TmNLQzhCZDc3YnlGNURNT0duemF4ZmwwNlk5S1dzaWFLYWZDdXhHa3hJdndVM2kzQyt5UXE0VHJ6alVEVm83ZFZZUERFVUF6RnBsZkQrQzJTZEdTbWZIZWhPanVXTy9UUlZkT0U1S09pTUZTOGlId3p1dVdDUjM3Y3BWRml1allna1FVMW5mZmJicjM2MVZsNkpQb1FmNk1VS0VTeTNyU0RidTRtK1pVOVB3ZGtLbDZFMHBsbmRSRnI0NStwc2Q0K050SGkzS2pzV1dUYlVJanFoN0lWcXotLVUxMWRWb0JHd3NTUzBRY2ZkWWNWNWc5PQ%3D%3D--34ee1cf1a40849e0b6030d755c1a5e7c3b611bad",
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

CHROME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Origin': 'https://www.vinted.fr',
    'Referer': 'https://www.vinted.fr/',
}

def renouveler_access_token():
    try:
        response = requests.post(
            "https://www.vinted.fr/api/v2/tokens",
            json={"grant_type": "refresh_token", "refresh_token": VINTED_TOKENS["refresh_token"], "client_id": "web"},
            headers=CHROME_HEADERS, timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("access_token"):
                VINTED_TOKENS["access_token"] = data["access_token"]
            if data.get("refresh_token"):
                VINTED_TOKENS["refresh_token"] = data["refresh_token"]
            logger.info("Tokens renouvelés")
            return True
        return False
    except Exception as e:
        logger.error(f"Erreur renouvellement token : {e}")
        return False

def creer_session():
    session = requests.Session()
    session.headers.update(CHROME_HEADERS)
    session.headers.update({"Authorization": f"Bearer {VINTED_TOKENS['access_token']}"})
    session.cookies.set("access_token_web", VINTED_TOKENS["access_token"], domain=".vinted.fr")
    session.cookies.set("refresh_token_web", VINTED_TOKENS["refresh_token"], domain=".vinted.fr")
    session.cookies.set("_vinted_fr_session", VINTED_TOKENS["session"], domain=".vinted.fr")
    session.cookies.set("cf_clearance", VINTED_TOKENS["cf_clearance"], domain=".vinted.fr")
    session.cookies.set("datadome", VINTED_TOKENS["datadome"], domain=".vinted.fr")
    return session

def choisir_point_relais(options):
    rate_uuids = {opt.get("rate_uuid") for opt in options}
    for point in POINTS_RELAIS:
        if point["rate_uuid"] in rate_uuids:
            return point
    return None

def acheter(item_id, tentative=1):
    session = creer_session()
    try:
        logger.info(f"Étape 1 : checkout item {item_id}")
        r = session.post(
            f"https://www.vinted.fr/api/v2/purchases/{item_id}/checkout",
            json={"components": {"item_presentation_escrow_v2": {}, "additional_service": {}, "payment_method": {}, "shipping_address": {}, "shipping_pickup_options": {}, "shipping_pickup_details": {}}},
            timeout=20
        )
        logger.info(f"Étape 1 status: {r.status_code}")
        if r.status_code == 401 and tentative == 1:
            if renouveler_access_token():
                return acheter(item_id, tentative=2)
            return False, "Token expiré"
        if r.status_code not in [200, 201]:
            return False, f"Échec étape 1 ({r.status_code}): {r.text[:200]}"
        checkout = r.json().get("checkout", {})
        purchase_id = checkout.get("id")
        if not purchase_id:
            return False, "Purchase ID introuvable"
    except Exception as e:
        return False, f"Erreur étape 1: {e}"

    try:
        pickup_types = checkout.get("components", {}).get("shipping_pickup_details", {}).get("pickup_types", {})
        pickup_options = pickup_types.get("pickup", {}).get("shipping_options", [])
        if not pickup_options:
            pickup_option = checkout.get("components", {}).get("shipping_pickup_options", {})
            selected_rate_uuid = pickup_option.get("pickup_options", {}).get("pickup", {}).get("selected_rate_uuid")
            point_uuid = pickup_option.get("pickup_options", {}).get("pickup", {}).get("shipping_point", {}).get("uuid")
            point_nom = "défaut"
        else:
            point = choisir_point_relais(pickup_options)
            if point:
                selected_rate_uuid = point["rate_uuid"]
                point_uuid = point["uuid"]
                point_nom = point["nom"]
            else:
                selected_rate_uuid = pickup_options[0].get("rate_uuid")
                point_uuid = None
                point_nom = "premier disponible"

        r2 = session.patch(
            f"https://www.vinted.fr/api/v2/purchases/{purchase_id}/checkout",
            json={"components": {"shipping_pickup_options": {"pickup_type": 2}, "shipping_pickup_details": {"selected_rate_uuid": selected_rate_uuid, "shipping_point_uuid": point_uuid}}},
            timeout=20
        )
        logger.info(f"Étape 2 status: {r2.status_code}")
        if r2.status_code not in [200, 201]:
            return False, f"Échec étape 2 ({r2.status_code}): {r2.text[:200]}"
        checksum = r2.json().get("checkout", {}).get("checksum")
        if not checksum:
            return False, "Checksum introuvable"
    except Exception as e:
        return False, f"Erreur étape 2: {e}"

    try:
        r3 = session.post(
            f"https://www.vinted.fr/api/v2/purchases/{purchase_id}/payment",
            json={"checksum": checksum, "payment_options": {"browser_info": {"language": "fr-FR", "color_depth": 32, "java_enabled": False, "screen_height": 956, "screen_width": 1470, "timezone_offset": -60}}},
            timeout=20
        )
        logger.info(f"Étape 3 status: {r3.status_code}")
        if r3.status_code in [200, 201]:
            return True, f"Acheté via {point_nom}"
        return False, f"Échec paiement ({r3.status_code}): {r3.text[:200]}"
    except Exception as e:
        return False, f"Erreur étape 3: {e}"

@app.route('/acheter/<item_id>', methods=['POST'])
def route_acheter(item_id):
    logger.info(f"Demande achat reçue pour item {item_id}")
    succes, message = acheter(item_id)
    return jsonify({"succes": succes, "message": message})

@app.route('/ping')
def ping():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    logger.info("🟢 Serveur d'achat local démarré sur port 4444")
    app.run(host='0.0.0.0', port=4444)
