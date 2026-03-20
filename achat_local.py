"""
Script local qui tourne sur ton Mac.
- Port 4444 : recoit les demandes de Railway via ngrok
- Port 4445 : communique avec l extension Chrome (poll + result)
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import threading
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

demandes = {}
lock = threading.Lock()

# App principale port 4444 (Railway -> ngrok -> ici)
app = Flask(__name__)

@app.route('/acheter/<item_id>', methods=['POST'])
def route_acheter(item_id):
    logger.info(f"Demande achat recue pour item {item_id}")
    with lock:
        demandes[item_id] = {"status": "pending", "result": None}

    for _ in range(30):
        time.sleep(1)
        with lock:
            d = demandes.get(item_id, {})
            if d.get("status") == "done":
                result = d["result"]
                del demandes[item_id]
                logger.info(f"Resultat item {item_id}: {result}")
                return jsonify(result)

    with lock:
        demandes.pop(item_id, None)
    logger.warning(f"Timeout item {item_id}")
    return jsonify({"succes": False, "message": "Timeout - Chrome pas ouvert ou extension non installee"})

@app.route('/ping')
def ping():
    return jsonify({"status": "ok"})

# App extension port 4445 (extension Chrome -> ici)
app2 = Flask(__name__ + "_ext")
CORS(app2)

@app2.route('/poll', methods=['GET'])
def poll():
    with lock:
        for item_id, d in demandes.items():
            if d["status"] == "pending":
                return jsonify({"item_id": item_id})
    return jsonify({}), 204

@app2.route('/result', methods=['POST'])
def result():
    data = request.get_json()
    item_id = str(data.get("item_id"))
    logger.info(f"Resultat extension pour item {item_id}: {data}")
    with lock:
        if item_id in demandes:
            demandes[item_id] = {
                "status": "done",
                "result": {"succes": data.get("succes"), "message": data.get("message")}
            }
    return jsonify({"ok": True})

if __name__ == '__main__':
    logger.info("Serveur Railway demarre sur port 4444")
    logger.info("Serveur extension Chrome demarre sur port 4445")

    t = threading.Thread(
        target=lambda: app2.run(host='0.0.0.0', port=4445, use_reloader=False)
    )
    t.daemon = True
    t.start()

    app.run(host='0.0.0.0', port=4444, use_reloader=False)
