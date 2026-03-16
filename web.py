from flask import Flask, render_template, jsonify, request
import psycopg2
import psycopg2.extras
import os
import requests

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

ALERTES = [
    {"nom": "Rick Owens", "brand_id": 145654},
    {"nom": "Ann Demeulemeester", "brand_id": 51445},
    {"nom": "Isaac Sellam", "brand_id": 393343},
    {"nom": "Mon profil", "user_id": 0},
]

CHROME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Origin': 'https://www.vinted.fr',
    'Referer': 'https://www.vinted.fr/',
}

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def get_articles(alerte=None, search=None, limit=200):
    try:
        conn = get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if alerte and search:
            c.execute(
                'SELECT DISTINCT ON (vinted_id) * FROM articles_vus WHERE nom_alerte=%s AND LOWER(titre) LIKE %s ORDER BY vinted_id, trouve_le DESC LIMIT %s',
                (alerte, f'%{search.lower()}%', limit)
            )
        elif alerte:
            c.execute(
                'SELECT * FROM articles_vus WHERE nom_alerte=%s ORDER BY trouve_le DESC LIMIT %s',
                (alerte, limit)
            )
        elif search:
            c.execute(
                'SELECT DISTINCT ON (vinted_id) * FROM articles_vus WHERE LOWER(titre) LIKE %s ORDER BY vinted_id, trouve_le DESC LIMIT %s',
                (f'%{search.lower()}%', limit)
            )
        else:
            c.execute(
                'SELECT DISTINCT ON (vinted_id) vinted_id, nom_alerte, titre, prix, photo_url, trouve_le FROM articles_vus ORDER BY vinted_id, trouve_le DESC LIMIT %s',
                (limit,)
            )
        rows = c.fetchall()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            if d.get('trouve_le'):
                d['trouve_le'] = d['trouve_le'].isoformat()
            result.append(d)
        result.sort(key=lambda x: x.get('trouve_le', ''), reverse=True)
        return result
    except Exception as e:
        print(f"Erreur get_articles: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html', alertes=ALERTES)

@app.route('/api/articles')
def api_articles():
    alerte = request.args.get('alerte')
    search = request.args.get('search')
    articles = get_articles(alerte, search)
    return jsonify(articles)

@app.route('/api/item/<item_id>')
def api_item(item_id):
    """Récupère les détails complets d'un article depuis Vinted"""
    try:
        session = requests.Session()
        session.headers.update(CHROME_HEADERS)
        session.get('https://www.vinted.fr', timeout=10)
        response = session.get(
            f"https://www.vinted.fr/api/v2/items/{item_id}",
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            item = data.get("item", {})
            photos = [p.get("url", "") for p in item.get("photos", []) if p.get("url")]
            
            # Calcul du temps depuis la publication
            created_at = item.get("created_at_ts", 0)
            import time
            now = time.time()
            diff = int(now - created_at)
            if diff < 3600:
                temps = f"il y a {diff // 60} min"
            elif diff < 86400:
                temps = f"il y a {diff // 3600}h"
            else:
                temps = f"il y a {diff // 86400}j"

            return jsonify({
                "succes": True,
                "id": item_id,
                "titre": item.get("title", ""),
                "prix": str(item.get("price", "")),
                "description": item.get("description", ""),
                "etat": item.get("status", ""),
                "taille": item.get("size_title", ""),
                "marque": item.get("brand_title", ""),
                "temps": temps,
                "photos": photos,
                "lien": f"https://www.vinted.fr/items/{item_id}"
            })
        else:
            return jsonify({"succes": False, "message": f"Status {response.status_code}"})
    except Exception as e:
        return jsonify({"succes": False, "message": str(e)})

@app.route('/api/acheter/<item_id>', methods=['POST'])
def api_acheter(item_id):
    try:
        from app import acheter_article
        succes, message = acheter_article(item_id)
        return jsonify({"succes": succes, "message": message})
    except Exception as e:
        return jsonify({"succes": False, "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
